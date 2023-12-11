#!/usr/bin/env python

# # #
#
#

import math
import os
import re
from functools import reduce
from pprint import pprint
from typing import Callable, Dict, List, Tuple

from aoc import utils
from aoc.utils import dprint

DAY = '08'
DEBUG = int(os.environ.get('DEBUG', 0))


def solve_part_1(fname: str):
    res = solve_p1(load_input(fname))
    print(res)


def solve_part_2(fname: str):
    res = solve_p2(load_input(fname))
    print(res)


class LRI:
    """Left-Right Instruction"""
    def __init__(self, text: str):
        self.tape = text
        self.pos = 0

    def reset(self):
        self.pos = 0
        return self

    def __iter__(self):
        return self

    def __next__(self):
        val = 0 if self.tape[self.pos] == 'L' else 1
        self.pos = (self.pos + 1) % len(self.tape)
        return val


def parse(lines: List[str]) -> Tuple[LRI, Dict[str, Tuple[str, str]]]:
    """Parse all lines of input into suitable data structure"""
    lri = LRI(lines.pop(0))
    steps = {}
    while lines:
        ln = lines.pop(0)
        if ln:
            src, l, r = re.sub(r'[=,()]', '', ln).split()
            steps[src] = (l, r)
    return lri, steps


def find_exit(
    location: str,
    maps: Dict[str, Tuple[str, str]],
    lri: LRI,
    end_reached: Callable
) -> int:
    """
    Calculate how many steps it takes to reach the endpoint starting
    from given start `location` following the `maps`
    """
    dprint(f"From:\t{location}")

    for c_steps, i in enumerate(lri):
        location = maps[location][i]
        if end_reached(location):
            break

    dprint(f"..Reached {location} in {1+c_steps}")

    return c_steps+1


def solve_p1(args) -> int:
    """Solution to the 1st part of the challenge"""
    lri, maps = args
    return find_exit('AAA', maps, lri, lambda loc: loc == 'ZZZ')


def solve_p2(args) -> int:
    lri, maps = args

    # starting points: all nodes ending with A
    locations = [src for src in maps.keys() if src[-1] == 'A']

    if DEBUG:
        pprint(maps)
        print(locations)

    # how long does it take to reach the end location from every
    # starting point?
    distances = [
        find_exit(loc, maps, lri.reset(), lambda loc: loc[-1] == 'Z')
        for loc in locations
    ]

    # looking at paths as periodic functions with frequencies equal to
    # corresponding value from distances, how long does it take before
    # all functions converge at a single point? (Least common multiple)
    return lcm(distances)


def lcm(numbers: List[int]):
    """Find least common multiple for a list of integers"""
    # works for python 3.9+
    # return math.lcm(*distances)

    # my own super slow implementation
    #return lcm_stupid_way(distances)

    return reduce(lambda x, y: (x*y) // math.gcd(x, y), numbers)


def lcm_stupid_way(numbers) -> int:
    """Find the least common multiple"""
    largest = max(numbers)

    c_cycles = 0
    while True:
        c_cycles += 1
        goal = largest * c_cycles
        if all(goal % n == 0 for n in numbers):
            break

    return goal


def solve_p1_v1(args) -> int:
    """Solution to the 1st part of the challenge before refactoring"""
    for c_steps, i in enumerate(lri):
        location = maps[location][i]
        if location == 'ZZZ':
            break
    return c_steps+1


def solve_p2_v1(args) -> int:
    """This may be a valid solution.
    It runs so long that I could not wait until it finishes.
    """
    lri, maps = args

    # starting points: all nodes ending with A
    locations = [src for src in maps.keys() if src[-1] == 'A']

    if DEBUG:
        pprint(maps)
        print(locations)

    for c_steps, inst in enumerate(lri):
        dprint("\nStep", c_steps)
        dprint("L/R", inst)
        dprint(f"From:\t{locations}")

        locations = [maps[loc][inst] for loc in locations]

        dprint(f"To:\t{locations}")

        # end point(s) reached?
        if all(loc[-1] == 'Z' for loc in locations):
            dprint("--> Solution found!")
            break

    return c_steps + 1


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    return utils.load_input(fname, parser=parse)


tests = [
     (load_input('test.1.txt'), 2, None),
     (load_input('test.2.txt'), 6, None),
     (load_input('test.3.txt'), None, 6),
]


reals = [
    (load_input(), 20221, 14616363770447)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
