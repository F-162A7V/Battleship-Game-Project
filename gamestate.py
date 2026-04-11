__author__ = "F-162A7V"

import pygame

#class Player():

#class Gamestate(p1,p2,s1,s2):

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game Window")
bg_img = pygame.image.load("assets/water2.jpg").convert()
player = pygame.image.load("assets/hoodplayer_1.png").convert_alpha()
player_rect = player.get_rect(center=(400, 300))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(bg_img,(0,0))
    pygame.display.flip()
pygame.quit()