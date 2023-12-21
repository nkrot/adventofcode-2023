#!/usr/bin/env python

# # #
#
#

import os
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

from aoc import Direction, Matrix, Point, utils
from aoc.utils import dprint

DAY = '16'
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
    return utils.load_input(fname, parser=parse)


@dataclass
class Tile:
    sign: str
    energy: int = 0
    visited_sides: Set = field(default_factory=set)

    def meets(self, beam: 'Beam') -> bool:
        """Update the state of the Tile as a reaction to a beam entering
        the tile.
        Return boolean indicating whether the tile was already visited by
        a beams coming from the same side.
        """
        self.energy += 1
        before = len(self.visited_sides)
        self.visited_sides.add(str(beam.direction))
        return before == len(self.visited_sides)

    def __str__(self):
        return self.sign

    def reset(self):
        """Reset the tile to the original state."""
        self.energy = 0
        self.visited_sides.clear()


def show_energies(src: Matrix):
    if DEBUG:
        tiles = deepcopy(src)
        for xy, tile in tiles:
            tiles[xy] = "#" if tile.energy else '.'
        dprint(str(tiles))


class Beam:

    def __init__(self, start: Tuple[int, int], direction: str = ">"):
        self.origin = Point(start)
        self.head: Point = self.origin
        self.direction = Direction(direction)

    def meets(self, tile: Tile) -> Optional['Beam']:
        """Update the Beam state (in place) as a reaction to hitting a Tile.

        In case a Beam is split, return the other Beam.
        Otherwise, return None.
        """
        _tile = str(tile)
        _dir = str(self.direction)

        # Light beam goes through w/o changing direction
        # if _tile == '.':
        #     return
        # if _tile == '-' and _dir in {'<', '>'}:
        #     return
        # if _tile == '|' and _dir in {'^', 'v'}:
        #     return

        # Light beam refects 90 degrees
        if _dir in {'<', '>'}:
            if _tile == '/':
                self.direction.ccw()
            if _tile == '\\':
                self.direction.cw()
        if _dir in {'^', 'v'}:
            if _tile == '/':
                self.direction.cw()
            if _tile == '\\':
                self.direction.ccw()

        # Light beam splits into two, each 90 degrees
        if (_dir in {'<', '>'} and _tile == '|'
            or _dir in {'^', 'v'} and _tile == '-'
        ):
            other = deepcopy(self)
            self.direction.cw()
            other.direction.ccw()
            return other

    def advance(self):
        """Advance the current Beam by one step."""
        self.head += self.direction
        return self

    def __repr__(self):
        return "<{}: head={} direction='{}'>".format(
            self.__class__.__name__,
            self.head,
            self.direction,
            # self.origin
        )


def parse(lines: List[str]) -> Matrix:
    """Parse a line of input into suitable data structure"""
    tiles = [
        [Tile(ch) for ch in line]
        for line in lines
    ]
    return Matrix(tiles)


def solve(tiles: Matrix, beam: Beam) -> int:
    """Solve the task for one beam"""
    beams = [beam]
    while beams:
        beam = beams.pop(0)
        tile = tiles.get(beam.head)
        dprint("Beam x Tile:", repr(beam), repr(tile))

        if not tile:
            # light falls off the edge of the contraption
            continue

        if tile.meets(beam):
            # If the tile was previously visited from the same side,
            # it does not make sense continuing with the beam because
            # it will repeat the same path as the previous beam.
            continue

        spinoff = beam.meets(tile)

        beams.append(beam.advance())
        if spinoff:
            beams.append(spinoff.advance())

    show_energies(tiles)
    # print(repr(tiles))

    return len([1 for _, t in tiles if t.energy])


def solve_p1(tiles: Matrix) -> int:
    """Solution to the 1st part of the challenge"""
    return solve(tiles, Beam((0, 0), ">"))


def solve_p2(tiles: Matrix) -> int:
    """Solution to the 2nd part of the challenge"""
    n_rows, n_cols = tiles.shape()

    def reset(tiles):
        """Reset tiles. This is faster than making a deep copy of tiles"""
        for _, tile in tiles:
            tile.reset()

    beams = []

    for r in range(n_rows):
        beams.append(Beam((r, 0), ">"))
        beams.append(Beam((r, n_cols-1), "<"))

    for c in range(n_cols):
        beams.append(Beam((0, c), "v"))
        beams.append(Beam((n_rows-1, c), "^"))

    energies = []
    for beam in beams:
        energies.append(solve(tiles, beam))
        reset(tiles)
        dprint(beam, energies[-1])

    return max(energies)


tests = [
    (load_input('test.1.txt'), 46, 51),
]


reals = [
    (load_input(), 6855, 7513)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
