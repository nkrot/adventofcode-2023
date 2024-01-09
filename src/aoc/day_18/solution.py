"""
Part 1
------

The solution to the first part simulates digging a field. The field is
represented by a matrix. First, the contour is dug out: this places into
corresponding cells one of the arrows (characters '^', '>', 'v', '<') such
that the sharp side point to the right side of the trench.

Then, the inner area is dug out. We *assume* that the right side ('>')
is the inside of the area and dig from all tiles in the direction where
the arrow point:
  - from >, dig rightwards
  - from v, dig downwards
  - from <, dig leftwards
  - from ^, dig upwards
all until another arrow is encountered.

It turns out, this is not sufficient: there are few points that occur at
the intersection of lines that connect the corners (turn points) and they
remain undug. They are dug out using a process similar to delation in CV:
if a tile is surrounded by dug out tiles, it gets dug out too.

Finally, all dug out tiles (arrows and #) are counted. The sum of them is
the answer to the task.

See the files `test.1.res.txt` and `input.res.txt` for visualization and
the file `solution_v1.py` for implementation.

Additional implementation details
--------------------------------

To ensure smooth operation with the matrix, more specifially that the matrix
is indexed with positive numbers, we first check digging instructions to
compute the max span of each axis and recompute the starting point for
digging that might need to be moved from [0][0]. For example:

    R 6   // ends at (0, 6)
    D 2   // ends at (2, 6)
    L 10  // ends at (2,-4)

L10 would move the point left into the negative area. Top avoid it, the
starting point (0, 0) is moved by 4 to (0, 4), so that now

    R 6   // ends at (0, 10)
    D 2   // ends at (2, 10)
    L 10  // ends at (2, 0)

Relevant for the first part and not used in part two, because Shoelace
algorithm handles correctly negative coordinates.

Part 2
------

The solution to the second part uses Shoelace algorithm for computing the area
of the polygon -- the shape that results from digging the  ground following
the instructions provided. Shoelace algorithm makes use of the coordinates of
the corners of the polygon shape. Computing the corners is straighforward.
Negative coordinate of the corners do not pose any problems to the algorithm.

TODO: explain why correction is necessary: adding the length of the contour
plus one.

This approach also works for the first part.
"""

import os
from typing import List

from aoc import AOCException, Point, utils
from aoc.utils import dprint

from . import solution_v1
from .common import (DiggingInstruction, convert_digging_instructions,
                     measure_field)

DAY = '18'
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
    return utils.load_input(fname, line_parser=DiggingInstruction.from_text)


def solve_p1(instructions: List[DiggingInstruction]) -> int:
    """Solution to the 1st part of the challenge"""
    return solution_v1.solve_p1(instructions)
    #return solve_with_shoelace(instructions)  # this also works


def solve_p2(instructions: List[DiggingInstruction]) -> int:
    """Solution to the 2nd part of the challenge"""
    instructions = convert_digging_instructions(instructions)
    return solve_with_shoelace(instructions)


def solve_with_shoelace(instructions: List[DiggingInstruction]):
    """
    Shoelace algorithm for computing the area of the polygon.
    https://www.101computing.net/the-shoelace-algorithm/
    """
    corners = find_corners(instructions)

    # for shoelace algorithm, arrange the corners anticlockwise
    # NOTE: this does not guarantee that the points are arranged correctly
    # but it works for the current task.
    corners = list(reversed(corners))

    # shoelace algorithm
    area = sum([
        a.x * b.y - b.x * a.y
        for a, b in zip(corners[:-1], corners[1:])
    ]) / 2

    # add area of the contour trench itself
    # TODO: I dont really understand why this is necessary
    area += sum([inst.length for inst in instructions]) / 2
    area += 1  # area of the starting point

    return int(area)


def find_corners(instructions: List[DiggingInstruction]) -> List[Point]:
    """Given set of digging instructions, find all points that are corners
    of the shape (contour) dug out when the instructions are applied.

    The first and the last corners are the same point.
    """
    # size, start = measure_field(instructions)
    # dprint(f"Field size = {size}, start at {start}")
    start = Point((0,0))
    corners = [start]
    for idx, inst in enumerate(instructions):
        dprint(idx, inst)
        corners.append(corners[-1] + inst)
        dprint(f"..new corner: {corners[-1]}")

    if corners[0] != corners[-1]:
        raise AOCException(
            "Expecting a closed shape but found that ends do not match:"
            " {} vs {}".format(repr(corners[0]), repr(corners[-1]))
        )

    return corners


tests = [
    (load_input('test.1.txt'), 62, 952408144115),
]


reals = [
    (load_input(), 47139, 173152345887206)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
