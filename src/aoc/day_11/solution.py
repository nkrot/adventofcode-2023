#!/usr/bin/env python

# # #
#
#

import os
import re
import sys
import itertools
from typing import Dict, List, Tuple

from aoc import utils, Matrix, Point
from aoc.utils import dprint, to_numbers


DAY = '11'
DEBUG = int(os.environ.get('DEBUG', 0))


class Galaxy(Point):
    """For better naming"""
    pass


def solve_part_1(fname: str):
    res = solve_p1((load_input(fname), None))
    print(res)


def solve_part_2(fname: str):
    res = solve_p2((load_input(fname), None))
    print(res)


def parse(lines: List[str]) -> Matrix:
    """Parse a line of input into suitable data structure"""
    rows = []
    for line in lines:
        rows.append(list(line))
    mtx = Matrix(rows)
    dprint(f"--- Initial ---\n{mtx.shape()}\n{mtx}")
    return mtx


def stretch_vertically(mtx: Matrix) -> Matrix:
    """part of solve_p1_v1"""
    rows = []
    for row in mtx.rows():
        rows.append(row)
        if all(space == '.' for space in row):
            rows.append(['.']*len(row))
    m = Matrix(rows)
    #dprint(f"--- Expanded ---\n{m.shape()}\n{m}")
    return m


def stretch(mtx: Matrix) -> Matrix:
    """part of solve_p1_v1"""
    m = stretch_vertically(mtx).transpose()
    res = stretch_vertically(m).transpose()
    dprint(f"--- Expanded ---\n{res.shape()}\n{res}")
    return res


def compute_distances(galaxies: List[Point]) -> List[int]:
    """Given a list of Points, compute distances between every two points
    and return the distances as a list
    """

    # original implementation
    # distances = []
    # for i in range(len(galaxies)):
    #     for j in range(i+1, len(galaxies)):
    #         distances.append(galaxies[i].l1_dist(galaxies[j]))

    distances = [
        g1.l1_dist(g2)
        for g1, g2 in itertools.combinations(galaxies, 2)
    ]

    return distances


def solve_p1(args) -> int:
    # return solve_p1_v1(args)
    return solve_p1_v2(args)


def solve_p1_v1(args) -> int:
    """Solution to the 1st part of the challenge, before implementing part 2
    """
    universe: Matrix = stretch(args[0])
    galaxies = [
        Point(xy)
        for xy, _ in universe.findall(lambda v: v == '#')
    ]
    dprint("Galaxy coordinates", galaxies)
    return sum(compute_distances(galaxies))


def solve_p1_v2(args) -> int:
    """Solution to the 1st part of the challenge based on the algorithm
    from the 2nd part.
    """
    return solve_p2((args[0], 2))


def solve_p2(args) -> int:
    """Solution to the 2nd part of the challenge"""
    mtx = args[0]
    expansion_coefficient = args[1] or 1000000  # real value for p2

    galaxies = [
        Galaxy(*xy)
        for xy, value in mtx if value == "#"
    ]
    dprint("Galaxies 0", galaxies)

    # Expand the universe: recompute coordinates of each galaxy.
    # The coordinates are (x, y) where:
    # - x is vertical dimension going topdown
    # - y is a horizontal dimension going from left to right
    # We do it starting from the outermost edge:
    # - for x (vertical) dimension, from bottom to top
    # - for y (horizontal) dimension, from right to left.
    # Doing it in natural (topdown, left to right) form leads to overcounts:
    # some galaxies get changed more than once because their new coordinate
    # places them once again in the reach of expansion process.

    maxx, maxy = Point(mtx.shape()) - (1,1)
    for x, row in enumerate(reversed(mtx.rows())):
        if all(s == "." for s in row):
            move_galaxies(galaxies, (maxx-x, None) , expansion_coefficient)
    dprint("Galaxies x", galaxies)

    for y, column in enumerate(reversed(mtx.columns())):
        if all(s == "." for s in column):
            move_galaxies(galaxies, (None, maxy-y) , expansion_coefficient)
    dprint("Galaxies y", galaxies)

    return sum(compute_distances(galaxies))


def move_galaxies(
    galaxies: List[Galaxy],
    reference_xy: Tuple[int, int],
    coefficient: int
):
    x, y = reference_xy
    for glx in galaxies:
        if x is not None and glx.x > x:
            glx.x += (coefficient - 1)
        if y is not None and glx.y > y:
            glx.y += (coefficient - 1)

    # Ideas for overengineering:
    # `coefficient` could be a pair [alongX, alongY], one of the values
    # being 1. Then, we can do the following
    # g += Point(*coefficient) - Point(1,1)
    # to update both coordinates at the same time.
    # The value of 1 will ensure that irrelevant coordinate is not affected.


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    return utils.load_input(fname, parser=parse)


tests = [
    # part 1
    ((load_input('test.1.txt'), None), 374, None),

    # part 2
    ((load_input('test.1.txt'), 2), None, 374),
    ((load_input('test.1.txt'), 10), None, 1030),
    ((load_input('test.1.txt'), 100), None, 8410),
]


reals = [
    ((load_input(), 1_000_000), 9723824, 731244261352)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
