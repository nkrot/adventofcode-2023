#!/usr/bin/env python

# # #
#
#

import re
import os
import sys
from typing import List, Callable

from aoc import utils

DAY = '01'
DEBUG = int(os.environ.get('DEBUG', 0))


def solve(lines: List[str], selector: Callable) -> int:
    summa = 0
    for line in lines:
        digits = selector(line)
        summa += digits[0]*10 + digits[-1]
    return summa


def solve_p1(lines: List[str]) -> int:
    """Solution to the 1st part of the challenge"""
    return solve(
        lines,
        lambda ln: [int(ch) for ch in ln if ch.isdigit()]
    )


def solve_p2(lines: List[str]) -> int:
    """Solution to the 2nd part of the challenge"""
    return solve(lines, unspell_and_select_digits)



numbers = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
}

def unspell_and_select_digits(line: str) -> List[int]:
    """
    Recognizes overlapping words too:
    eightwo -> 82
    """
    digits = []
    rgxp = re.compile("|".join(numbers.keys()))
    for start in range(len(line)):
        if line[start].isdigit():
            digits.append(int(line[start]))
        else:
            m = re.match(rgxp, line[start:])
            if m:
                digits.append(numbers[m[0]])
    return digits


tests = [
    (utils.load_input('test.1.txt'), 142, None),
    (utils.load_input('test.2.txt'), None, 281),
]


reals = [
    (utils.load_input(), 54630, 54770)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
