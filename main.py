import pygame
from classes.highlevel import Game
from classes.sprites import Player, Enemy

# Fenêtre Pygame et classe Game initialisées
pygame.init()
game = Game(800, 600, 90, Player(),
            enemies=pygame.sprite.Group(), powerups=pygame.sprite.Group())

# L'état du jeu est gardé en mémoire par la classe Game
# Attention, la plupart du code se trouve dans Game() !
while game.is_running:
    # Horloge qui permet de régler les FPS du jeu
    clock = pygame.time.Clock()
    clock.tick(game.FPS)

    #* Mise à jour du jeu
    game.update()

    #* Affichages finaux du jeu
    game.draw()

    #* Mise à jour du display Pygame
    pygame.display.update()

    #* Eventuels debogages

pygame.quit()
