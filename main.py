import string
from datetime import date

import pygame
from state import State, StateType, ErrorType, Direction, ElevatorArrival
from assets import Assets
import time
from os import environ
import random


def update_from_about_screen(state):
    if millis() - state.showing_about_start_time > 8000:
        transition_to_accepting_new_input(state)


def update_from_accepting_new_input(state):
    update_handicap_button_state(state)
    if update_about_button_state(state):
        transition_to_showing_about_screen(state)
        return

    for event in state.events:
        for keypad_button in state.keypad_sprites:
            keypad_button.handle_event(event)
            keypad_button.update(state)
            if keypad_button.was_depressed:
                transition_to_appending_input(state, keypad_button.button_id)
                return


def millis():
    return int(round(time.time() * 1000))


def transition_to_appending_input(state, selected_key):
    state.state_type = StateType.AppendingInput
    state.floor_selection_buffer = selected_key
    state.appending_input_start_millis = millis()


def transition_to_showing_error(state, error_type):
    state.state_type = StateType.ShowingError
    state.showing_error_start_millis = millis()
    state.error_type = error_type
    state.showing_error_context = {}


def transition_to_showing_about_screen(state):
    state.state_type = StateType.ShowingAboutScreen
    state.showing_about_start_time = millis()


def transition_to_directing_to_floor(state, selected_floor, selected_car, direction_of_car):
    state.state_type = StateType.DirectingToFloor
    state.directing_to_floor_start_millis = millis()
    state.selected_car = selected_car
    state.selected_floor = selected_floor
    state.direction_of_car = direction_of_car
    state.directing_to_floor_context = {}
    arrival = ElevatorArrival()
    arrival.car = selected_car
    arrival.arrives_at = millis() + 10000
    state.elevator_arrivals.append(arrival)


def transition_to_accepting_new_input(state):
    state.state_type = StateType.AcceptingNewInput


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def get_selection_error(selection):
    if not is_int(selection):
        return ErrorType.FloorNotAvailable
    if abs(int(selection)) > 40:
        return ErrorType.FloorNotAvailable
    if int(selection) == 0:
        return ErrorType.Floor0Error
    if int(selection) == 13:
        return ErrorType.Floor13Error
    return None


def random_car():
    return random.choice(string.ascii_uppercase)


def get_direction_of_car(car):
    return Direction(ord(car) % len(Direction))


def update_from_appending_input(state):
    update_handicap_button_state(state)
    if millis() - state.appending_input_start_millis > 5000:
        selection_error = get_selection_error(state.floor_selection_buffer)
        if selection_error is None:
            car = random_car()
            transition_to_directing_to_floor(state, state.floor_selection_buffer, car, get_direction_of_car(car[0]))

        else:
            transition_to_showing_error(state, selection_error)
        return

    for event in state.events:
        for keypad_button in state.keypad_sprites:
            keypad_button.handle_event(event)
            keypad_button.update(state)
            if keypad_button.was_depressed:
                state.floor_selection_buffer = state.floor_selection_buffer + keypad_button.button_id

    if len(state.floor_selection_buffer) < (
    3 if state.floor_selection_buffer.startswith("-") and state.floor_selection_buffer.count("-") == 1 else 2):
        return

    selection_error = get_selection_error(state.floor_selection_buffer)
    if selection_error is None:
        car = random_car()
        transition_to_directing_to_floor(state, state.floor_selection_buffer, car, get_direction_of_car(car))
    else:
        transition_to_showing_error(state, selection_error)
    return


def update_handicap_button_state(state):
    handicap_button = None
    for hc in state.handicap_button_group:
        handicap_button = hc

    for event in state.events:
        handicap_button.handle_event(event)
        handicap_button.update(state)
        if handicap_button.was_depressed:
            state.in_handicap_mode = not state.in_handicap_mode
            return


def update_about_button_state(state):
    about_button = None
    for hc in state.about_button_group:
        about_button = hc

    for event in state.events:
        about_button.handle_event(event)
        about_button.update(state)
        if about_button.was_depressed:
            return True

    return False


def update_from_directing_to_floor(state):
    update_handicap_button_state(state)
    if millis() - state.directing_to_floor_start_millis > 8000:
        transition_to_accepting_new_input(state)


def update_from_showing_error(state):
    update_handicap_button_state(state)
    if millis() - state.showing_error_start_millis > 5000:
        transition_to_accepting_new_input(state)


def type_of_bath_today():
    weekday = date.today().weekday()
    if weekday == 5 or weekday == 6:
        return "D"
    if weekday == 1 or weekday == 3:
        return "M"
    return "N"


def type_of_ceremony_today():
    weekday = date.today().weekday()
    if weekday == 0:
        return "7S"

    if weekday % 2 == 0:
        return "S"

    return "MBP"


def render_from_showing_about_screen(state, display):
    render_arrivals(state)
    render_bg(display)
    line1 = Assets.font.render("Authors: Rowan Moorman and Michael Mooorman", True, (255, 255, 255))
    line2 = Assets.font.render("Created date:  2021-01-21", True, (255, 255, 255))
    line3 = Assets.font.render("Current date:  " + str(date.today()), True, (255, 255, 255))
    line4 = Assets.font.render("Days until Rowan's next birthday:  " + str(days_until_rowans_next_birthday()), True,
                               (255, 255, 255))

    line5 = Assets.font.render("Type of bath scheduled for today:  " + str(type_of_bath_today()), True,
                               (255, 255, 255))

    line6 = Assets.font.render("Type of ceremony scheduled for today:  " + str(type_of_ceremony_today()), True,
                               (255, 255, 255))
    display.blit(line1, (100, 80))
    display.blit(line2, (100, 80 * 2))
    display.blit(line3, (100, 80 * 3))
    display.blit(line4, (100, 80 * 4))
    display.blit(line5, (100, 80 * 5))
    display.blit(line6, (100, 80 * 6))


def days_until_rowans_next_birthday():
    today = date.today()
    if today > date(today.year, 6, 19):
        return (today - date(today.year + 1, 6, 19)).days
    return (date(today.year, 6, 19) - today).days


def render_from_accepting_new_input(state, display):
    render_arrivals(state)
    render_bg(display)
    state.keypad_sprites.draw(display)
    state.handicap_button_group.draw(display)
    state.about_button_group.draw(display)


def render_from_appending_input(state, display):
    render_arrivals(state)
    render_bg(display)
    state.keypad_sprites.draw(display)
    state.handicap_button_group.draw(display)
    state.about_button_group.draw(display)
    text = Assets.font.render(state.floor_selection_buffer, True, (255, 255, 255))
    display.blit(text, (500, 300))


direction_to_img = {
    Direction.Back: Assets.dir_d,
    Direction.Left: Assets.dir_l,
    Direction.BackLeft: Assets.dir_ld,
    Direction.Right: Assets.dir_r,
    Direction.BackRight: Assets.dir_rd
}
direction_to_sound = {
    Direction.Back: Assets.to_the_back_sound,
    Direction.Left: Assets.to_the_left_sound,
    Direction.BackLeft: Assets.to_the_back_left_sound,
    Direction.Right: Assets.to_the_right_sound,
    Direction.BackRight: Assets.to_the_back_right_sound
}


def image_of_direction(direction_of_car):
    return direction_to_img.get(direction_of_car)


def sound_of_direction(direction_of_car):
    return direction_to_sound.get(direction_of_car)


def play_arrival_sound(car):
    pass


def render_arrivals(state):
    for arrival in state.elevator_arrivals:
        t = millis() - arrival.arrives_at;
        if t < 0:
            continue

        if "STARTED_ELEVATOR_SOUND" not in arrival.sound_play_context:
            if state.in_handicap_mode:
                Assets.elevator_sound.play()
            arrival.sound_play_context["STARTED_ELEVATOR_SOUND"] = 1

        if "STARTED_CAR_SOUND" not in arrival.sound_play_context and t > 800:
            if state.in_handicap_mode:
                Assets.car_sounds.get(arrival.car).play()
            arrival.sound_play_context["STARTED_CAR_SOUND"] = 1

        if "STARTED_HAS_ARRIVED_SOUND" not in arrival.sound_play_context and t > 1500:
            if state.in_handicap_mode:
                Assets.has_arrived_sound.play()
            arrival.sound_play_context["STARTED_HAS_ARRIVED_SOUND"] = 1
            state.elevator_arrivals.remove(arrival)


def render_from_directing_to_floor(state, display):
    render_arrivals(state)
    if "STARTED_FLOOR_SOUND" not in state.directing_to_floor_context and millis() - state.directing_to_floor_start_millis > 1200 and state.in_handicap_mode:
        Assets.floor_sound.play()
        state.directing_to_floor_context["STARTED_FLOOR_SOUND"] = 1

    if "STARTED_FLOOR_NUMBER_SOUND" not in state.directing_to_floor_context and millis() - state.directing_to_floor_start_millis > 2000 and state.in_handicap_mode:
        Assets.floor_sounds.get(str(abs(int(state.floor_selection_buffer)))).play()
        state.directing_to_floor_context["STARTED_FLOOR_NUMBER_SOUND"] = 1

    if "STARTED_PROCEED_TO_CAR_SOUND" not in state.directing_to_floor_context and millis() - state.directing_to_floor_start_millis > 2900 and state.in_handicap_mode:
        Assets.proceed_to_car_sound.play()
        state.directing_to_floor_context["STARTED_PROCEED_TO_CAR_SOUND"] = 1

    if "STARTED_CAR_SOUND" not in state.directing_to_floor_context and millis() - state.directing_to_floor_start_millis > 4000 and state.in_handicap_mode:
        Assets.car_sounds.get(state.selected_car).play()
        state.directing_to_floor_context["STARTED_CAR_SOUND"] = 1

    if "STARTED_DIRECTIONAL_SOUND" not in state.directing_to_floor_context and millis() - state.directing_to_floor_start_millis > 4500 and state.in_handicap_mode:
        sound_of_direction(state.direction_of_car).play()
        state.directing_to_floor_context["STARTED_DIRECTIONAL_SOUND"] = 1

    render_bg(display)
    text = Assets.big_font.render("FOLLOW INSTRUCTIONS BELOW", True, (255, 255, 255))
    display.blit(text, [display.get_width() / 2 - text.get_width() / 2, 50])

    car_text_box_center = (1024 / 3, 120)
    floor_text_box_center = ((1024 / 3) * 2, 120)
    box_width = 100
    box_height = 100
    box_stroke = 3

    car_text = Assets.big_font.render("Car", True, (255, 255, 255))
    display.blit(car_text, (car_text_box_center[0] - car_text.get_width() / 2, car_text_box_center[1]))

    car_box_rect = pygame.Rect(
        car_text_box_center[0] - car_text.get_width() / 2 - (box_width - car_text.get_width()) / 2,
        car_text_box_center[1] + car_text.get_height(),
        box_width,
        box_height)

    pygame.draw.rect(display, (255, 255, 255), car_box_rect, box_stroke)

    selected_car_text = Assets.big_font.render(state.selected_car, True, (255, 255, 255))
    display.blit(selected_car_text,
                 (
                     car_box_rect.x + car_box_rect.width / 2 - (selected_car_text.get_width() / 2),
                     car_box_rect.y + car_box_rect.height / 2 - (selected_car_text.get_height() / 2)
                 )
                 )

    floor_text = Assets.big_font.render("Floor", True, (255, 255, 255))
    display.blit(floor_text, (floor_text_box_center[0] - floor_text.get_width() / 2, floor_text_box_center[1]))

    floor_box_rect = pygame.Rect(
        floor_text_box_center[0] - floor_text.get_width() / 2 - (box_width - floor_text.get_width()) / 2,
        floor_text_box_center[1] + floor_text.get_height(),
        box_width,
        box_height)
    pygame.draw.rect(display, (255, 255, 255), floor_box_rect, box_stroke)

    selected_floor_text = Assets.big_font.render(state.selected_floor, True, (255, 255, 255))
    display.blit(selected_floor_text,
                 (
                     floor_box_rect.x + floor_box_rect.width / 2 - (selected_floor_text.get_width() / 2),
                     floor_box_rect.y + floor_box_rect.height / 2 - (selected_floor_text.get_height() / 2)
                 )
                 )

    dir_img = image_of_direction(state.direction_of_car).convert_alpha()

    display.blit(dir_img, (1024 / 2 - (dir_img.get_width() / 2), 230))


def convert_alpha(img):
    return img.convert_alpha()


def render_from_showing_error(state, display):
    render_arrivals(state)
    render_bg(display)
    if state.error_type == ErrorType.FloorNotAvailable:

        if "ENTRY_NOT_UNDERSTOOD_SOUND" not in state.showing_error_context and millis() - state.showing_error_start_millis > 1200 and state.in_handicap_mode:
            Assets.entry_not_understood_sound.play()
            state.showing_error_context["ENTRY_NOT_UNDERSTOOD_SOUND"] = 1

        text1 = Assets.font.render("Entry not understood!", True, (255, 255, 255))
        text2 = Assets.font.render("Floor " + state.floor_selection_buffer, True, (255, 255, 255))
        display.blit(text1, (500, 200))
        display.blit(text2, (500, 300))

    if state.error_type == ErrorType.Floor0Error or state.error_type == ErrorType.Floor13Error:
        if "FLOOR_NOT_AVAILABLE_SOUND" not in state.showing_error_context and millis() - state.showing_error_start_millis > 1200 and state.in_handicap_mode:
            Assets.floor_not_available_sound.play()
            state.showing_error_context["FLOOR_NOT_AVAILABLE_SOUND"] = 1

        text1 = Assets.font.render("Floor Not Available!", True, (255, 255, 255))
        text2 = Assets.font.render("Floor " + state.floor_selection_buffer, True, (255, 255, 255))
        display.blit(text1, (500, 200))
        display.blit(text2, (500, 300))


update_funcs = {
    StateType.AcceptingNewInput: update_from_accepting_new_input,
    StateType.AppendingInput: update_from_appending_input,
    StateType.DirectingToFloor: update_from_directing_to_floor,
    StateType.ShowingError: update_from_showing_error,
    StateType.ShowingAboutScreen: update_from_about_screen
}


def update_state(state):
    update_funcs.get(state.state_type)(state)


render_funcs = {
    StateType.AcceptingNewInput: render_from_accepting_new_input,
    StateType.AppendingInput: render_from_appending_input,
    StateType.DirectingToFloor: render_from_directing_to_floor,
    StateType.ShowingError: render_from_showing_error,
    StateType.ShowingAboutScreen: render_from_showing_about_screen
}


def render_state(state, display):
    render_funcs.get(state.state_type)(state, display)


def main():
    pygame.init()
    print(pygame.display.Info().current_w, "x", pygame.display.Info().current_h)

    if environ.get('FULL_SCREEN') is not None:
        print("Using full screen mode")
        display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        print("Using windowed mode")
        display = pygame.display.set_mode((1024, 600))

    state = State()

    run = True
    while run:
        state.events = pygame.event.get()
        for event in state.events:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                run = False
        update_state(state)
        render_state(state, display)
        pygame.display.flip()
        time.sleep(1 / 6)

    pygame.quit()


def render_bg(display):
    display.blit(Assets.bg, (0, 0))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
