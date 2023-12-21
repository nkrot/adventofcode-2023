#!/usr/bin/env python

# # #
#
#

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
    """Solution to the 2nd part of the challenge"""
    instructions = convert_digging_instructions(instructions)
    print(measure_field(instructions))
    return 0


tests = [
    (load_input('test.1.txt'), 62, 952408144115),
]


reals = [
    (load_input(), 47139, None)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
