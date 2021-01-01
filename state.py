import enum
import pygame

pygame.font.init()
pygame.mixer.init()


class StateType(enum.Enum):
    AcceptingNewInput = 1
    AppendingInput = 2
    DirectingToFloor = 3
    ShowingError = 4


class ErrorType(enum.Enum):
    FloorNotAvailable = 1
    EntryNotUnderstood = 2
    CannotAllocateCarAtThisTime = 3


class State:
    def __init__(self):
        self.run = True
        self.state_type = StateType.AcceptingNewInput
        self.floor_selection_buffer = ""
        self.error_type = None
        self.keypad_sprites = init_keypad_sprites()
        self.events = []
        self.appending_input_start_millis = 0
        self.directing_to_floor_start_millis = 0
        self.showing_error_start_millis = 0


def init_keypad_sprites():
    ret = pygame.sprite.Group()

    x_origin = 50
    y_origin = 200
    x_space = 130
    y_space = 130
    x_idx = 0
    y_idx = 0

    ret.add(KeypadButton("1", x_origin + x_space * x_idx, y_origin + y_space * y_idx))

    x_idx = x_idx + 1
    ret.add(KeypadButton("2", x_origin + x_space * x_idx, y_origin + y_space * y_idx))

    x_idx = x_idx + 1
    ret.add(KeypadButton("3", x_origin + x_space * x_idx, y_origin + y_space * y_idx))

    x_idx = 0
    y_idx = 1
    ret.add(KeypadButton("4", x_origin + x_space * x_idx, y_origin + y_space * y_idx))

    x_idx = x_idx + 1
    ret.add(KeypadButton("5", x_origin + x_space * x_idx, y_origin + y_space * y_idx))

    x_idx = x_idx + 1
    ret.add(KeypadButton("6", x_origin + x_space * x_idx, y_origin + y_space * y_idx))

    x_idx = 0
    y_idx = 2
    ret.add(KeypadButton("7", x_origin + x_space * x_idx, y_origin + y_space * y_idx))

    x_idx = x_idx + 1
    ret.add(KeypadButton("8", x_origin + x_space * x_idx, y_origin + y_space * y_idx))

    x_idx = x_idx + 1
    ret.add(KeypadButton("9", x_origin + x_space * x_idx, y_origin + y_space * y_idx))

    x_idx = 1
    y_idx = 3
    ret.add(KeypadButton("0", x_origin + x_space * x_idx, y_origin + y_space * y_idx))

    return ret


class Assets:
    button_pressed = pygame.transform.scale(pygame.image.load('assets/button_pressed.png'), (100, 100))
    button_unpressed = pygame.transform.scale(pygame.image.load('assets/button_unpressed.png'), (100, 100))
    font = pygame.font.SysFont('Sans', 32)
    beep_sound = pygame.mixer.Sound("assets/beep.wav")


class KeypadButton(pygame.sprite.Sprite):
    def __init__(self, button_id, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.button_id = button_id
        self.pressed_image = Assets.button_pressed.convert().copy()
        self.unpressed_image = Assets.button_unpressed.convert().copy()
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

    def update(self):
        if self.pressed:
            self.image = self.pressed_image
        else:
            self.image = self.unpressed_image
        if self.was_depressed:
            Assets.beep_sound.play()
