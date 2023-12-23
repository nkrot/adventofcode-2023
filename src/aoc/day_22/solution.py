#!/usr/bin/env python

# # #
#
#

import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import networkx as nx
import numpy as np

from aoc import Point, utils
from aoc.utils import dprint, to_numbers

from .utils import count_descendants

DAY = '22'
DEBUG = int(os.environ.get('DEBUG', 0))
ROTATE = not False  # for debugging


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
    return utils.load_input(fname, line_parser=parse_line, parser=parse)


@dataclass
class Brick:
    """A brick has two Points that denote its ends

    Each point has coordinates (x,y,z) where z is height over the floor
    (called Zearth here).
    """
    start: Point
    end: Point
    id: int = -1

    def __lt__(self, other: 'Brick'):
        """Less than means is closer to Zearth"""
        assert isinstance(other, type(self))
        return self.z <= other.z

    def validate(self):
        """This is my attempt to debug non-working solution"""
        # start coordinates must be less or equal to the end coordinate
        tests = [self.start[axis] <= self.end[axis] for axis in (0,1,2)]
        if not all(tests):
            raise ValueError(repr(self))
        # a brick can be larger than 1 in one dimension only. if it is
        # larger than one in two or more dimensions, error.
        tests = [abs(self.start[axis] - self.end[axis]) > 0
                 for axis in (0,1,2)]
        if tests.count(True) > 1:
            raise ValueError(repr(self))

    @property
    def z(self) -> int:
        """Return z (vertical) coordinate of the brick"""
        return min(self.start.z, self.end.z)

    def __call__(self) -> Tuple[slice]:
        """to be used for indexing numpy ndarray
        numpy.ndarray[brick()]

        TODO: is there a dedicated method that numpy would invoke on an object
        to convert it to a valid indexing object?
        https://stackoverflow.com/questions/55190988/numpy-ndarray-indexing-with-index-method
        """
        # print("Brick.__call__")
        idx = tuple(
            slice(s, e+1)
            for s, e in zip(self.start, self.end)
        )
        # print(f"-> {idx}")
        return idx

    def fall(self, n_steps: int = 1):
        """Brick falls (towards Zearth, along z-axis)"""
        d = (0, 0, n_steps)
        self.start -= d
        self.end -= d
        return self

    def shadow(self):
        """Shadow of a brick is a copy of the brick has the same XY dimensions
        that the brick itself but its z-dimension is 1.

        For the horizontal bricks, their shadow is equal to the original brick.
        The difference is observed by vertical bricks.
        """
        start = Point(self.start)
        end = Point(self.end)
        end.z = start.z
        return type(self)(start, end, -self.id)

    # def __copy__(self):
    #     return type(self)(Point(self.start), Point(self.end), self.id)


def parse_line(line: str) -> Brick:
    """Return a brick (a List of 2 Points)"""
    ends = [
        # tuple(to_numbers(spec.split(',')))
        Point(to_numbers(spec.split(',')))
        for spec in line.split('~')
    ]
    return Brick(*ends)


# < The ground is at z=0 and is perfectly flat; the lowest z value a brick can have is therefore 1.
# TODO: get rid of level 0? this means recomputing z for all bricks z-=1

def parse(bricks: List[List[Point]]) -> Tuple[np.ndarray, List[Brick]]:
    """
    Create a grid (numpy.ndrarray) with all bricks on it.

    >>> np.iinfo(grid.dtype)
    for `int8`:
      min = -128
      max = 127
    for `int16`:
      min = -32768
      max = 32767
    """
    for idx, b in enumerate(bricks):
        b.id = idx + 1
        # b.validate()

    # estimate the shape of the grid, large enough to accomodate all bricks
    shape = [
        1 + max(b.end[axis] for b in bricks)
        for axis in (0, 1, 2)
    ]
    grid = np.zeros(shape, dtype=np.int16)
    #print(grid.dtype, np.iinfo(grid.dtype))

    for brick in bricks:
        #dprint("Brick:", brick)
        grid[brick()] = brick.id

    return grid, bricks


def drop_a_brick(grid, brick, n_steps: int = 1):
    """Move given brick towards Zearth given number of steps"""
    if n_steps > 0:
        dprint(f"Falls {n_steps} steps {brick}")
        grid[brick()] = 0
        brick.fall(n_steps)
        grid[brick()] = brick.id


def fall(grid, bricks):
    """Let all bricks fall towards Zearth"""
    dprint("--- fall ---")

    # Process the bricks in the order: the ones closer to Zearth should be
    # first to fall in order to make space for other bricks.
    for brick in sorted(bricks):
        # How much a brick can fall before it hits Zearth or another brick.
        n_steps = get_z_spacing(grid, brick)
        if n_steps:
            drop_a_brick(grid, brick, n_steps)

    dprint(f"=== fallen ===\n{rotate(grid)}")


def get_z_spacing(grid, brick) -> int:
    """Compute the amount of empty space underneath given brick:
    how far it can move downwards before it collides with another brick
    or Zearth.

    Algorithm:
    Create a shadow of the brick and let it fall step by step.
    At each step we examine the area of the grid within the shadow area.
    If the area is all zeroes, it means it is empty.
    Otherwise, there is another brick.
    """
    n_steps = 0
    shadow = brick.shadow()
    dprint(f"Shadow: {shadow}")
    for n_steps in range(brick.z):
        shadow.fall()
        dprint(f"..{shadow}")
        layer = grid[shadow()]  # 2d
        dprint(f"..area underneath:\n{layer}\n")
        dprint(layer.shape, layer.sum())
        if layer.sum() > 0:
            break
    return n_steps


def get_connections(grid, bricks) -> nx.DiGraph:
    """
    The algorithm is a combination of parts of fall() and get_z_spacing()
    TODO: Can it be dried out?
    """
    dprint("--- get Graph of connections between bricks ---")
    g = nx.DiGraph()
    g.add_nodes_from([brick.id for brick in bricks])

    for brick in sorted(bricks):
        dprint("Inspecting", brick)
        shadow = brick.shadow().fall()
        layer = grid[shadow()]
        dprint("..layer underneath", layer)
        other_bricks = list(filter(None, set(np.unique(layer))))
        dprint(f"..connected bricks: {type(other_bricks)} {other_bricks}")
        for other in other_bricks:
            g.add_edge(other, brick.id)
    dprint(f"Graph: {g}\n{g.nodes()}")

    return g


def validate_graph(g, bricks):
    """Debugging"""
    dprint("--- Validate Graph ---")
    # find all bricks that do not sit on a brick or Zearth
    for v in g.nodes():
        predecessors = list(g.predecessors(v))
        if not predecessors:
            brick = bricks[v-1]
            if brick.z != 1:
                dprint(f"Levitating brick?: {v} {brick}")


def rotate(grid: np.ndarray) -> np.ndarray:
    """Rotate the grid such that
    * z goes from bottom to top
    * x goes from left to right

    Return
    a copy of the original grid rotated
    """
    if ROTATE:
        r1 = np.rot90(grid, 1, (1,2)) # z goes from bottom to top
        r2 = np.rot90(r1, 1, (0,2))   # x goes from left to right
        return r2
    else:
        return grid


def can_be_removed(g: nx.DiGraph, vertex: int) -> bool:
    """Check if the brick `vertex` can be removed without causing
    the structure to fall. The structure will fall if the current brick
    is the only brick supporting it.

    Algorithm
    Our structure is given as Directed Graph where
    * vertices are bricks and
    * a directed edge exists between every pair of supporting and supported
      bricks.
    A brick can be removed if it supports a brick (or several bricks) that
    are supported by other bricks.
    """
    for u in g.successors(vertex):
        predecessors = set(g.predecessors(u)) - {vertex}
        dprint(f"{vertex} -> {u} <- {predecessors}")
        if not predecessors:
            dprint(f"=> {vertex} cannot be removed")
            return False
    dprint(f"=> {vertex} can be removed")
    return True


def solve(grid: np.ndarray, bricks: List[Brick]) -> nx.DiGraph:
    """Common part to both parts"""
    dprint(f"---Initial (rotated) ---\n{rotate(grid)}")
    fall(grid, bricks)
    g = get_connections(grid, bricks)
    # validate_graph(g, bricks)
    return g


def solve_p1(args) -> int:
    """Solution to the 1st part of the challenge"""
    grid, bricks  = args
    g_connections: nx.DiGraph = solve(grid, bricks)
    return sum(can_be_removed(g_connections, vertex)
               for vertex in g_connections.nodes())


def solve_p2(args) -> int:
    """Solution to the 2nd part of the challenge"""
    grid, bricks  = args
    g_connections: nx.DiGraph = solve(grid, bricks)
    counts: Dict[int, int] = count_descendants(g_connections)
    total = 0
    for v in g_connections.nodes():
        if not can_be_removed(g_connections, v):
            total += counts[v]
    return total


tests = [
    (load_input('test.1.txt'), 5, 6+1),
]


reals = [
    # 643064 -- too high
    # 627757 -- too high
    # 119550 -- too high
    (load_input(), 468, None)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
