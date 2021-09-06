import pygame

from assets import Assets


class PressableButton(pygame.sprite.Sprite):
    def __init__(self, x, y, pressed_img=Assets.about_button_pressed, unpressed_img=Assets.about_button_unpressed):
        pygame.sprite.Sprite.__init__(self)
        self.pressed_image = pressed_img.convert_alpha().copy()
        self.unpressed_image = unpressed_img.convert_alpha().copy()
        self.image = self.unpressed_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pressed = False
        self.was_depressed = False
        self.beep_sound = Assets.beep_sound

    def handle_event(self, event):
        self.was_depressed = False

        if event.type == pygame.MOUSEBUTTONDOWN and not self.pressed:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and self.pressed:
            if event.button == 1:
                self.pressed = False
                if self.rect.collidepoint(event.pos):
                    self.was_depressed = True

    def update(self, state):
        if self.pressed:
            self.image = self.pressed_image
        else:
            self.image = self.unpressed_image
