#!/usr/bin/env python

# # #
#
#

import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple

from aoc import utils, Matrix, Point
from aoc.utils import dprint, to_numbers


DAY = '11'
DEBUG = int(os.environ.get('DEBUG', 0))


def solve_part_1(fname: str):
    res = solve_p1(load_input(fname))
    print(res)


def solve_part_2(fname: str):
    res = solve_p2(load_input(fname))
    print(res)


def parse(lines: List[str]) -> Matrix:
    """Parse a line of input into suitable data structure:
    """
    rows = []
    for line in lines:
        rows.append(list(line))
    mtx = Matrix(rows)
    dprint(f"--- Initial ---\n{mtx.shape()}\n{mtx}")
    return mtx


def stretch_vertically(mtx: Matrix) -> Matrix:
    rows = []
    for row in mtx.rows():
        rows.append(row)
        if all(space == '.' for space in row):
            rows.append(['.']*len(row))
    m = Matrix(rows)
    #dprint(f"--- Expanded ---\n{m.shape()}\n{m}")
    return m


def stretch(mtx: Matrix) -> Matrix:
    m = stretch_vertically(mtx).transpose()
    res = stretch_vertically(m).transpose()
    dprint(f"--- Expanded ---\n{res.shape()}\n{res}")
    return res


def solve_p1(mtx: Matrix) -> int:
    """Solution to the 1st part of the challenge"""
    galaxies = []
    for xy, _ in stretch(mtx).findall(lambda v: v == '#'):
        galaxies.append(Point(xy))
    dprint("Galaxy coordinates", galaxies)
    distances = []
    for i in range(len(galaxies)):
        for j in range(i+1, len(galaxies)):
            distances.append(galaxies[i].l1_dist(galaxies[j]))
    return sum(distances)


def solve_p2(lines: List[str]) -> int:
    """Solution to the 2nd part of the challenge"""
    return 0


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    return utils.load_input(fname, parser=parse)


tests = [
    (load_input('test.1.txt'), 374, None),
]


reals = [
    (load_input(), 9723824, None)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
