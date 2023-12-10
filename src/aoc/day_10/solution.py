#!/usr/bin/env python

# # #
#
#

import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple

from aoc import utils, Matrix
# TODO: move Point into into own file
from aoc.utils import dprint, Point


DAY = '10'
DEBUG = int(os.environ.get('DEBUG', 0))

class Tile:
    """
    position is (x, y) where
    x axis goes from top to bottom
    y axis goes from left to right
    """

    ENDS = {
        "-": [(0, -1), (0, 1)],
        "|": [(-1, 0), (1, 0)],
        "L": [(-1, 0), (0, 1)],
        "J": [(-1, 0), (0, -1)],
        "7": [(0, -1), (1, 0)],
        "F": [(0, 1),  (1, 0)],
        ".": [],
        "S": [(-1, 0), (0, 1), (1, 0), (0, -1)]
    }

    def __init__(self, shape: str, pos = None):
        self.shape: str = shape
        self.pos: Point = pos

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, val):
        self._pos = Point(val)

    def is_start(self) -> bool:
        return self.shape == "S"

    def is_ground(self) -> bool:
        return self.shape == "."

    def ends(self) -> List[Point]:
        """List of ends of the pipe"""
        return [
            self.pos + Point(dxy)
            for dxy in self.ENDS[self.shape]
        ]

    def can_connect_to(self, other: 'Tile') -> bool:
        assert isinstance(other, type(self))
        for xy in self.ends():
            if xy == other.pos:
                return True
        return False

    def __repr__(self):
        return "<{}: {} {}>".format(
            self.__class__.__name__, self.shape, self.pos)


def solve_part_1(fname: str):
    res = solve_p1(load_input(fname))
    print(res)


def solve_part_2(fname: str):
    res = solve_p2(load_input(fname))
    print(res)


def parse(lines: List[str]) -> Matrix:
    """Parse lines of input into suitable data structure"""
    tiles = [[Tile(ch) for ch in line]
             for line in lines]
    mtx = Matrix(tiles)
    for xy, tile in mtx:
        tile.pos = xy
    if DEBUG:
        print(mtx.shape())
        print(mtx)
    return mtx


def solve_p1(mtx: Matrix) -> int:
    """Solution to the 1st part of the challenge"""
    _, tile = mtx.find(lambda t: t.is_start())
    dprint("Start", tile)
    route = [(tile, 0)]
    distances = [0]
    # TODO: do we need to store **all** visited tiles or most recent ones
    # will be enough?
    visited_tiles = [None]
    while route:
        tile, dist = route.pop(0)
        dprint("Step", dist, tile)
        visited_tiles.append(tile)
        for neighbour_pos in tile.ends():
            neighbour_tile = mtx.get(neighbour_pos)

            if neighbour_tile in visited_tiles or neighbour_tile.is_ground():
                continue

            if tile.is_start() and not neighbour_tile.can_connect_to(tile):
                # starting point requires a special check because we dont
                # know its shape: perform a reverse check, that is whether
                # the neighbouring tile can connect to the starting point.
                continue

            route.append((neighbour_tile, dist+1))
            distances.append(dist+1)

    return max(distances)


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
    (load_input('test.1.txt'), 4, None),
    (load_input('test.2.txt'), 8, None),
    (load_input('test.3.txt'), None, 4),
    (load_input('test.4.txt'), None, 4),
]


reals = [
    (load_input(), 6768, None)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
