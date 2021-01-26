import pygame

from assets import Assets


class KeypadButton(pygame.sprite.Sprite):
    def __init__(self, button_id, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.button_id = button_id
        self.pressed_image = Assets.button_pressed.convert_alpha().copy()
        self.unpressed_image = Assets.button_unpressed.convert_alpha().copy()
        self.image = self.unpressed_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pressed = False
        self.was_depressed = False
        self.handicap_sound = Assets.handicap_sound_for_button(button_id)

        text = Assets.font.render(button_id, True, (0, 0, 0))
        w = text.get_width()
        h = text.get_height()
        self.unpressed_image.blit(text,
                                  [self.image.get_rect().width / 2 - w / 2, self.image.get_rect().height / 2 - h / 2])
        self.pressed_image.blit(text,
                                [self.image.get_rect().width / 2 - w / 2, self.image.get_rect().height / 2 - h / 2])

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
        if self.was_depressed:
            if state.in_handicap_mode and self.button_id != '-':
                self.handicap_sound.play()
            else:
                Assets.beep_sound.play()
