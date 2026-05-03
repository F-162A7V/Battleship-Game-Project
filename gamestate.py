__author__ = "F-162A7V"

import pygame
from battleshiplayer import Player

#class Gamestate(p1,p2,s1,s2):

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game Window")
bg_img = pygame.image.load("assets/water2.jpg").convert()
hood_img = pygame.image.load("assets/hoodplayer_2.png").convert_alpha()
bismarck_img = pygame.image.load("assets/bismarckplayer_2.png").convert_alpha()
player2_rect = bismarck_img.get_rect(center=(400, 300))
P1_obj = Player(400, 500, 0, 0, 0)
P2_obj = Player(600, 300, 0, 0, 1)


def check_inpts(pressed_keys,plr):
    if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
        plr.turn(1, 1)
    if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
        plr.turn(-1, 1)
    if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
        plr.change_velocity(1, 0.05)
    if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
        plr.change_velocity(-1, 0.05)

def upd_screen(screen,hood,bis):
    screen.blit(hood, player1_rect)
    screen.blit(bis, player2_rect)
    pygame.display.flip(),

running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pressed = pygame.key.get_pressed()
    check_inpts(pressed, P1_obj)
    P1_obj.change_coords()
    screen.blit(bg_img,(0,0))
    new_hood = pygame.transform.rotate(hood_img, P1_obj.angle)
    player1_rect = new_hood.get_rect(center=(P1_obj.x, P1_obj.y))
    upd_screen(screen,new_hood,bismarck_img)
    clock.tick(10)
pygame.quit()






























