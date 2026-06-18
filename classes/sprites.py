import pygame
import os
import math
import random
from physicsengine.physics import update_physics
from physicsengine.constants import *

#* Définition de fonctions auxiliaires

def enemy_spawn(screen_width: int, screen_height: int) -> tuple[int, int]:
    """
    Cette fonction déterminera les mécaniques de spawn des ennemis.
    Ils apparaissent SOIT à x = -100 ou s_width + 100 et y = randint(100, s_height - 100) OU...
    à x = randint(100, s_width - 100) et y = -100.
    La fonction force un padding de 100 pixels.
    La fonction renvoie un tuple représentant un point dans le système de coordonnées de pygame.
    """
    padding = 100
    if random.randint(0, 1):
        return random.choice([-padding, screen_width + padding]), random.randint(padding, screen_height // 2 - padding)
    else:
        return random.randint(padding, screen_width - padding), -padding

def powerup_spawn(screen_width: int, screen_height: int) -> tuple[int, int]:
    """
    Cette fonction déterminera les mécaniques de spawn des powerups.
    Ils apparaissent dans un rectangle dont l'origine dans les coordonnées pygame est (padding, padding) et dont la taille est de screen_width - 2*padding et screen_height - 2*padding respectivement.
    La fonction force un padding de 100 pixels.
    La fonction renvoie un tuple représentant un point dans le système de coordonnées de pygame.
    """
    padding = 100
    return random.randint(padding, padding + screen_width - 2*padding), \
        random.randint(padding, padding + screen_height - 2*padding)

#* Classes

class Player(pygame.sprite.Sprite):
    """
    La classe correspondant à l'entité du joueur, qui permet d'interagir avec le jeu
    """
    def __init__(self):
        super().__init__()
        # Images du joueur
        self.image = pygame.image.load('/home/arni/Downloads/projetpython/data/images/idle.png')
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.image = pygame.transform.rotate(self.image, -90) # Pour faire correspondre l'image à la fonction rotate du joueur
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300) # Point de départ du joueur
        self.health = 4
        # Ajouts pour s'ajuster au moteur de physiques
        self.vx, self.vy = 0, 0
        self.angle_control = -math.pi / 2
        self.dt = pygame.time.Clock().tick(60) / 1000 # pour le moteur de physiques
        self.attack_length = 0.5 * 1000 # Pour forcer 0.5s d'attaque
        self.attack_start = -self.attack_length # Sera modifiée lors d'une attaque. Egale a cela au negatif a cause de la condition plus tard

    def update(self, enemies, increment_score):
        """
        Permet au joueur de se déplacer et de contrôler le personnage jouable
        """
        # On obtient la liste des touches utilisées
        runtime = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle_control -= TURN_SPEED * self.dt
        if keys[pygame.K_RIGHT]:
            self.angle_control += TURN_SPEED * self.dt
        if keys[pygame.K_UP]:
            self.rect.x, self.rect.y, \
                self.vx, self.vy = update_physics(self.rect.x, self.rect.y,
                                                        self.vx, self.vy, self.angle_control, True, self.dt)[:4]
        if keys[pygame.K_r]:
            self.attack_start = pygame.time.get_ticks()

        # Attaque pour détruire les météorites
        # Forcer au moins 0.5s d'attaque'
        if runtime < self.attack_start + self.attack_length:
            self.rect.x, self.rect.y, \
                self.vx, self.vy = update_physics(self.rect.x, self.rect.y,
                                                        1.1 * self.vx, 1.1 * self.vy, self.angle_control, True, self.dt)[:4]
            for enemy in pygame.sprite.spritecollide(self, enemies, dokill=True):
                increment_score()

        self.rotate()

    def rotate(self):
        """Permet de faire une rotatio sur l'image du joueur en conservant une position correcte."""
        self.image = pygame.transform.rotate(self.original_image, -math.degrees(self.angle_control))
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, screen):
      screen.blit(self.image, self.rect)

class Enemy(pygame.sprite.Sprite):
    """
    L'entité correspondant aux enemis qu'il faut affronter dans le jeu
    """
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join('data', 'images', 'asteroid.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (70, 70))
        self.rect = self.image.get_rect()
        self.rect.center = enemy_spawn(800, 600)
        self.speed = 3

    def update(self, player):
        """
        Cette fonction fait déplacer l'enemi vers la position du joueur.
        Pour se faire, elle utilise un vecteur décrivant la distance entre l'enemi et le joueur.
        """
        dx, dy = player.rect.x - self.rect.x, player.rect.y - self.rect.y
        dist = math.hypot(dx, dy) # Norme euclidienne du vecteur obtenu
        if pygame.sprite.collide_rect(self, player):
            player.health -= 1
            self.kill()
        dx, dy = dx / dist, dy / dist  # On normalize les vecteurs de déplacement
        # L'enemi se déplace selon le vecteur de déplacement calculé
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Powerup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join('data', 'images', 'star.png'))
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.center = powerup_spawn(800, 600) # Coordonnées aléatoires dans les dimensions de l'écran

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, player, enemies, score):
        """
        Faire en sorte que le power-up donne un bonus au joueur, quand ce dernier le touche.
        """
        if self.rect.colliderect(player.rect):
            self.give_powerup(player, enemies, score)
            self.kill() # Le powerup concerné s'enlève de son groupe de sprites et sera automatiquement enlevé

    def give_powerup(self, player, enemies, score):
        """
        Cette fonction recense tous les bonus qu'il soit possible de donner au joueur.
        """
        def health_powerup(player):
            player.health = 4

        def nuke_powerup(enemies):
            enemies.empty()

        def score_powerup(increment_score):
            increment_score(20)

        powerup_choices = [health_powerup, nuke_powerup, score_powerup]
        chosen_powerup = random.choice(powerup_choices)
        if chosen_powerup == health_powerup:
            health_powerup(player)
        elif chosen_powerup == nuke_powerup:
            nuke_powerup(enemies)
        else: # chosen_powerup == score_powerup
            score_powerup(score)

if __name__ == "__main__":
    game = Game(800, 600, 90, Player(),
            enemies=pygame.sprite.Group(), powerups=pygame.sprite.Group())
    test_powerup = Powerup()
    for _ in range(10):
        test_powerup.give_powerup(game.player, game.enemies, game.increment_score)
