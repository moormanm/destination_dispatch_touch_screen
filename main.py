

print("initting main.py", flush=True)

import datetime
import string
from datetime import date
import thorpy.elements.slider
from elements.checker import Checker
from pygame.surface import Surface
import lightning_mode
from state import State, StateType, ErrorType, Direction, ElevatorArrival, StatsType
from assets import Assets
from os import environ
import random
import sqlite3
from os.path import expanduser
import pygame
from pyvidplayer import Video
import sys

frame_rate = 30
home = expanduser("~")


def stub_data():
    for i in range(-99, 99):
        for c in range(ord('A'), ord('Z') + 1):
            car_id = chr(c)
            floor_id = i
            tally_call(floor_id, car_id, True)
            tally_call(floor_id, car_id, False)


def setup_db():
    stmt = 'CREATE TABLE IF NOT EXISTS call_stats (id INTEGER PRIMARY KEY AUTOINCREMENT, floor_number INTEGER, car_id TEXT, successful INTEGER);'
    conn.execute(stmt)


def tally_call(floor_number, car_id, is_successful):
    stmt = "INSERT INTO call_stats(floor_number, car_id, successful) VALUES (?, ?, ?)"
    conn.execute(stmt, (floor_number, car_id, 1 if is_successful else 0))
    conn.commit()


def get_call_stats():
    successful_calls_stmt = 'SELECT COUNT(*) from call_stats where successful = 1'
    unsuccessful_calls_stmt = 'SELECT COUNT(*) from call_stats where successful = 0'
    successful_calls = conn.execute(successful_calls_stmt).fetchone()[0]
    unsuccessful_calls = conn.execute(unsuccessful_calls_stmt).fetchone()[0]
    return successful_calls, unsuccessful_calls


def get_call_stats_by_floor():
    sql = 'SELECT floor_number, COUNT(*) from call_stats group by floor_number order by floor_number'
    results = conn.execute(sql).fetchall()
    return {x[0]: x[1] for x in results}


def get_call_stats_by_car():
    sql = 'SELECT car_id, COUNT(*) from call_stats where car_id is not null group by car_id order by car_id'
    results = conn.execute(sql).fetchall()
    return {x[0]: x[1] for x in results}


conn = sqlite3.connect(home + '/destination-dispatch.db')
setup_db()


def update_from_about_screen(state):
    if update_car_stats_button_state(state):
        transition_to_showing_stats_screen(state, StatsType.Car)
        return

    if update_floor_stats_button_state(state):
        transition_to_showing_stats_screen(state, StatsType.Floor)
        return
    if millis() - state.showing_about_start_time > 8000:
        transition_to_accepting_new_input(state)


def update_from_accepting_new_input(state):
    update_handicap_button_state(state)
    if update_floor_selection_button_state(state):
        transition_to_choose_floor_screen(state)
        return
    if update_about_button_state(state):
        transition_to_showing_about_screen(state)
        return
    if update_lightning_mode_button_state(state):
        transition_to_showing_lightning_maze_screen(state)
        return
    if update_calc_button_state(state):
        transition_to_showing_calculator_gallery(state)
        return

    for event in state.events:
        for keypad_button in state.keypad_sprites:
            keypad_button.handle_event(event)
            keypad_button.update(state)
            if keypad_button.was_depressed:
                transition_to_appending_input(state, keypad_button.button_id)
                return


def millis():
    return pygame.time.get_ticks()


def transition_to_appending_input(state, selected_key):
    state.state_type = StateType.AppendingInput
    state.floor_selection_buffer = selected_key
    state.appending_input_start_millis = millis()


def transition_to_showing_error(state, error_type):
    state.state_type = StateType.ShowingError
    state.showing_error_start_millis = millis()
    state.error_type = error_type
    state.showing_error_context = {}
    tally_call(state.floor_selection_buffer, None, False)


def transition_to_showing_about_screen(state):
    state.state_type = StateType.ShowingAboutScreen
    state.showing_about_start_time = millis()


def transition_to_showing_stats_screen(state, stats_type):
    state.state_type = StateType.ShowingStatsScreen
    state.showing_stats_start_time = millis()
    state.stats_type = stats_type


def transition_to_showing_lightning_maze_screen(state: State):
    state.state_type = StateType.ShowingLightningMazeScreen
    state.lightning_mode_state = lightning_mode.LightningModeState(
        search_all_paths=state.lightning_mode_widgets.search_all_paths_checkbox.get_value())
    state.lightning_mode_is_paused = False

    def restart_func():
        Assets.lightning_strike_sound.stop()
        transition_to_showing_lightning_maze_screen(state)

    def quit_func():
        Assets.lightning_strike_sound.stop()
        transition_to_accepting_new_input(state)

    def pause_func():
        state.lightning_mode_is_paused = not state.lightning_mode_is_paused
        state.lightning_mode_widgets.pause_play_button.set_text("Play" if state.lightning_mode_is_paused else "Pause")
        if state.lightning_mode_is_paused:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause()
        state.lightning_mode_widgets.time_slider.set_active(state.lightning_mode_is_paused)

    state.lightning_mode_widgets.enable_sound_checkbox.set_topleft((115, 80))
    state.lightning_mode_widgets.search_all_paths_checkbox.set_topleft((115, 110))
    state.lightning_mode_widgets.show_numbers_checkbox.set_topleft((115, 140))
    state.lightning_mode_widgets.restart_button = thorpy.make_button("Restart", func=restart_func)
    state.lightning_mode_widgets.quit_button = thorpy.make_button("Quit", func=quit_func)
    state.lightning_mode_widgets.pause_play_button = thorpy.make_button("Pause", func=pause_func)

    state.lightning_mode_widgets.show_numbers_checkbox._name_element.set_font_color((255, 255, 255))
    state.lightning_mode_widgets.show_numbers_checkbox._name_element.set_font(Assets.little_font)
    state.lightning_mode_widgets.search_all_paths_checkbox._name_element.set_font_color((255, 255, 255))
    state.lightning_mode_widgets.search_all_paths_checkbox._name_element.set_font(Assets.little_font)
    state.lightning_mode_widgets.enable_sound_checkbox._name_element.set_font_color((255, 255, 255))
    state.lightning_mode_widgets.enable_sound_checkbox._name_element.set_font(Assets.little_font)

    bottom_part_y = 500
    state.lightning_mode_widgets.restart_button.set_topleft((30, bottom_part_y))
    state.lightning_mode_widgets.quit_button.set_topleft((100, bottom_part_y))

    state.lightning_mode_widgets.pause_play_button.set_topleft((75, 280))
    state.lightning_mode_widgets.time_slider = thorpy.SliderX(length=150,
                                                              limvals=(0, state.lightning_mode_state.final_step),
                                                              text='',
                                                              type_=int)
    state.lightning_mode_widgets.time_slider.set_topleft((10, 200))
    state.lightning_mode_widgets.time_slider.get_slider().set_size((150, 30))
    state.lightning_mode_widgets.time_slider.get_dragger().set_size((15, 50))

    state.lightning_mode_widgets.time_slider._value_element.set_visible(False)

    state.lightning_mode_widgets.time_slider.set_active(False)

    def slider_react_func_pause(event, state: State):
        if event.el == state.lightning_mode_widgets.time_slider and event.id == thorpy.constants.EVENT_SLIDE:
            state.lightning_mode_state.current_step = state.lightning_mode_widgets.time_slider.get_value()

    slider_reaction_pause = thorpy.Reaction(
        reacts_to=thorpy.constants.THORPY_EVENT,
        reac_func=slider_react_func_pause,
        params={'state': state}
    )
    state.lightning_mode_widgets.time_slider.add_reactions([slider_reaction_pause])
    state.thorpy_base_menu.set_elements(
        state.lightning_mode_widgets.static_widgets + [state.lightning_mode_widgets.restart_button,
                                                       state.lightning_mode_widgets.quit_button,
                                                       state.lightning_mode_widgets.pause_play_button,
                                                       state.lightning_mode_widgets.time_slider])
    state.thorpy_base_menu.refresh()


def transition_to_directing_to_floor(state, selected_floor, selected_car, direction_of_car):
    state.state_type = StateType.DirectingToFloor
    state.directing_to_floor_start_millis = millis()
    state.selected_car = selected_car
    state.selected_floor = selected_floor
    state.direction_of_car = direction_of_car
    state.directing_to_floor_context = {"delay_sound_until": 1200 + millis()}
    arrival = ElevatorArrival()
    arrival.car = selected_car
    arrival.arrives_at = millis() + 10000
    state.elevator_arrivals.append(arrival)
    tally_call(selected_floor, selected_car, True)


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
    if int(selection) == -13:
        return ErrorType.Floor13Error
    return None


def pick_car(floor_num):
    if floor_num == 11:
        return "G"
    if floor_num == 8:
        return "Z"
    if floor_num == 5:
        return "M"
    if floor_num == 7:
        return "N"

    if floor_num == 3:
        return "P"

    if floor_num == 14:
        return random.choice(["P", "U"])

    if floor_num == 1:
        return "R"

    if floor_num == 12:
        return "U"

    return random.choice(string.ascii_uppercase)


def get_direction_of_car(car):
    return Direction(ord(car) % len(Direction))


def transition_to_choose_floor_screen(state):
    state.state_type = StateType.ShowingDestinationButtonsScreen
    state.active_destination_buttons_group_idx = 0


def update_from_appending_input(state):
    update_handicap_button_state(state)
    if update_floor_selection_button_state(state):
        transition_to_choose_floor_screen(state)
        return

    if update_lightning_mode_button_state(state):
        transition_to_showing_lightning_maze_screen(state)
        return

    if update_calc_button_state(state):
        transition_to_showing_calculator_gallery(state)
        return

    if millis() - state.appending_input_start_millis > 5000:
        selection_error = get_selection_error(state.floor_selection_buffer)
        if selection_error is None:
            car = pick_car(int(state.floor_selection_buffer))
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
        car = pick_car(int(state.floor_selection_buffer))
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


def update_lightning_mode_button_state(state):
    btn = None
    for hc in state.lightning_mode_button_group:
        btn = hc

    for event in state.events:
        btn.handle_event(event)
        btn.update(state)
        if btn.was_depressed:
            return True

    return False


def update_calc_button_state(state):
    btn = None
    for hc in state.calculator_gallery_button_group:
        btn = hc

    for event in state.events:
        btn.handle_event(event)
        btn.update(state)
        if btn.was_depressed:
            return True

    return False


def update_car_stats_button_state(state):
    stats_button = None
    for hc in state.car_stats_button_group:
        stats_button = hc

    for event in state.events:
        stats_button.handle_event(event)
        stats_button.update(state)
        if stats_button.was_depressed:
            return True

    return False


def update_floor_stats_button_state(state):
    stats_button = None
    for hc in state.floor_stats_button_group:
        stats_button = hc

    for event in state.events:
        stats_button.handle_event(event)
        stats_button.update(state)
        if stats_button.was_depressed:
            return True

    return False


def update_floor_selection_button_state(state):
    floor_selection_button = None
    for hc in state.choose_floors_button_group:
        floor_selection_button = hc

    for event in state.events:
        floor_selection_button.handle_event(event)
        floor_selection_button.update(state)
        if floor_selection_button.was_depressed:
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


def render_floor_stats(display):
    floor_call_stats = get_call_stats_by_floor()
    i = 0
    v_pad = 26
    start_y = 50

    floor_stats_line = Assets.font.render("Floor Stats", True, (255, 255, 255))

    start_x = 20
    display.blit(floor_stats_line, (start_x, 10))

    for floor in floor_call_stats:
        count = floor_call_stats[floor]
        line = Assets.little_font.render(str(floor) + " : " + str(count), True, (255, 255, 255))
        display.blit(line, (start_x, start_y + v_pad * i))
        i = i + 1
        if i == 20:
            i = 0
            start_x += 100


def render_car_stats(display):
    car_call_stats = get_call_stats_by_car()
    i = 0
    v_pad = 60
    start_y = 70

    floor_stats_line = Assets.font.render("Car Stats", True, (255, 255, 255))

    start_x = 20
    display.blit(floor_stats_line, (start_x, 10))

    for car in car_call_stats:
        count = car_call_stats[car]
        line = Assets.font.render(str(car) + " : " + str(count), True, (255, 255, 255))
        display.blit(line, (start_x, start_y + v_pad * i))
        i = i + 1
        if i == 6:
            i = 0
            start_x += 200


def render_from_showing_stats_screen(state, display):
    render_bg(display)
    if state.stats_type == StatsType.Floor:
        render_floor_stats(display)
    else:
        render_car_stats(display)


def render_from_showing_lightning_screen(state: State, display):
    render_bg(display)
    surface = Surface((800, 580))
    lightning_mode.draw_current_step(state.lightning_mode_state, surface)
    state.lightning_mode_widgets.time_slider.blit()
    state.lightning_mode_widgets.pause_play_button.blit()
    state.lightning_mode_widgets.quit_button.blit()
    state.lightning_mode_widgets.restart_button.blit()
    state.lightning_mode_widgets.show_numbers_checkbox.blit()
    state.lightning_mode_widgets.search_all_paths_checkbox.blit()
    state.lightning_mode_widgets.enable_sound_checkbox.blit()
    display.blit(Assets.lightning_mode_step_number_line, (20, 180))
    display.blit(surface, (200, 10))


def render_from_showing_about_screen(state, display):
    render_arrivals(state)
    render_bg(display)
    state.floor_stats_button_group.draw(display)
    state.car_stats_button_group.draw(display)

    call_stats = get_call_stats()

    line1 = Assets.font.render("Authors: Rowan Moorman and Michael Mooorman", True, (255, 255, 255))
    line2 = Assets.font.render("Created date:  2021-01-21", True, (255, 255, 255))
    line3 = Assets.font.render("Current date:  " + str(date.today()), True, (255, 255, 255))
    line4 = Assets.font.render("Days until Rowan's next birthday:  " + str(days_until_rowans_next_birthday()), True,
                               (255, 255, 255))

    line5 = Assets.font.render("Type of bath scheduled for today:  " + str(type_of_bath_today()), True,
                               (255, 255, 255))

    line6 = Assets.font.render("Type of ceremony scheduled for today:  " + str(type_of_ceremony_today()), True,
                               (255, 255, 255))

    line7 = Assets.font.render("Successful calls : " + str(call_stats[0]), True,
                               (255, 255, 255))
    line8 = Assets.font.render("Failed calls : " + str(call_stats[1]), True,
                               (255, 255, 255))
    vpad = 70
    start = 20
    display.blit(line1, (100, start + vpad * 0))
    display.blit(line2, (100, start + vpad * 1))
    display.blit(line3, (100, start + vpad * 2))
    display.blit(line4, (100, start + vpad * 3))
    display.blit(line5, (100, start + vpad * 4))
    display.blit(line6, (100, start + vpad * 5))
    display.blit(line7, (100, start + vpad * 6))
    display.blit(line8, (100, start + vpad * 7))


def days_until_rowans_next_birthday():
    today = date.today()
    if today > date(today.year, 6, 19):
        return abs((today - date(today.year + 1, 6, 19)).days)
    return abs((date(today.year, 6, 19) - today).days)


def render_from_accepting_new_input(state, display):
    render_arrivals(state)
    render_bg(display)
    state.keypad_sprites.draw(display)
    state.handicap_button_group.draw(display)
    state.choose_floors_button_group.draw(display)
    state.about_button_group.draw(display)
    state.lightning_mode_button_group.draw(display)
    state.calculator_gallery_button_group.draw(display)


def render_from_appending_input(state, display):
    render_arrivals(state)
    render_bg(display)
    state.keypad_sprites.draw(display)
    state.handicap_button_group.draw(display)
    state.about_button_group.draw(display)
    state.lightning_mode_button_group.draw(display)
    state.choose_floors_button_group.draw(display)
    state.calculator_gallery_button_group.draw(display)
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


def render_arrivals(state):
    for arrival in state.elevator_arrivals:
        t = millis() - arrival.arrives_at
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

    render_direct_to_floor_sounds(state)

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

    if int(state.floor_selection_buffer) == 26:
        thirteen_is_showing = millis() - state.directing_to_floor_start_millis < 3500
        if thirteen_is_showing:
            display.blit(Assets.numberblock_13.convert_alpha(), (720, 280))
            display.blit(Assets.numberblock_13.convert_alpha(), (720 - 600, 280))
            numberling_text = Assets.font.render("13", True, (0, 0, 0))
            display.blit(numberling_text, (775, 250))
            display.blit(numberling_text, (775 - 600, 250))
        else:
            display.blit(Assets.numberblock_10.convert_alpha(), (690, 280))
            display.blit(Assets.numberblock_3.convert_alpha(), (850, 320))
            display.blit(Assets.numberblock_10.convert_alpha(), (690 - 600, 280))
            display.blit(Assets.numberblock_3.convert_alpha(), (850 - 600, 320))


def render_direct_to_floor_sounds(state):
    if state.directing_to_floor_context["delay_sound_until"] > millis():
        return

    if not state.in_handicap_mode:
        return

    if "STARTED_FLOOR_SOUND" not in state.directing_to_floor_context:
        Assets.floor_sound.play()
        state.directing_to_floor_context["STARTED_FLOOR_SOUND"] = 1
        state.directing_to_floor_context["delay_sound_until"] = millis() + 800
        return

    if "STARTED_MINUS_SOUND" not in state.directing_to_floor_context and int(state.selected_floor) < 0:
        Assets.minus_sound.play()
        state.directing_to_floor_context["STARTED_MINUS_SOUND"] = 1
        state.directing_to_floor_context["delay_sound_until"] = millis() + 600
        return

    if "STARTED_FLOOR_NUMBER_SOUND" not in state.directing_to_floor_context:
        Assets.floor_sounds.get(str(abs(int(state.selected_floor)))).play()
        state.directing_to_floor_context["STARTED_FLOOR_NUMBER_SOUND"] = 1
        state.directing_to_floor_context["delay_sound_until"] = millis() + 900
        return

    if "STARTED_PROCEED_TO_CAR_SOUND" not in state.directing_to_floor_context:
        Assets.proceed_to_car_sound.play()
        state.directing_to_floor_context["STARTED_PROCEED_TO_CAR_SOUND"] = 1
        state.directing_to_floor_context["delay_sound_until"] = millis() + 1100
        return

    if "STARTED_CAR_SOUND" not in state.directing_to_floor_context:
        Assets.car_sounds.get(state.selected_car).play()
        state.directing_to_floor_context["STARTED_CAR_SOUND"] = 1
        state.directing_to_floor_context["delay_sound_until"] = millis() + 500
        return

    if "STARTED_DIRECTIONAL_SOUND" not in state.directing_to_floor_context and millis() - state.directing_to_floor_start_millis > 4500 and state.in_handicap_mode:
        sound_of_direction(state.direction_of_car).play()
        state.directing_to_floor_context["STARTED_DIRECTIONAL_SOUND"] = 1
        return


def convert_alpha(img):
    return img.convert_alpha()


def render_from_showing_error(state, display):
    render_arrivals(state)
    render_bg(display)
    font_color = (255, 255, 255) if is_night_mode() else (0, 0, 0)

    if state.error_type == ErrorType.FloorNotAvailable:

        if "ENTRY_NOT_UNDERSTOOD_SOUND" not in state.showing_error_context and millis() - state.showing_error_start_millis > 1200 and state.in_handicap_mode:
            Assets.entry_not_understood_sound.play()
            state.showing_error_context["ENTRY_NOT_UNDERSTOOD_SOUND"] = 1

        text1 = Assets.font.render("Entry not understood!", True, font_color)
        text2 = Assets.font.render("Floor " + state.floor_selection_buffer, True, font_color)
        display.blit(text1, (500, 200))
        display.blit(text2, (500, 300))

    if state.error_type == ErrorType.Floor13Error:
        text1 = Assets.font.render("Unlucky floor " + state.floor_selection_buffer + "... Who said that?!", True,
                                   font_color)
        text2 = Assets.font.render("Floor " + state.floor_selection_buffer, True, font_color)
        if "FLOOR_NOT_AVAILABLE_SOUND" not in state.showing_error_context and millis() - state.showing_error_start_millis > 1200 and state.in_handicap_mode:
            if int(state.floor_selection_buffer) == -13:
                Assets.floor_minus_13_error_sound.play()
            else:
                Assets.floor_13_error_sound.play()
            state.showing_error_context["FLOOR_NOT_AVAILABLE_SOUND"] = 1

        thirteen_is_showing = millis() - state.showing_error_start_millis < 2000
        if thirteen_is_showing:
            display.blit(Assets.numberblock_13.convert_alpha(), (720, 280))
            numberling_text = Assets.font.render("13", True, font_color)
            display.blit(numberling_text, (775, 250))
        else:
            display.blit(Assets.numberblock_10.convert_alpha(), (690, 280))
            display.blit(Assets.numberblock_3.convert_alpha(), (850, 320))

        display.blit(text1, (500, 200))
        display.blit(text2, (500, 300))

    if state.error_type == ErrorType.Floor0Error:
        if "FLOOR_NOT_AVAILABLE_SOUND" not in state.showing_error_context and millis() - state.showing_error_start_millis > 1200 and state.in_handicap_mode:
            Assets.floor_not_available_sound.play()
            state.showing_error_context["FLOOR_NOT_AVAILABLE_SOUND"] = 1

        text1 = Assets.font.render("Floor Not Available!", True, (255, 255, 255))
        text2 = Assets.font.render("Floor " + state.floor_selection_buffer, True, (255, 255, 255))
        if state.error_type == ErrorType.Floor13Error:
            text1 = Assets.font.render("That is an unlucky floor!", True, (255, 255, 255))
            text2 = Assets.font.render("Floor " + state.floor_selection_buffer, True, (255, 255, 255))

        display.blit(text1, (500, 200))
        display.blit(text2, (500, 300))


def render_from_showing_destination_buttons_screen(state, display):
    render_arrivals(state)
    render_bg(display)
    state.destination_button_groups[state.active_destination_buttons_group_idx].draw(display)
    state.handicap_button_group.draw(display)
    state.about_button_group.draw(display)
    state.lightning_mode_button_group.draw(display)
    state.calculator_gallery_button_group.draw(display)
    state.more_floors_button_group.draw(display)
    state.back_to_keypad_button_group.draw(display)


def update_from_showing_destination_buttons_screen(state):
    update_handicap_button_state(state)
    if update_about_button_state(state):
        transition_to_showing_about_screen(state)
        return
    if update_lightning_mode_button_state(state):
        transition_to_showing_lightning_maze_screen(state)
        return

    if update_calc_button_state(state):
        transition_to_showing_calculator_gallery(state)
        return

    more_floors_button = None
    for hc in state.more_floors_button_group:
        more_floors_button = hc

    back_to_keypad_button = None
    for hc in state.back_to_keypad_button_group:
        back_to_keypad_button = hc

    for event in state.events:
        for destination_button in state.destination_button_groups[state.active_destination_buttons_group_idx]:
            destination_button.handle_event(event)
            destination_button.update(state)
            if destination_button.was_depressed:
                car = pick_car(int(destination_button.button_id))
                transition_to_directing_to_floor(state, destination_button.button_id, car, get_direction_of_car(car))
                return

            more_floors_button.handle_event(event)
            more_floors_button.update(state)
            if more_floors_button.was_depressed:
                state.active_destination_buttons_group_idx = (state.active_destination_buttons_group_idx + 1) % len(
                    state.destination_button_groups)
            back_to_keypad_button.handle_event(event)
            back_to_keypad_button.update(state)
            if back_to_keypad_button.was_depressed:
                transition_to_accepting_new_input(state)
                return


def update_from_stats_screen(state):
    if millis() - state.showing_stats_start_time > 8000:
        transition_to_accepting_new_input(state)


def transition_to_showing_calculator_gallery(state: State):
    state.state_type = StateType.ShowingCalculatorGallery
    state.last_calculator_gallery_change = millis()
    state.current_calc_showing = 0
    state.vid = Video("assets/videoplayback.mp4")
    state.vid.set_size((1024, 600))
    state.drew_bg = False


def update_from_showing_calculator_gallery(state: State):
    for event in state.events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            state.vid.close()
            transition_to_accepting_new_input(state)
            return


def render_from_showing_calculator_gallery(state: State, display):
    if not state.drew_bg:
        render_bg(display)
        state.drew_bg = True
    state.vid.draw(display, (0, 0), force_draw=False)


def update_from_showing_lightning_screen(state: State):
    state.lightning_mode_state.show_numbers = state.lightning_mode_widgets.show_numbers_checkbox.get_value()
    state.lightning_mode_widgets.time_slider.get_slider().set_text(str(state.lightning_mode_state.current_step))
    state.lightning_mode_state.enable_sound = state.lightning_mode_widgets.enable_sound_checkbox.get_value()
    if not state.lightning_mode_is_paused:
        state.lightning_mode_widgets.time_slider.set_value(state.lightning_mode_state.current_step)

    if state.lightning_mode_state.endRequested:
        transition_to_accepting_new_input(state)
    if not state.lightning_mode_is_paused and not state.lightning_mode_state.tick():
        transition_to_showing_lightning_maze_screen(state)


update_funcs = {
    StateType.AcceptingNewInput: update_from_accepting_new_input,
    StateType.AppendingInput: update_from_appending_input,
    StateType.DirectingToFloor: update_from_directing_to_floor,
    StateType.ShowingError: update_from_showing_error,
    StateType.ShowingAboutScreen: update_from_about_screen,
    StateType.ShowingDestinationButtonsScreen: update_from_showing_destination_buttons_screen,
    StateType.ShowingStatsScreen: update_from_stats_screen,
    StateType.ShowingLightningMazeScreen: update_from_showing_lightning_screen,
    StateType.ShowingCalculatorGallery: update_from_showing_calculator_gallery
}


def update_state(state):
    update_funcs.get(state.state_type)(state)


render_funcs = {
    StateType.AcceptingNewInput: render_from_accepting_new_input,
    StateType.AppendingInput: render_from_appending_input,
    StateType.DirectingToFloor: render_from_directing_to_floor,
    StateType.ShowingError: render_from_showing_error,
    StateType.ShowingAboutScreen: render_from_showing_about_screen,
    StateType.ShowingDestinationButtonsScreen: render_from_showing_destination_buttons_screen,
    StateType.ShowingStatsScreen: render_from_showing_stats_screen,
    StateType.ShowingLightningMazeScreen: render_from_showing_lightning_screen,
    StateType.ShowingCalculatorGallery: render_from_showing_calculator_gallery,
}


def render_state(state, display):
    render_funcs.get(state.state_type)(state, display)


def main():
    print("initting main", flush=True)
    pygame.init()
    print(pygame.display.Info().current_w, "x", pygame.display.Info().current_h, flush=True)

    if environ.get('FULL_SCREEN') is not None:
        print("Using full screen mode", flush=True)
        pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
        display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        print("Using windowed mode", flush=True)
        display = pygame.display.set_mode((1024, 600))

    print("start initting state", flush=True)
    state = State(display)
    print("done initting state", flush=True)
    clock = pygame.time.Clock()
    run = True
    while run:
        state.events = pygame.event.get()
        for event in state.events:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                run = False
            state.thorpy_base_menu.react(event)
        update_state(state)
        render_state(state, display)
        pygame.display.flip()
        clock.tick(frame_rate)

    pygame.quit()


def is_night_mode():
    return not is_day_mode()


def is_day_mode():
    # return 8 <= datetime.datetime.now().hour <= (12 + 6)
    return False


easter_days = [datetime.date(2021, 4, 3), datetime.date(2021, 4, 4)]


def render_bg(display):
    bg = Assets.day_time_bg if is_day_mode() else Assets.night_time_bg
    display.blit(bg, (0, 0))
    if datetime.datetime.today().date() in easter_days:
        display.blit(Assets.easter_bunny.convert_alpha(), (330, 270))


if __name__ == '__main__':
    main()
