import pygame
from pygame.rect import Rect

from assets import Assets
from choose_floors_button import make_filled_rounded_rect


class DestinationButton(pygame.sprite.Sprite):
    def __init__(self, button_id, x, y, width=80, height=40):
        pygame.sprite.Sprite.__init__(self)
        self.button_id = button_id
        self.pressed_image = make_filled_rounded_rect(Rect(0, 0, width, height), (150, 150, 150), .4)
        self.unpressed_image = make_filled_rounded_rect(Rect(0, 0, width, height), (240, 240, 240), .4)
        self.image = self.unpressed_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pressed = False
        self.was_depressed = False

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
            Assets.beep_sound.play()
