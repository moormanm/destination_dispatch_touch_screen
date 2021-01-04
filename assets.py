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

    handicap_sounds = {
        '0': pygame.mixer.Sound('assets/0.wav'),
        '1': pygame.mixer.Sound('assets/1.wav'),
        '2': pygame.mixer.Sound('assets/2.wav'),
        '3': pygame.mixer.Sound('assets/3.wav'),
        '4': pygame.mixer.Sound('assets/4.wav'),
        '5': pygame.mixer.Sound('assets/5.wav'),
        '6': pygame.mixer.Sound('assets/6.wav'),
        '7': pygame.mixer.Sound('assets/7.wav'),
        '8': pygame.mixer.Sound('assets/8.wav'),
        '9': pygame.mixer.Sound('assets/9.wav')
    }

    @classmethod
    def handicap_sound_for_button(cls, button_id):
        return Assets.handicap_sounds.get(button_id)
