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


class Galaxy(Point):
    pass


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

def compute_distances(galaxies: List[Point]) -> List[int]:
    distances = []
    for i in range(len(galaxies)):
        for j in range(i+1, len(galaxies)):
            distances.append(galaxies[i].l1_dist(galaxies[j]))
    return distances

def solve_p1(args) -> int:
    """Solution to the 1st part of the challenge"""
    mtx, _ = args
    galaxies = []
    for xy, _ in stretch(mtx).findall(lambda v: v == '#'):
        galaxies.append(Point(xy))
    dprint("Galaxy coordinates", galaxies)
    return sum(compute_distances(galaxies))


def solve_p2(args) -> int:
    """Solution to the 2nd part of the challenge"""
    mtx, expansion_coefficient = args

    galaxies = []
    for xy, value in mtx:
        if value == "#":
            galaxies.append(Galaxy(*xy))
    dprint("Galaxies 0", galaxies)

    maxx, maxy = Point(mtx.shape()) - (1,1)
    for x, row in enumerate(reversed(mtx.rows())):
        if all(s == "." for s in row):
            expand_universe(galaxies, (maxx-x, None) , expansion_coefficient-1)
    dprint("Galaxies x", galaxies)

    for y, column in enumerate(reversed(mtx.columns())):
        if all(s == "." for s in column):
            expand_universe(galaxies, (None, maxy-y) , expansion_coefficient-1)
    dprint("Galaxies y", galaxies)

    return sum(compute_distances(galaxies))


def expand_universe(galaxies, xy, coefficient):
    x, y = xy
    for g in galaxies:
        if x is not None and g.x > x:
            g.x += coefficient
        if y is not None and g.y > y:
            g.y += coefficient


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    return utils.load_input(fname, parser=parse)


tests = [
    ((load_input('test.1.txt'), 1), 374, None),

    # part 2
    ((load_input('test.1.txt'), 2), None, 374),
    ((load_input('test.1.txt'), 10), None, 1030),
    ((load_input('test.1.txt'), 100), None, 8410),
]


reals = [
    ((load_input(), 1000000), 9723824, 731244261352)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
