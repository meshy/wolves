import random
import time
from functools import partial
from itertools import product

from blessings import Terminal


term = Terminal()

WINDOW_WIDTH = term.width // 2
WINDOW_HEIGHT = term.height - 1

WOLF = 'W'
RABBIT = 'R'
EMPTY = ' '
RABBIT_SURVIVAL = 60
WOLF_SURVIVAL = 80
WOLF_BREED = 80


def random_animal():
    choice = random.randint(0, 10)
    if choice == 0:
        return WOLF
    if choice in (1, 2):
        return RABBIT
    return EMPTY


def random_row():
    return [random_animal() for _ in range(WINDOW_WIDTH)]


def random_board():
    return [random_row() for _ in range(WINDOW_HEIGHT)]


def colour(cell):
    if cell == WOLF:
        return term.red(cell)
    return cell


def print_board(rows):
    rows = map(lambda r: ' '.join(map(colour, r)), rows)
    result = term.move(0, 0) + '\n'.join(rows)
    print(result, flush=True)


def get_neighbours(board, y, x):
    above, below = y - 1, y + 1
    left, right = x - 1, x + 1

    above %= WINDOW_HEIGHT
    below %= WINDOW_HEIGHT

    left %= WINDOW_WIDTH
    right %= WINDOW_WIDTH

    combinations = list(product([above, y, below], [left, x, right]))
    combinations.remove((y, x))

    return [board[Y][X] for Y, X in combinations]


def beside_rabbit(board, y, x):
    return any(filter(lambda cell: cell == RABBIT, get_neighbours(board, y, x)))


def beside_wolf(board, y, x):
    return any(filter(lambda cell: cell == WOLF, get_neighbours(board, y, x)))


def next_animal_state(board, y, x):
    # prey expand into all adjacent cells
    # Includes random death rate, and random breed failure?
    survival_chance = random.randrange(100)
    current_state = board[y][x]
    if current_state == RABBIT:
        if beside_wolf(board, y, x):
            return WOLF if survival_chance < WOLF_BREED else EMPTY
        return RABBIT if survival_chance < RABBIT_SURVIVAL else EMPTY
    if current_state == WOLF and beside_rabbit(board, y, x):
        return WOLF if survival_chance < WOLF_SURVIVAL else EMPTY
    return EMPTY


def next_board(board):
    new_board = []
    # predators breed over adjacent prey or die
    for y in range(WINDOW_HEIGHT):
        new_states = map(partial(next_animal_state, board, y), range(WINDOW_WIDTH))
        new_board.append(''.join(new_states))
    new_rabbit_coords = []
    for y in range(WINDOW_HEIGHT):
        new_rabbits_on_row = []
        for x in range(WINDOW_WIDTH):
            if board[y][x] == EMPTY and beside_rabbit(new_board, y, x):
                new_rabbits_on_row.append((y, x))
        new_rabbit_coords += new_rabbits_on_row
    for y, x in new_rabbit_coords:
        survival_chance = random.randrange(100)
        if survival_chance >= RABBIT_SURVIVAL:
            continue
        row = new_board[y]
        new_board[y] = row[:x] + RABBIT + row[(x + 1):]
    return new_board


def print_totals(board):
    num_wolves = 0
    for row in board:
        num_wolves += row.count(WOLF)

    num_rabbits = 0
    for row in board:
        num_rabbits += row.count(RABBIT)

    info = 'Wolves: {:6d}\tRabbits: {:6d}'.format(num_wolves, num_rabbits)
    print(info, end='')

if __name__ == '__main__':
    original_board = board = random_board()

    print(term.clear)
    with term.fullscreen():
        while True:
            print_board(board)
            print_totals(board)
            time.sleep(.07)

            board = next_board(board)
