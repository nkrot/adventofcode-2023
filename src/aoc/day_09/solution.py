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

DAY = '09'
DEBUG = int(os.environ.get('DEBUG', 0))


def solve_part_1(fname: str):
    #print(f"Part 1 for file {fname}")
    res = solve_p1(load_input(fname))
    print(res)


def solve_part_2(fname: str):
    #print(f"Part 2 for file {fname}")
    res = solve_p2(load_input(fname))
    print(res)


def parse(line: str) -> List[int]:
    return to_numbers(line.split())


def extrapolate(numbers: List[int], level=0) -> Tuple[int]:
    """
    Extrapolate given sequence of numbers to the left and to the right.

    Returns two numbers, the first one being extrapolation to the left
    and the second an extrapolation to the right.
    """

    indent = '  ' * level
    dprint(f"{indent}Input:   {numbers}")

    if all(n == 0 for n in numbers):
        return (0, 0)

    reduced = [numbers[i] - numbers[i-1] for i in range(1, len(numbers))]
    dprint(f"{indent}Reduced: {reduced}")

    # alternative way of generating pairs of (previous, next) numbers
    # for p, n in zip(numbers[0:-1], numbers[1:])

    extras = extrapolate(reduced, level+1)
    dprint(f"{indent}extras: {extras}")

    return (numbers[0]-extras[0], numbers[-1] + extras[1])


def solve_p1(reports: List[int]) -> int:
    """Solution to the 1st part of the challenge"""
    return sum(extrapolate(report)[1] for report in reports)


def solve_p2(reports: List[int]) -> int:
    """Solution to the 2nd part of the challenge"""
    return sum(extrapolate(report)[0] for report in reports)


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    return utils.load_input(fname, line_parser=parse)


tests = [
    (load_input('test.1.txt'), 18+28+68, -3+0+5),
]


reals = [
    (load_input(), 1980437560, 977)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
