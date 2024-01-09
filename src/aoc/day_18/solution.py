#!/usr/bin/env python

# # #
#
# TODO
# 1) write docstrings for --eplain

import os
from typing import Dict, List, Tuple

from aoc import utils
from aoc.utils import dprint

from . import solution_v1
from .common import (DiggingInstruction, convert_digging_instructions,
                     measure_field)

DAY = '18'
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
    return utils.load_input(fname, line_parser=DiggingInstruction.from_text)


def solve_p1(instructions: List[DiggingInstruction]) -> int:
    """Solution to the 1st part of the challenge"""
    return solution_v1.solve_p1(instructions)
    #return solution_v2.solve_p1(instructions)


def solve_p2(instructions: List[DiggingInstruction]) -> int:
    """Solution to the 2nd part of the challenge

    Using shoelace algorithm
    https://www.101computing.net/the-shoelace-algorithm/
    """
    instructions = convert_digging_instructions(instructions)
    size, start = measure_field(instructions)
    dprint(f"Field size = {size}, start at {start}")

    corners = [start]
    for idx, inst in enumerate(instructions):
        dprint(idx, inst)
        corners.append(corners[-1] + inst)
        dprint(f"..new corner: {corners[-1]}")
    # if corners[0] == corners[-1]:
    #     print(f"Loop! Start and end point match: {corners[-1]}")

    # for shoelace algorithm, arrange the corners anticlockwise
    corners = list(reversed(corners))

    area = sum([
        a.x * b.y - b.x * a.y
        for a, b in zip(corners[:-1], corners[1:])
    ]) / 2

    # add area of the contour trench itself
    area += sum([inst.length for inst in instructions]) / 2
    area += 1  # area of the starting point

    return int(area)


tests = [
    (load_input('test.1.txt'), 62, 952408144115),
]


reals = [
    (load_input(), 47139, 173152345887206)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
