import pygame

print("initting font")
pygame.font.init()


print("initting music")
pygame.mixer.init()


print("initting Assets")

class Assets:

    button_pressed = pygame.transform.scale(pygame.image.load('assets/button_pressed.png'), (100, 100))
    button_unpressed = pygame.transform.scale(pygame.image.load('assets/button_unpressed.png'), (100, 100))
    numberblock_13 = pygame.transform.scale(pygame.image.load('assets/numberblock_13.png'), (207, 300))
    numberblock_10 = pygame.transform.scale(pygame.image.load('assets/numberblock_10.png'), (183, 250))
    numberblock_3 = pygame.transform.scale(pygame.image.load('assets/numberblock_3.png'), (117, 250))
    easter_bunny = pygame.transform.scale(pygame.image.load('assets/easter_bunny.png'), (300, 330))
    font = pygame.font.SysFont('Sans', 32)

    little_font = pygame.font.SysFont('Sans', 16)
    big_font = pygame.font.SysFont('Sans', 42)
    beep_sound = pygame.mixer.Sound("assets/beep.wav")

    night_time_bg = pygame.image.load('assets/bg.png')
    day_time_bg = pygame.image.load('assets/bg-day.png')

    dir_l = pygame.image.load('assets/l.png')
    dir_r = pygame.image.load('assets/r.png')
    dir_d = pygame.image.load('assets/d.png')
    dir_ld = pygame.image.load('assets/ld.png')
    dir_rd = pygame.image.load('assets/rd.png')
    handicap_button_pressed = pygame.transform.scale(pygame.image.load('assets/handicap_button_mode_off.png'),
                                                     (300, 300))
    handicap_button_on = pygame.transform.scale(pygame.image.load('assets/handicap_button_mode_on.png'), (300, 300))
    handicap_button_off = pygame.transform.scale(pygame.image.load('assets/handicap_button_mode_off.png'), (300, 300))

    about_button_pressed = pygame.transform.scale(pygame.image.load('assets/about_button_pressed.png'), (60, 60))
    about_button_unpressed = pygame.transform.scale(pygame.image.load('assets/about_button_unpressed.png'), (60, 60))

    button_lightning_pressed = pygame.transform.scale(pygame.image.load('assets/lightning.png'), (60, 60))
    button_lightning_unpressed = pygame.transform.scale(pygame.image.load('assets/lightning.png'), (60, 60))

    button_calc_pressed = pygame.transform.scale(pygame.image.load('assets/hp_pressed.png'), (60, 60))
    button_calc_unpressed = pygame.transform.scale(pygame.image.load('assets/hp_unpressed.jpg'), (60, 60))

    keypad_sounds = {
        '0': pygame.mixer.Sound('assets/0.wav'),
        '1': pygame.mixer.Sound('assets/1.wav'),
        '2': pygame.mixer.Sound('assets/2.wav'),
        '3': pygame.mixer.Sound('assets/3.wav'),
        '4': pygame.mixer.Sound('assets/4.wav'),
        '5': pygame.mixer.Sound('assets/5.wav'),
        '6': pygame.mixer.Sound('assets/6.wav'),
        '7': pygame.mixer.Sound('assets/7.wav'),
        '8': pygame.mixer.Sound('assets/8.wav'),
        '9': pygame.mixer.Sound('assets/9.wav')
    }

    floor_sounds = {str(floor_number): pygame.mixer.Sound('assets/' + str(floor_number) + '.wav') for floor_number in
                    range(0, 40 + 1)}

    minus_sound = pygame.mixer.Sound('assets/minus.wav')

    car_sounds = {chr(id): pygame.mixer.Sound('assets/' + chr(id) + '.wav') for id in range(ord('A'), ord('Z') + 1)}

    proceed_to_car_sound = pygame.mixer.Sound('assets/Proceed_to_car.wav')

    floor_sound = pygame.mixer.Sound('assets/Floor.wav')

    to_the_left_sound = pygame.mixer.Sound('assets/To_the_left.wav')
    to_the_right_sound = pygame.mixer.Sound('assets/To_the_right.wav')
    to_the_back_sound = pygame.mixer.Sound('assets/To_the_back.wav')
    to_the_back_left_sound = pygame.mixer.Sound('assets/To_the_back_left.wav')
    to_the_back_right_sound = pygame.mixer.Sound('assets/To_the_back_right.wav')

    elevator_sound = pygame.mixer.Sound('assets/Elevator.wav')
    has_arrived_sound = pygame.mixer.Sound('assets/Has_arrived.wav')
    lightning_strike_sound = pygame.mixer.Sound('assets/lightning.wav')
    entry_not_understood_sound = pygame.mixer.Sound('assets/Entry_not_understood.wav')
    floor_not_available_sound = pygame.mixer.Sound('assets/Floor_not_available.wav')
    floor_13_error_sound = pygame.mixer.Sound('assets/Unlucky_floor_13_who_said_that.wav')
    floor_minus_13_error_sound = pygame.mixer.Sound('assets/Unlucky_floor_minus_13_who_said_that.wav')
    lightning_mode_step_number_line = little_font.render("Step Number", True, (255, 255, 255))

    @classmethod
    def make_calc_asset(cls, asset_path):
        surf = pygame.image.load(asset_path)
        max_width = 800
        max_height = 450
        best_ratio = min(max_width / surf.get_width(), max_height / surf.get_height())
        w = best_ratio * surf.get_width()
        h = best_ratio * surf.get_height()
        print(f'w={w}, h={h}, img={asset_path}')
        return pygame.transform.scale(surf, (w, h))

    @classmethod
    def handicap_sound_for_button(cls, button_id):
        return Assets.keypad_sounds.get(button_id)
