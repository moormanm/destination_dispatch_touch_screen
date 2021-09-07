import enum
import itertools
import random
from collections import deque
from dataclasses import dataclass

import pygame
from elements.slidersetter import SliderXSetter
from pygame.rect import Rect
from pygame.surface import Surface
from thorpy import Clickable, Checker

from assets import Assets

YELLOW = (253, 208, 35)


class LightningModeState:
    def tick(self):
        if self.current_step >= self.final_step:
            return False

        self.current_step += 1
        return True

    def __init__(self, columns_count=30, rows_count=20, search_all_paths=False):
        self.rendered_edges = None
        while True:
            self.maze = generate_maze(columns_count, rows_count)
            self.solution, self.end_pos, self.solution_path = solve_maze(self.maze, search_all_paths)
            if not self.solution:
                print("Could not solve.. retrying")
                continue
            break

        self.enable_sound = True
        self.show_numbers = True
        self.show_frontier_lightning = True
        self.show_lightning_strike = True
        self.endRequested = False
        self.current_step = 0
        self.solution_len = self.solution[self.end_pos[1]][self.end_pos[0]]
        self.final_step = calculate_final_step(self)
        self.previous_state = None


@dataclass
class Maze:
    start_pos: (int, int)
    horizontal_edges: []
    vertical_edges: []


def solve_maze(maze, search_all_paths):
    solution = [
        [
            0 for _ in range(len(maze.horizontal_edges[0]))
        ]
        for _ in range(len(maze.vertical_edges))
    ]

    q = deque()
    q.append((maze.start_pos, 1, []))

    solved = False
    solution_path = None
    while q:
        v = q.popleft()
        pos_x = v[0][0]
        pos_y = v[0][1]
        val = v[1]
        previous_coords = list(v[2])

        # out of range x max?
        if pos_x > len(solution[0]) - 1:
            continue

        # out of range y max?
        if pos_y > len(solution) - 1:
            continue

        # visited already?
        if solution[pos_y][pos_x] > 0:
            continue

        solution[pos_y][pos_x] = val
        previous_coords.append(v[0])

        if pos_x == len(solution[0]) - 1 and not solved:
            solved = True
            solution_path = previous_coords
            end_pos = (pos_x, pos_y)
            if not search_all_paths:
                return solution, end_pos, solution_path

        # right
        if pos_x < len(solution[0]) - 1 and maze.vertical_edges[pos_y][pos_x] is False:
            q.append(((pos_x + 1, pos_y), val + 1, previous_coords))

        # up
        if pos_y > 0 and maze.horizontal_edges[pos_y - 1][pos_x] is False:
            q.append(((pos_x, pos_y - 1), val + 1, previous_coords))

        # left
        if pos_x > 0 and maze.vertical_edges[pos_y][pos_x - 1] is False:
            q.append(((pos_x - 1, pos_y), val + 1, previous_coords))

        # down
        if pos_y < len(solution) - 1 and maze.horizontal_edges[pos_y][pos_x] is False:
            q.append(((pos_x, pos_y + 1), val + 1, previous_coords))

    if solved:
        return solution, end_pos, solution_path
    return None, None, None


def generate_maze(columns_count, rows_count):
    p = .5
    q = .3
    choices = [False, True]
    h_weights = [1 - p, p]
    v_weights = [1 - q, q]
    horizontal_edges = [
        [random.choices(choices, h_weights)[0] for _ in range(columns_count)]
        for _ in range(rows_count - 1)
    ]

    vertical_edges = [
        [random.choices(choices, v_weights)[0] for _ in range(columns_count - 1)]
        for _ in range(rows_count)
    ]

    start_pos = (0, random.randint(0, rows_count))

    return Maze(start_pos, horizontal_edges, vertical_edges)


def get_cell_size(solution, display: Surface):
    cells_x_cnt = len(solution[0])
    cells_y_cnt = len(solution)
    return int(display.get_width() / cells_x_cnt), int(display.get_height() / cells_y_cnt)


def render_vertical_edge(display, cell_size, x, y):
    cell_width = cell_size[0]
    cell_height = cell_size[1]
    stroke_width = 2
    start = (x * cell_width, y * cell_height)
    end = (x * cell_width, y * cell_height + cell_height)
    color = (255, 255, 255)
    pygame.draw.line(display, color, start, end, stroke_width)


def render_horizontal_edge(display, cell_size, x, y):
    cell_width = cell_size[0]
    cell_height = cell_size[1]
    stroke_width = 2
    start = (x * cell_width, y * cell_height)
    end = (x * cell_width + cell_width, y * cell_height)
    color = (255, 255, 255)
    pygame.draw.line(display, color, start, end, stroke_width)


def render_edges(state: LightningModeState, display: Surface):
    if state.rendered_edges is not None:
        display.blit(state.rendered_edges, (0, 0))
        return

    target_surface = Surface((display.get_width(), display.get_height()), pygame.SRCALPHA, 32).convert_alpha()

    cell_size = get_cell_size(state.solution, target_surface)

    # draw edge at top
    for i in range(len(state.maze.horizontal_edges[0])):
        render_horizontal_edge(target_surface, cell_size, i, 0)

    # draw edge at bottom
    for i in range(len(state.maze.horizontal_edges[0])):
        render_horizontal_edge(target_surface, cell_size, i, len(state.maze.horizontal_edges) + 1)

    for y in range(len(state.maze.vertical_edges)):
        for x, is_solid in enumerate(state.maze.vertical_edges[y]):
            if is_solid:
                render_vertical_edge(target_surface, cell_size, x + 1, y)

    for y in range(len(state.maze.horizontal_edges)):
        for x, is_solid in enumerate(state.maze.horizontal_edges[y]):
            if is_solid:
                render_horizontal_edge(target_surface, cell_size, x, y + 1)

    state.rendered_edges = target_surface
    display.blit(state.rendered_edges, (0, 0))


def render_background(state, display):
    display.fill((0, 0, 0))


rendered_numbers = {
    val: Assets.little_font.render(str(val), True, (255, 255, 255))
    for val in range(100)
}


def render_number(surface, x_idx, y_idx, cell_size, val):
    text = rendered_numbers.get(val)

    dest_x = cell_size[0] * x_idx
    dest_y = cell_size[1] * y_idx

    x_offset = (cell_size[0] - text.get_width()) // 2
    y_offset = (cell_size[1] - text.get_height()) // 2

    surface.blit(text, (dest_x + x_offset, dest_y + y_offset))


class RenderingStateType(enum.Enum):
    EXPLORING = 1
    BACKTRACKING = 2
    FLASHING = 3


class Transparency(enum.Enum):
    LIGHT = 1
    MEDIUM = 2
    HEAVY = 3


def ceiling_step_for_exploring(lightning_mode_state: LightningModeState):
    return lightning_mode_state.solution_len * 3


def ceiling_step_for_backtracking(lightning_mode_state: LightningModeState):
    return ceiling_step_for_exploring(lightning_mode_state) + lightning_mode_state.solution_len // 3


def rendering_state_of_current_step(lightning_mode_state: LightningModeState):
    ceiling_for_exploring = ceiling_step_for_exploring(lightning_mode_state)

    ceiling_for_backtracking = ceiling_step_for_backtracking(lightning_mode_state)

    if lightning_mode_state.current_step <= ceiling_for_exploring:
        return RenderingStateType.EXPLORING

    if ceiling_for_exploring < lightning_mode_state.current_step <= ceiling_for_backtracking:
        return RenderingStateType.BACKTRACKING

    return RenderingStateType.FLASHING


def render_numbers(lightning_mode_state: LightningModeState, display: Surface):
    cell_size = get_cell_size(lightning_mode_state.solution, display)

    up_to = lightning_mode_state.current_step // 3

    for y in range(len(lightning_mode_state.solution)):
        for x, val in enumerate(lightning_mode_state.solution[y]):
            if 0 < val <= up_to:
                render_number(display, x, y, cell_size, val)


def render_frontier_cell(display, cell_size, x_idx, y_idx, alpha):
    s = pygame.Surface(cell_size)
    s.set_alpha(alpha)
    s.fill(YELLOW)
    display.blit(s, (x_idx * (cell_size[0]), y_idx * (cell_size[1])))


def render_frontier(lightning_mode_state, display):
    cell_size = get_cell_size(lightning_mode_state.solution, display)
    current_max_val = lightning_mode_state.current_step // 3

    current_max_cells = list(filter(lambda item: len(item) > 0, [
        [(x, y) for x, v in enumerate(lightning_mode_state.solution[y]) if v == current_max_val and v != 0]
        for y in range(len(lightning_mode_state.solution))
    ]))
    current_max_cells_flattened = [y for x in current_max_cells for y in x]

    if len(current_max_cells_flattened) == 0:
        return

    def keyfunc(x):
        return x[0]

    max_alpha = 255
    min_alpha = 10
    max_x = max(map(keyfunc, current_max_cells_flattened))

    render_frontier_cell(display, cell_size, lightning_mode_state.solution_path[0][0],
                         lightning_mode_state.solution_path[0][1], 255)

    increment = (max_alpha - min_alpha) // (max_x + 1)
    for cell in current_max_cells_flattened:
        alpha = (cell[0] + 1) * increment
        render_frontier_cell(display, cell_size, cell[0], cell[1], alpha)


def render_from_exploring(lightning_mode_state: LightningModeState, display: Surface):
    render_background(lightning_mode_state, display)

    render_frontier(lightning_mode_state, display)
    if lightning_mode_state.show_numbers:
        render_numbers(lightning_mode_state, display)
    render_edges(lightning_mode_state, display)


def render_from_backtracking(lightning_mode_state: LightningModeState, display: Surface):
    c = lightning_mode_state.end_pos
    s = lightning_mode_state.solution
    cell_size = get_cell_size(s, display)
    render_background(lightning_mode_state, display)

    current_backtracking_step = lightning_mode_state.current_step - ceiling_step_for_exploring(lightning_mode_state)
    up_to_number = lightning_mode_state.solution_len - (current_backtracking_step * 3)

    p = lightning_mode_state.solution_path
    render_frontier_cell(display, cell_size, p[0][0], p[0][1], 255)
    for c in reversed(lightning_mode_state.solution_path):
        v = s[c[1]][c[0]]
        if v < up_to_number:
            break
        render_frontier_cell(display, cell_size, c[0], c[1], 255)
    if lightning_mode_state.show_numbers:
        render_numbers(lightning_mode_state, display)
    render_edges(lightning_mode_state, display)


def render_from_flashing(lightning_mode_state: LightningModeState, display: Surface):
    s = lightning_mode_state.solution
    cell_size = get_cell_size(s, display)
    render_background(lightning_mode_state, display)

    current_flashing_step = lightning_mode_state.current_step - ceiling_step_for_backtracking(lightning_mode_state) - 1

    if current_flashing_step == 0 and lightning_mode_state.enable_sound:
        Assets.lightning_strike_sound.play()

    if current_flashing_step % 2 == 0 or current_flashing_step > 10:
        for c in lightning_mode_state.solution_path:
            render_frontier_cell(display, cell_size, c[0], c[1], 255)

    if lightning_mode_state.show_numbers:
        render_numbers(lightning_mode_state, display)

    render_edges(lightning_mode_state, display)


rendering_state_switch = {
    RenderingStateType.EXPLORING: render_from_exploring,
    RenderingStateType.BACKTRACKING: render_from_backtracking,
    RenderingStateType.FLASHING: render_from_flashing
}


def draw_current_step(lightning_mode_state: LightningModeState, display: Surface):
    rendering_state = rendering_state_of_current_step(lightning_mode_state)
    if lightning_mode_state.previous_state != rendering_state:
        print("Entering " + str(rendering_state))
    lightning_mode_state.previous_state = rendering_state
    rendering_state_switch.get(rendering_state)(lightning_mode_state, display)


def calculate_final_step(state: LightningModeState):
    return ceiling_step_for_backtracking(state) + state.solution_len * 3


class LightningModeWidgets:
    def __init__(self):
        self.lightning_mode_state: LightningModeState = None
        self.pause_play_button: Clickable = None
        self.restart_button: Clickable = None
        self.time_slider: SliderXSetter = None
        self.show_numbers_checkbox: Checker = None
        self.lightning_mode_is_paused = False
        self.quit_button = None
        self.search_all_paths_checkbox: Checker = None
        self.enable_sound_checkbox: Checker = None
        self.static_widgets: [] = None
        self.show_numbers_checkbox = Checker(text="Show numbers", value=False, type_="checkbox")
        self.search_all_paths_checkbox = Checker(text="Search all paths", value=False, type_="checkbox")
        self.enable_sound_checkbox = Checker(text="Enable sound", value=False, type_="checkbox")
        self.static_widgets = [self.show_numbers_checkbox,
                               self.search_all_paths_checkbox,
                               self.enable_sound_checkbox]
