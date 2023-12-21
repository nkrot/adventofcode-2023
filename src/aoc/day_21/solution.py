#!/usr/bin/env python

# # #
#
#

import os
from typing import Callable, Dict, List, Tuple

from aoc import Matrix, Point, utils
from aoc.utils import dprint, is_odd, is_even

DAY = '21'
DEBUG = int(os.environ.get('DEBUG', 0))


def solve_part_1(fname: str):
    res = solve_p1(load_input(fname))
    print(res)


def solve_part_2(fname: str):
    res = solve_p2(load_input(fname))
    print(res)


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    return utils.load_input(fname, parser=parse)


def parse(lines: List[str]) -> Tuple[Matrix, Point]:
    """Parse a line of input into suitable data structure:

    # is a rock (non walkable)
    . is garden plot (walkable)
    S is starting point of the elf
    """
    lines = [list(line) for line in lines]
    garden = Matrix(lines)
    start, _ = garden.find(lambda t: t == 'S')
    garden[start] = "."
    dprint(garden)
    dprint("Start at", start)
    return garden, Point(start)


def walk(
    garden: Matrix,
    start: Point,
    max_steps: int = None,
    initial_distance: int = 0
):
    """Traverse the garden (Matrix) from the starting point in all directions
    computing and recording distances of each step to the start.
    Said distances are stored in Garden matrix.
    The starting point is assigned the distance value of 0.

    If max_steps is given, walk at most this number of steps.
    """
    garden[start] = initial_distance
    locations = [start]
    c_steps = 0
    while True:
        c_steps += 1
        for _ in range(len(locations)):
            start = locations.pop(0)
            dist = garden[start]
            for loc in start.around4():
                step = garden.get(loc, '#')
                dprint(loc, step)
                if step == '.':
                    garden[loc] = dist+1
                    locations.append(loc)
        if max_steps is not None and max_steps == c_steps:
            break
        if not locations:
            break

def solve_p1(args) -> int:
    """Solution to the 1st part of the challenge

    Algorithm:
    Given a garden plan (garden: Matrix), use BFS to find all locations that
    can be reached with at most given number of steps (max_steps: int) from
    the starting location (start: Point).
    Select only those locations that are even, because max_steps is even,
    """
    (garden, start), max_steps = args
    walk(garden, start, max_steps)
    dprint(f"--- Distances ---\n{garden}")

    is_same_parity = is_even if is_even(max_steps) else is_odd
    locations = garden.findall(
        lambda dist: (isinstance(dist, int) and 0 <= dist <= max_steps
                      and is_same_parity(dist))
    )
    dprint(len(locations), locations)

    return len(locations)


class EndlessGarden:
    """Stretches automatically as soon as you step outside if its boundaries.

    Delete old plots if they have been explored.

    Since plots repeat, can we avoid exploring them anew but instead reuse
    previously computed ones? this depends on the starting point on a plot.
    If the starting point is the same as before, all distances can be automatically
    adjusted.
    There is not even a need to store a matrix
    """

    def __init__(self, base_plot: Matrix):
        self.base_plot = base_plot

    def get(self, xy):
        """TODO: compute plot number when xy lies, get that plot (creating
        a new on when necessary) and return (pos, value)

        pos should be the original xy, not the one wrt to the current plot?
        can Point have negative coordinates?
        """
        pass

    def findall(self, predicate: Callable):
        pass


def solve_p2(args) -> int:
    """Solution to the 2nd part of the challenge"""
    (garden, start), max_steps = args
    return 0


tests = [
    ((load_input('test.1.txt'), 6), 16, None), # ok

    #((load_input('test.1.txt'), 10), None, 50),
    #((load_input('test.1.txt'), 50), None, 1594),
    #((load_input('test.1.txt'), 100), None, 6536),
    #((load_input('test.1.txt'), 500), None, 167004),
    #((load_input('test.1.txt'), 1000), None, 668697),
    #((load_input('test.1.txt'), 5000), None, 16733044),
]


reals = [
    ((load_input(), 64), 3578, None), # ok
    #((load_input(), 26501365), None, None)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
