#!/usr/bin/env python

# # #
#
#

import re
import os
import sys
from typing import List, Tuple, Dict
from dataclasses import dataclass

from aoc.utils import load_input, run_tests, run_real, Point, prod

DAY = '03'
DEBUG = int(os.environ.get('DEBUG', 0))


@dataclass
class PartNumber:
    # position: Tuple[int, int, int] # x, starty, endy
    value: int
    valid: bool = False

    def __hash__(self):  # set() wants objects to be hashable
        return hash(id(self))


def parse(lines: List[str]) -> Tuple[Dict[Point, PartNumber], Dict[Point, str]]:
    """Parse lines of input into suitable data structure.

    Returns:
      numbers (Dict[Point, PartNumber])
      symbols (Dict[Point, str])

    """
    numbers, symbols = {}, {}

    for i, line in enumerate(lines):
        # parse part numbers
        for m in re.finditer(r'(\d+)', line):
            part_number = PartNumber(
                # position=(i, m.start(), m.end()),  # useless
                value=int(m[0])
            )
            for j in range(m.start(), m.end()):
                numbers[Point(i,j)] = part_number
        # parse symbols
        for m in re.finditer(r'([^\d.])', line):
            symbols[Point(i, m.start())] = m[0]

    if DEBUG:
        print(f"numbers:\n{numbers}")
        print(f"symbols:\n{symbols}")

    return numbers, symbols


def solve_p1(args: Tuple[dict, dict]) -> int:
    """Solution to the 1st part of the challenge"""
    part_numbers: Dict[Point, int] = args[0]
    symbols: Dict[Point, str] = args[1]

    # Determine which part numbers are valid part numbers by checking
    # if there is a symbol adjacent to it in 8 directions and mark such
    # part numbers as valid.
    for pt, _ in symbols.items():
        for npt in pt.around8():
            if npt in part_numbers:
                part_numbers[npt].valid = True

    total = 0
    for part_number in set(part_numbers.values()):
        if part_number.valid:
            total += part_number.value

    return total


def solve_p2(args) -> int:
    """Solution to the 2nd part of the challenge"""
    part_numbers: Dict[Point, int] = args[0]
    symbols: Dict[Point, str] = args[1]
    total_gear_ratio = 0

    # keep * only in symbols, these are indicators of gears.
    symbols = [pt for pt, value in symbols.items() if value == '*']

    for pt in symbols:
        # if symbol * is adjacent to exacly two part numbers, the latter
        # are gears. find such part numbers (gears).
        gears = set()
        for npt in pt.around8():
            if npt in part_numbers:
                gears.add(part_numbers[npt])
        if len(gears) == 2:
            gear_ratio = prod([g.value for g in gears])
            total_gear_ratio += gear_ratio

    return total_gear_ratio


tests = [
    (load_input('test.1.txt', parser=parse), 4361, 16345+451490),
]


reals = [
    (load_input(parser=parse), 527144, 81463996)
]


if __name__ == '__main__':
    run_tests(DAY, tests, solve_p1, solve_p2)
    run_real(DAY, reals, solve_p1, solve_p2)
