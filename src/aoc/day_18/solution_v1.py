"""
Solution v.1

It works for the part 1 of the task but cannot handle part 2 that would need
a matrix of a very large size.
"""

from typing import List, Tuple

from aoc import Matrix, Point
from aoc.utils import dprint

from .common import DiggingInstruction, measure_field


class Trench:
    # if the trench goes in R,L,U,D direction, which side of it is the right
    # hand side (or inner side of the lagoon):
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
    of the lagoon. We dig in all directions:
      1) from >, dig rightwards
      2) from v, dig downwards
      3) from <, dig leftwards
      4) from ^, dig upwards
    all until another trench tile is encountered.

    Turns out, a few spots remain undug, at the intersections of the points
    where digging turned:
    ```
          >#<
          >#<vv
          >###<
        >vv#.#<vv
        >#######<
        ?????????
            vvvv<
            >
    ```
    and they are addressed in the fashion of delation: if such a tile is
    surrounded by dug out tiles, dig this one out too.

    TODO
    1) Maybe have extra 4 characters to represent turn points (corners) that
       have the inside on two sides?

    Historic notes:
    ---------------
    In the initial buggy implementation, digging was only from left to right,
    starting after '>' and ending before '<'. By coincidence, it produced
    the correct answers, though the shape was wrong: some inner parts were
    not dug out and some outer parts were dug out.
    """
    _dig_interior(field, DiggingInstruction.DXY['R'], '>')
    _dig_interior(field, DiggingInstruction.DXY['L'], '<')
    _dig_interior(field, DiggingInstruction.DXY['U'], '^')
    _dig_interior(field, DiggingInstruction.DXY['D'], 'v')
    _delate(field)


def _delate(field: Matrix):
    """
    Dig a tile if surrounded by 4 dug out tiles.
    """
    for xy, tile in field:
        if str(tile) == '.':
            tests = [str(field.get(nxy)) == '#' for nxy in Point(xy).around4()]
            if len(tests) == 4 and all(tests):
                field[xy] = Trench()


def _dig_interior(field, dxy, start):

    def can_dig_after(tile):
        return str(tile) == start

    for xy, _ in field.findall(can_dig_after):
        pos = Point(xy) + dxy
        while field.get(pos):
            tile = field[pos]
            dprint("Dig?", pos, str(tile))
            if str(tile) == '.':  # dig out
                field[pos] = Trench()
            elif str(tile) == '#':  # skip, already dug out
                pass
            elif isinstance(tile, Trench):
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
