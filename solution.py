#!/usr/bin/env python

# # #
#
#

import re
import os
import sys
from typing import List
from dataclasses import dataclass

from aoc.utils import load_input, run_tests, run_real, to_numbers

DAY = 'DD'  # TODO
DEBUG = int(os.environ.get('DEBUG', 0))


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


tests = [
    # (load_input('test.1.txt', line_parser=parse), exp1, None),
    # TODO
]


reals = [
    # (load_input(line_parser=parse), None, None)
]


if __name__ == '__main__':
    run_tests(DAY, tests, solve_p1, solve_p2)
    # run_real(DAY, reals, solve_p1, solve_p2)
