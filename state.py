import enum
import pygame

from aboutbutton import AboutButton
from destination_button import DestinationButton
from choose_floors_button import ChooseFloorsButton
from handicapbutton import HandicapButton
from keypadbutton import KeypadButton

class StateType(enum.Enum):
    AcceptingNewInput = 1
    AppendingInput = 2
    DirectingToFloor = 3
    ShowingError = 4
    ShowingAboutScreen = 5
    ShowingDestinationButtonsScreen = 6


class ErrorType(enum.Enum):
    FloorNotAvailable = 1
    EntryNotUnderstood = 2
    CannotAllocateCarAtThisTime = 3
    Floor0Error = 4
    Floor13Error = 5


class ElevatorArrival:
    def __init__(self):
        self.arrives_at = 0
        self.car = ""
        self.sound_play_context = {}


def init_handicap_button():
    ret = pygame.sprite.Group()
    ret.add(HandicapButton(650, 100))
    return ret


def init_about_button():
    ret = pygame.sprite.Group()
    ret.add(AboutButton(930, 510))
    return ret


def init_choose_floors_button():
    ret = pygame.sprite.Group()
    ret.add(ChooseFloorsButton(650, 510, 240, 60, "Choose Floors"))
    return ret


def init_more_floors_button():
    ret = pygame.sprite.Group()
    ret.add(ChooseFloorsButton(630, 410, 60, 60, ">"))
    return ret


def init_back_to_keypad_button():
    ret = pygame.sprite.Group()
    ret.add(ChooseFloorsButton(680, 510, 190, 60, "Keypad"))
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
        self.choose_floors_button_group = init_choose_floors_button()
        self.more_floors_button_group = init_more_floors_button()
        self.back_to_keypad_button_group = init_back_to_keypad_button()
        self.active_destination_buttons_group_idx = 0

        self.destination_button_groups = init_destination_buttons()
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
        self.showing_about_start_time = 0


class Direction(enum.Enum):
    Left = 0
    Right = 1
    Back = 2
    BackLeft = 3
    BackRight = 4


all_button_ids = [x for x in range(-40, 41, 1) if x != -13 and x != 13 and x != 0]


def translate_button_id(sequential_id):
    return all_button_ids[sequential_id]


def init_destination_buttons():
    group1 = pygame.sprite.Group()
    group2 = pygame.sprite.Group()
    x_origin = 50
    y_origin = 50
    x_space = 90
    y_space = 55

    columns = 6
    rows = 9
    for y in range(0, rows):
        for x in range(0, columns):
            button_id = (columns * y) + x
            if button_id > 77:
                continue

            group1.add(DestinationButton(str(translate_button_id(button_id)), x_origin + (x_space * x),
                                      y_origin + (y_space * y)))

    for y in range(0, rows):
        for x in range(0, columns):
            button_id = (columns * y) + x
            button_id += rows * columns
            if button_id > 77:
                continue

            group2.add(DestinationButton(str(translate_button_id(button_id)), x_origin + (x_space * x),
                                      y_origin + (y_space * y)))


    return [group1, group2]


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

    x_idx = 0
    y_idx = 3
    ret.add(KeypadButton("-", x_origin + x_space * x_idx, y_origin + y_space * y_idx))

    return ret
