import re
from dataclasses import dataclass
from typing import List, Tuple

from aoc import Point
from aoc.utils import dprint


@dataclass
class DiggingInstruction:
    """
    The look like this:

    R 6 (#70c710)
    D 5 (#0dc571)
    L 2 (#5713f0)
    D 2 (#d2c081)
    """

    direction: str
    length: int
    color: str = None

    DXY = {
        'R': (0, 1),
        'L': (0, -1),
        'D': (1, 0),
        'U': (-1, 0)
    }

    def __iter__(self):
        # TODO: use generator
        steps = [ self.DXY[self.direction] ] * self.length
        return iter(steps)

    @classmethod
    def from_text(cls, line: str):
        fields = re.sub(r'[()]', '', line).split()
        fields[1] = int(fields[1])
        return cls(*fields)

    def __radd__(self, other: Point):
        return self.__add__(other)

    def __add__(self, other: Point) -> Point:
        """Return another Point that is offset from the given point according
        to the current digging instruction.
        """
        assert isinstance(other, Point)
        offset = Point(self.DXY[self.direction]) * self.length
        return other + offset

def measure_field(
    instructions: List['DiggingInstruction']
) -> Tuple[Tuple[int, int], Point]:
    """Inspect digging instructions, estimate the size (height and width)
    of the lagoon.

    Additionally, compute starting point whether the digging must start
    such that it is within the field.
    """
    dprint("measure_field")
    y, x = 0, 0
    max_y, max_x = None, None
    min_y, min_x = None, None
    for inst in instructions:
        if inst.direction == 'R':
            y += inst.length
            max_y = y if max_y is None else max(max_y, y)
        elif inst.direction == 'L':
            y -= inst.length
            min_y = y if min_y is None else min(min_y, y)
        elif inst.direction == 'D':
            x += inst.length
            max_x = x if max_x is None else max(max_x, x)
        elif inst.direction == 'U':
            x -= inst.length
            min_x = x if min_x is None else min(min_x, x)
    height = max_x - min_x + 1
    width = max_y - min_y + 1
    dprint("x (height)", (min_x, max_x), height)
    dprint("y (width)", (min_y, max_y), width)
    start = Point(0, 0) - (min_x, min_y)
    dprint(f"Start at {start}")
    return (height, width), start


def convert_digging_instructions(instructions: List[DiggingInstruction]):
    """Convert digging instructions of the part 1 for the part 2."""
    recoding = {'0': 'R', '1': 'D', '2': 'L', '3': 'U'}
    new_instructions = [
        DiggingInstruction(
            direction=recoding[inst.color[-1]],
            length=int(inst.color[1:-1], 16),
        )
        for inst in instructions
    ]
    return new_instructions
