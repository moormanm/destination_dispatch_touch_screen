import pygame
from state import *
import time
from os import environ

blue = (0, 96, 255)


def update_from_accepting_new_input(state):
    for event in state.events:
        for keypad_button in state.keypad_sprites:
            keypad_button.handle_event(event)
            keypad_button.update()
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


def transition_to_directing_to_floor(state):
    state.state_type = StateType.DirectingToFloor
    state.directing_to_floor_start_millis = millis()


def transition_to_accepting_new_input(state):
    state.state_type = StateType.AcceptingNewInput


def get_selection_error(selection):
    if int(selection) > 50:
        return ErrorType.FloorNotAvailable

    return None


def update_from_appending_input(state):
    if millis() - state.appending_input_start_millis > 5000:
        selection_error = get_selection_error(state.floor_selection_buffer)
        if selection_error is None:
            transition_to_directing_to_floor(state)
        else:
            transition_to_showing_error(state, selection_error)
        return

    for event in state.events:
        for keypad_button in state.keypad_sprites:
            keypad_button.handle_event(event)
            keypad_button.update()
            if keypad_button.was_depressed:
                state.floor_selection_buffer = state.floor_selection_buffer + keypad_button.button_id

    if len(state.floor_selection_buffer) < 2:
        return

    selection_error = get_selection_error(state.floor_selection_buffer)
    if selection_error is None:
        transition_to_directing_to_floor(state)
    else:
        transition_to_showing_error(state, selection_error)
    return


def update_from_directing_to_floor(state):
    if millis() - state.appending_input_start_millis > 5000:
        transition_to_accepting_new_input(state)


def update_from_showing_error(state):
    if millis() - state.showing_error_start_millis > 5000:
        transition_to_accepting_new_input(state)


def render_from_accepting_new_input(state, display):
    display.fill(blue)
    state.keypad_sprites.draw(display)


def render_from_appending_input(state, display):
    display.fill(blue)
    state.keypad_sprites.draw(display)


def render_from_directing_to_floor(state, display):
    display.fill(blue)


def render_from_showing_floor(state, display):
    display.fill(blue)


update_funcs = {
    StateType.AcceptingNewInput: update_from_accepting_new_input,
    StateType.AppendingInput: update_from_appending_input,
    StateType.DirectingToFloor: update_from_directing_to_floor,
    StateType.ShowingError: update_from_showing_error
}


def update_state(state):
    update_funcs.get(state.state_type)(state)


render_funcs = {
    StateType.AcceptingNewInput: render_from_accepting_new_input,
    StateType.AppendingInput: render_from_appending_input,
    StateType.DirectingToFloor: render_from_directing_to_floor,
    StateType.ShowingError: render_from_showing_floor
}


def render_state(state, display):
    render_funcs.get(state.state_type)(state, display)


def main():
    pygame.init()

    if environ.get('FULL_SCREEN') is not None:
        display = pygame.display.set_mode((1024, 768),  pygame.FULLSCREEN)
    else:
        display = pygame.display.set_mode((1024, 768))

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
        time.sleep(1/60)

    pygame.quit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
