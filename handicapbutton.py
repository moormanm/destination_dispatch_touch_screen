import pygame

from assets import Assets


class HandicapButton(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.pressed_image = Assets.handicap_button_pressed.convert_alpha().copy()
        self.on_image = Assets.handicap_button_on.convert_alpha().copy()
        self.off_image = Assets.handicap_button_off.convert_alpha().copy()
        self.image = self.off_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pressed = False
        self.was_depressed = False
        self.enter_handicap_sound = Assets.beep_sound
        self.exit_handicap_sound = Assets.beep_sound

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
            pass
        else:
            self.image = self.on_image if state.in_handicap_mode else self.off_image
        if self.was_depressed:
            if state.in_handicap_mode:
                self.exit_handicap_sound.play()
                self.image = self.off_image
            else:
                self.enter_handicap_sound.play()
                self.image = self.on_image