import pygame
pygame.font.init()
pygame.mixer.init()


class Assets:
    button_pressed = pygame.transform.scale(pygame.image.load('assets/button_pressed.png'), (100, 100))
    button_unpressed = pygame.transform.scale(pygame.image.load('assets/button_unpressed.png'), (100, 100))
    font = pygame.font.SysFont('Sans', 32)
    big_font = pygame.font.SysFont('Sans', 42)
    beep_sound = pygame.mixer.Sound("assets/beep.wav")
    bg = pygame.image.load('assets/bg.png')
    dir_l = pygame.image.load('assets/l.png')
    dir_r = pygame.image.load('assets/r.png')
    dir_d = pygame.image.load('assets/d.png')
    dir_ld = pygame.image.load('assets/ld.png')
    dir_rd = pygame.image.load('assets/rd.png')
