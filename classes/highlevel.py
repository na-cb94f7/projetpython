import pygame
from classes.sprites import *

#* Notes sur les structures de données utilisées
# Pour mieux comprendre ce code, apprendre les structures suivantes :
# - pygame.sprite.Sprite() ; https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite
# - pygame.sprite.Group() ; https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group
# - pygame.USERVENT ; https://coderslegacy.com/python/pygame-userevents/

#* Définition de fonctions auxiliaires

def draw_background(game):
    """
    Prépare et dessine un arrière-plan, transformé afin de rentrer dans les contraintes de la taille définie de l'écran
    """
    scaled_background = pygame.transform.scale(game.BG_IMAGE, (game.SCREEN_WIDTH, game.SCREEN_HEIGHT))
    game.screen.blit(scaled_background, (0,0))

def draw_introimage(game):
    """
    Prépare et dessine un arrière-plan, transformé afin de rentrer dans les contraintes de la taille définie de l'écran
    """
    scaled_intro = pygame.transform.scale(game.INTRO_SCREEN, (game.SCREEN_WIDTH, game.SCREEN_HEIGHT))
    game.screen.blit(scaled_intro, (0,0))
    text = game.FONT.render('CLIQUEZ POUR JOUER !', True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.center = (game.SCREEN_WIDTH // 2, game.SCREEN_HEIGHT - 50)
    game.screen.blit(text, text_rect)

def draw_losescreen(game):
    """
    Prépare et dessine un écran game-over, transformé afin de rentrer dans les contraintes de la taille définie de l'écran
    """
    scaled_losescreen = pygame.transform.scale(game.LOSE_SCREEN, (game.SCREEN_WIDTH, game.SCREEN_HEIGHT))
    game.screen.blit(scaled_losescreen, (0,0))

def draw_score(game):
    """
    Prépare et dessine le score mis à jour en temps réel.
    """
    text = game.FONT.render(f"SCORE : {game.score}", True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.center = (125, game.SCREEN_HEIGHT - 50)
    game.screen.blit(text, text_rect)

def draw_health(game):
    """
    Prépare et dessine les points de vie du joueur en temps réel.
    """
    text = game.FONT.render(f"PV : {game.player.health}", True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.center = (125, game.SCREEN_HEIGHT - 100)
    game.screen.blit(text, text_rect)

#* Définition de la classe Game, qui tiendra toutes les variables en mémoire

class Game():
    """
    Classe à haut niveau d'abstraction, permettant une meilleure opérabilité entre les différents éléments du jeu
    """
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, player, enemies, powerups):
        # Dimensions, écran Pygame et FPS
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.FPS = FPS
        # Ressources et médias
        self.FONT = pygame.font.Font('./data/font/PixeloidSansBold.ttf', 32)
        self.BG_IMAGE = pygame.image.load("data/images/background.png")
        self.LOSE_SCREEN = pygame.image.load("data/images/lose_screen.jpg")
        self.INTRO_SCREEN = pygame.image.load("data/images/intro_screen.png")
        # Sprites
        self.player = player
        self.enemies = enemies
        self.powerups = powerups
        # Elements propres au jeu
        self.current_state = "intro" # Etat initial qui va changer
        self.score = 0
        self.ENEMYSPAWN = pygame.USEREVENT + 0
        self.POWERUPSPAWN = pygame.USEREVENT + 1
        self.is_running = True
        self.runtime = pygame.time.get_ticks()

        # Préparation de la fenêtre et des timers évènements
        pygame.display.set_caption("David Zorp")
        pygame.time.set_timer(self.ENEMYSPAWN, 5 * 1000) # Timer initial pour l'event ENEMYSPAWN, qui changera au fil du temps
        pygame.time.set_timer(self.POWERUPSPAWN, 8 * 1000)

    def update(self):
        """Va mettre à jour la logique de jeu en fonction de l'état actuel du jeu.
        Toutes les fonctions liées aux états de jeu spécifiques sont définies ici."""

        def intro_update(self):
            """Permet la gestion des évènements lors de la phase d'introduction."""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.screen.fill((0, 0, 0))
                    self.current_state = "gameplay"

        def gameplay_update(self):
            """Permet la gestion des évènements et l'interaction avec le joueur en temps réel lors de la phase de gameplay."""

            # Affichages préliminaux avant la mise à jour de l'état du jeu
            draw_background(self)
            draw_health(self)
            draw_score(self)

            # Gestion des évènements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                elif event.type == self.ENEMYSPAWN:
                    self.enemies.add(Enemy())
                    # En fonction du temps passé, les ennemis apparaissent de plus en plus rapidement
                    if self.runtime < 10 * 1000:
                        pygame.time.set_timer(self.ENEMYSPAWN, 2 * 1000)
                    elif 10 * 1000 < self.runtime < 20 * 1000:
                        pygame.time.set_timer(self.ENEMYSPAWN, 1 * 1000)
                    else : # 20 * 1000 < self.runtime
                        pygame.time.set_timer(self.ENEMYSPAWN, int(0.5 * 1000))

                # On ajoute un powerup toutes les 8s
                elif event.type == self.POWERUPSPAWN:
                    self.powerups.add(Powerup())

            # Les sprites sont mis à jour
            self.player.update(self.enemies, self.increment_score)
            self.enemies.update(self.player)
            self.powerups.update(self.player, self.enemies, self.increment_score)

            # Gestion de la condition de perte
            if self.player.health <= 0:
                self.current_state = "lose"
                self.player.health = 4 # Sans cette ligne, on tourne en boucle entre "intro" et "lose" lors de la prochaine session

        def lose_update(self):
            """Permet la gestion des évènements lors de la phase de perte."""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if pygame.type == pygame.MOUSEBUTTONDOWN:
                    self.screen.fill((0, 0, 0))
                    self.current_state = "intro"

        # En fonction de l'état de jeu, appliquer une logique différente au jeu
        # match / case ... permet une écriture plus propre que if / elif / elif ...
        match self.current_state:
            case "intro":
                intro_update(self)
            case "gameplay":
                gameplay_update(self)
            case "lose":
                lose_update(self)

    def draw(self):
        """Va mettre à jour l'affichage du jeu en fonction de l'état actuel du jeu.
        Toutes les fonctions liées aux états de jeu spécifiques sont définies ici."""

        def intro_draw(self):
            """Dessinera l'image d'introduction à l'écran."""
            draw_introimage(self)

        def gameplay_draw(self):
            """Dessinera les différents sprites sur l'écran lors du gameplay."""
            self.player.draw(self.screen)
            self.enemies.draw(self.screen)
            self.powerups.draw(self.screen)

        def lose_draw(self):
            """Dessinera l'écran de perte à l'écran."""
            draw_losescreen(self)

        match self.current_state:
            case "intro":
                intro_draw(self)
            case "gameplay":
                gameplay_draw(self)
            case "lose":
                lose_draw(self)

    def increment_score(self, n=1):
        """Fonction permettant d'incrémenter le score, lorsque le joueur détruit un astéroide ou que le joueur obtienne un power-up de score."""
        self.score += n
