#!/usr/bin/env python

# # #
#
#

import re
import os
import sys
from typing import List, Dict, Tuple
from dataclasses import dataclass

from aoc import utils
from aoc.utils import dprint, to_numbers


DAY = 'DD'  # TODO
DEBUG = int(os.environ.get('DEBUG', 0))


def solve_part_1(fname: str):
    res = solve_p1(load_input(fname))
    print(res)


def solve_part_2(fname: str):
    res = solve_p2(load_input(fname))
    print(res)


def parse(line: str) -> str:
    """Parse a line of input into suitable data structure:
    """
    # TODO: implement or delete if no transformation is needed
    return line


def solve_p1(lines: List[str]) -> int:
    """Solution to the 1st part of the challenge"""
    return 0


def solve_p2(lines: List[str]) -> int:
    """Solution to the 2nd part of the challenge"""
    return 0


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    # TODO: fix loading parameters if necessary
    return utils.load_input(fname, line_parser=parse)


tests = [
    # (load_input('test.1.txt'), exp1, None),
    # TODO
]


reals = [
    # (load_input(), None, None)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
