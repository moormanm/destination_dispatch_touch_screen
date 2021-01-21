import enum
import pygame

from aboutbutton import AboutButton
from handicapbutton import HandicapButton
from keypadbutton import KeypadButton


class StateType(enum.Enum):
    AcceptingNewInput = 1
    AppendingInput = 2
    DirectingToFloor = 3
    ShowingError = 4
    ShowingAboutScreen = 5


class ErrorType(enum.Enum):
    FloorNotAvailable = 1
    EntryNotUnderstood = 2
    CannotAllocateCarAtThisTime = 3


class ElevatorArrival:
    def __init__(self):
        self.arrives_at = 0
        self.car = ""
        self.sound_play_context = {}


def init_handicap_button():
    ret = pygame.sprite.Group()
    ret.add(HandicapButton(550, 100))
    return ret

def init_about_button():
    ret = pygame.sprite.Group()
    ret.add(AboutButton(940, 520))
    return ret

class State:
    def __init__(self):
        self.run = True
        self.state_type = StateType.AcceptingNewInput
        self.floor_selection_buffer = ""
        self.error_type = None
        self.keypad_sprites = init_keypad_sprites()
        self.handicap_button_group = init_handicap_button()
        self.about_button_group = init_about_button()
        self.events = []
        self.appending_input_start_millis = 0
        self.directing_to_floor_start_millis = 0
        self.showing_error_start_millis = 0
        self.directing_to_floor_context = {}
        self.showing_error_context = {}
        self.selected_car = ""
        self.selected_floor = ""
        self.direction_of_car = None
        self.in_handicap_mode = False
        self.elevator_arrivals = []
        self.in_about_mode = False


class Direction(enum.Enum):
    Left = 0
    Right = 1
    Back = 2
    BackLeft = 3
    BackRight = 4


def init_keypad_sprites():
    ret = pygame.sprite.Group()

    x_origin = 50
    y_origin = 50
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
