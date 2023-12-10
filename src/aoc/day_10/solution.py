#!/usr/bin/env python

# # #
# TODO:
# 1) study others' solutions. My solution is definitely more complex than
#    necessary.
# 2) is there a way to DRY out visit_all_pipe_tiles() and
#    visit_all_ground_tiles()?
# 3) Use networkx library for graphs?

import os
from typing import List

from aoc import utils, Matrix, Point
from aoc.utils import dprint


DAY = '10'
DEBUG = int(os.environ.get('DEBUG', 0))


class Tile:
    """
    This is a single segment of a Pipe that occupies one tile on the map.

    Position is (x, y) where
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
        self.distance = None  # from the START point

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

    def make_ground(self):
        """Change the tile to be a ground tile"""
        self.shape = "."

    def ends(self) -> List[Point]:
        """List of ends of the pipe"""
        return [
            self.pos + Point(dxy)
            for dxy in self.ENDS[self.shape]
        ]

    def is_connected_to(self, other: 'Tile') -> bool:
        """
        TODO: this will not work for two S-Tiles but they are not possible
        in this task, so we ignore this situation.
        """
        assert isinstance(other, type(self))
        if self.is_ground() or other.is_ground():
            return False
        oks = [
            any(xy == other.pos for xy in self.ends()),
            any(xy == self.pos for xy in other.ends())
        ]
        return all(oks)

    def __str__(self):
        return str(self.shape)

    def __repr__(self):
        return "<{}: {} {} {}>".format(
            self.__class__.__name__, self.shape, self.pos, self.distance)


class StretchTile(Tile):
    pass


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
        print(repr(mtx))
    return mtx


def solve_p1(mtx: Matrix) -> int:
    _, start = mtx.find(lambda t: t.is_start())
    visited_tiles = visit_all_pipe_tiles(mtx, start)
    return max(t.distance for t in visited_tiles)


def solve_p2(mtx: Matrix) -> int:
    """Solution to the 2nd part of the challenge"""
    dprint(f"--- Initial ---\n{mtx.shape()}\n{mtx}")
    erase_tiles_outside_of_loop(mtx)
    stretched_mtx = stretch(mtx)
    # counting before visit_all_ground_tiles() that in debug mode can change
    # visited tiles to appear as * thus making them not ground (.) tiles
    c_ground_tiles = len(stretched_mtx.findall(
        lambda t: type(t) is Tile and t.is_ground()
    ))
    dprint("Total ground tiles", c_ground_tiles)
    visited_tiles = visit_all_ground_tiles(stretched_mtx)
    c_visited_tiles = len([t for t in visited_tiles if type(t) is Tile])
    dprint("Total visited ground tiles", c_visited_tiles)

    return c_ground_tiles - c_visited_tiles


def visit_all_pipe_tiles(mtx: Matrix, start: Tile) -> List[Tile]:
    """Traverse the graph starting at vertex `start`, ignoring Ground tiles.
    Collect tiles that have been visited and set Tile.distance to the value
    of distance between start tile and the current tile.

    Return
    a list of visited tiles
    """
    start.distance = 0
    dprint("Start", repr(start))
    heads = [start]
    visited_tiles = []
    while heads:
        tile = heads.pop(0)
        dprint("Visiting", repr(tile))
        visited_tiles.append(tile)
        for neighbour_pos in tile.ends():
            neighbour_tile = mtx.get(neighbour_pos)
            if (neighbour_tile
                and neighbour_tile not in visited_tiles
                and not neighbour_tile.is_ground()
                and neighbour_tile.is_connected_to(tile)
            ):
                neighbour_tile.distance = tile.distance + 1
                heads.append(neighbour_tile)

    return visited_tiles


def stretch(src_mtx: Matrix) -> Matrix:
    """Stretch given matrix by inserting special StretchTile
    around the matrix and between every two tiles in the matrix.
    """

    # create an empty stretched matrix (aka canvas).
    n_rows, n_cols = src_mtx.shape()
    mtx = Matrix(n_rows*2+1, n_cols*2+2)
    for xy, _ in mtx:
        mtx[xy] = StretchTile(".", xy)

    # Insert source matrix into the stretched matrix, spacing the values
    # as required.
    for src_xy, tile in src_mtx:
        xy = Point(src_xy) * 2 + (1,1)
        mtx[xy] = tile  # tile.pos must remain at original value!

    # Reconnect pipe segments that became interrupted by stretching
    # the matrix. For this, convert some StretchTiles to | or -
    offsets = [
        [(0, -1), (0, 1), "-"],  # to reach tiles in horizontal direction
        [(-1, 0), (1, 0), "|"],  # to reach tiles in vertical direction
    ]
    for xy, tile in mtx.findall(lambda t: type(t) is StretchTile):
        connected = False
        for (pre, post, sign) in offsets:
            if connected:
                break
            pre_tile = mtx.get(Point(xy) + pre)
            post_tile = mtx.get(Point(xy) + post)
            dprint("PreTile", repr(pre_tile))
            dprint("PstTile", repr(post_tile))
            if (pre_tile and post_tile and pre_tile.is_connected_to(post_tile)):
                mtx[xy].shape = sign
                dprint("..connecting", repr(mtx[xy]))
                connected = True

    # Finally, fix Tile.pos to be relative to the stretched matrix
    for xy, tile in mtx.findall(lambda t: type(t) is Tile):
        tile.pos = xy

    #print(f"--- Stretched ---\n{mtx.shape()}\n{repr(mtx)}")
    dprint(f"--- Stretched ---\n{mtx.shape()}\n{mtx}")

    return mtx


def visit_all_ground_tiles(mtx: Matrix):
    dprint("Visiting all ground tiles...")
    _, start = mtx.find(lambda t: t.is_ground())
    dprint("Start", repr(start))
    heads = [start]
    visited_tiles = []  # or set to avoid duplicates
    while heads:
        tile = heads.pop(0)
        visited_tiles.append(tile)
        dprint("Visiting", repr(tile))
        for neighbour_pos in Point.around4(tile.pos):
            neighbour_tile = mtx.get(neighbour_pos)
            if (not neighbour_tile
                or not neighbour_tile.is_ground()
                or neighbour_tile in visited_tiles
            ):
                continue
            if neighbour_tile in heads:
                # since the same vertex can be reachable from all its
                # neighbours, here we ensure that we dont visit the vertex
                # if it is alredy scheduled for visiting
                continue
            heads.append(neighbour_tile)
    if DEBUG:
        # for visualization, mark all visited tiles differently
        # TODO: create a copy for visualization! mutating the original
        # object is a bad idea, cuz Tile.is_ground() is affected.
        for tile in visited_tiles:
            tile.shape = "*"
        print(f"--- Reach all ground tiles ---\n{mtx}")
    return visited_tiles


def erase_tiles_outside_of_loop(mtx: Matrix):
    """Mark all tiles that do not belong to the loop as Ground tiles"""
    dprint("Erasing tiles outside of loop...")
    _, start = mtx.find(lambda t: t.is_start())
    loop_tiles = visit_all_pipe_tiles(mtx, start)
    for _, tile in mtx:
        if tile not in loop_tiles:
            tile.make_ground()
    dprint(f"--- Non-loop tiles removed ---\n{mtx}")


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    return utils.load_input(fname, parser=parse)


tests = [
    # part 1
    (load_input('test.1.txt'), 4, None),
    (load_input('test.2.txt'), 8, None),

    # part 2
    (load_input('test.3.txt'), None, 4),
    (load_input('test.4.txt'), None, 4),
    (load_input('test.5.txt'), None, 8),
    (load_input('test.6.txt'), None, 10),
]


reals = [
    (load_input(), 6768, 351)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
