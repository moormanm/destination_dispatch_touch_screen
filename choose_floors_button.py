import pygame
from pygame import draw, transform
from pygame.color import Color
from pygame.constants import BLEND_RGBA_MIN, BLEND_RGBA_MAX, SRCALPHA
from pygame.rect import Rect
from pygame.surface import Surface

from assets import Assets


def make_filled_rounded_rect(rect, color, radius=0.4):
    rect = Rect(rect)
    color = Color(*color)
    alpha = color.a
    color.a = 0
    rect.topleft = 0, 0
    rectangle = Surface(rect.size, SRCALPHA)

    circle = Surface([min(rect.size) * 3] * 2, SRCALPHA)
    draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)

    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)
    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))
    rectangle.fill(color, special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=BLEND_RGBA_MIN)

    return rectangle


def render_image(label, iw, ih, is_pressed):
    if is_pressed:
        fill_color = (100, 100, 100)
    else:
        fill_color = (245, 245, 245)

    ret = make_filled_rounded_rect(Rect(0, 0, iw, ih), fill_color, .4)
    text = Assets.font.render(label, True, (0, 0, 0))
    w = text.get_width()
    h = text.get_height()
    ret.blit(text,
             [
                 ret.get_rect().width / 2 - w / 2,
                 ret.get_rect().height / 2 - h / 2
             ]
             )

    return ret


class ChooseFloorsButton(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, label):
        pygame.sprite.Sprite.__init__(self)
        self.pressed = False
        self.label = label
        self.image = render_image(self.label, w, h, self.pressed)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

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
        self.image = render_image(self.label, self.rect.width, self.rect.height, self.pressed)
        if self.was_depressed:
            Assets.beep_sound.play()
