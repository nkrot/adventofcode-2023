"""
Solution v.1

It works for the part 1 of the task but cannot handle part 2
"""

from typing import List, Tuple

from aoc import Matrix, Point
from aoc.utils import dprint

from .common import DiggingInstruction, measure_field


class Trench:
    # if the trench goes in R,L,U,D direction, which side of it is the right
    # hand side?
    SIDES = {
        'R': 'v',  # south side
        'L': '^',  # north side
        'U': '>',  # east side
        'D': '<',  # west side
    }

    def __init__(self, instruction: DiggingInstruction = None):
        self.rhs = self.SIDES.get(instruction.direction) if instruction else None

    def __str__(self):
        return self.rhs or "#"


def dig_contour(
    field: Matrix,
    pos: Point,
    instructions: List[DiggingInstruction]
):
    """Apply digging instructions and dig the trench (contour of the lagoon)
    on the field.
    """
    for inst in instructions:
        for dxy in inst:
            pos += dxy
            field[pos] = Trench(inst)


def dig_interior(field: Matrix):
    """Dig interior enclosed within the contour.

    We assume that the right hand side of the contour faces the inner side
    of the lagoon.
    """
    # we plan to dig from left to right
    dxy = DiggingInstruction.DXY['R']

    def can_dig_after(tile):
        return isinstance(tile, Trench) and str(tile) == '>'

    for xy, _ in field.findall(can_dig_after):
        pos = Point(xy) + dxy
        while field.get(pos):
            tile = field[pos]
            dprint("Dig?", pos, str(tile))
            if str(tile) == '.':
                field[pos] = Trench()
            elif str(tile) == '<':
                break
            pos += dxy


def create_field(
    instructions: List[DiggingInstruction]
) -> Tuple[Matrix, Point]:
    """Create and return matrix of required size (computed from instructions)
    as well as the starting point.
    """
    dprint("measure_field")
    (height, width), start = measure_field(instructions)
    mat = Matrix(height, width, ".")
    return mat, start


def solve_p1(instructions: List[DiggingInstruction]) -> int:
    field, start = create_field(instructions)
    dprint(f"--- Initial field ---\n{field}")

    dig_contour(field, start, instructions)
    dprint(f"--- Lagoon contour ---\n{field}")

    dig_interior(field)
    dprint(f"--- Lagoon ---\n{field}")

    cubes = field.findall(lambda tile: isinstance(tile, Trench))

    return len(cubes)
