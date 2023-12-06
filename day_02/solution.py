#!/usr/bin/env python

# # #
#
#

import re
import os
import sys
from dataclasses import dataclass
from typing import List, Tuple

from aoc import utils

DAY = '02'
DEBUG = int(os.environ.get('DEBUG', 0))


@dataclass
class SetOfCubes:
    red: int = 0
    green: int = 0
    blue: int = 0

    COLORS = ('red', 'green', 'blue')

    @classmethod
    def from_string(cls, text: str):
        colors = {}
        for chunk in text.strip().split(','):
            m = re.match('(\d+) (.+)', chunk.strip())
            colors[m[2]] = int(m[1])
        return cls(**colors)

    def power(self) -> int:
        return self.red * self.green * self.blue

    def __gt__(self, other):
        tests = [
            getattr(self, color) > getattr(other, color)
            for color in self.COLORS
        ]
        return any(tests)


T_GAME = Tuple[int, List[SetOfCubes]]


def parse(line: str) -> T_GAME:
    """Parse a line of input into suitable data structure:"""
    m = re.match(r'Game (\d+): (.+)', line)
    return (
        int(m[1]),
        [SetOfCubes.from_string(chunk) for chunk in m[2].split(';')]
    )


def solve_p1(games: List[T_GAME]) -> int:
    """Solution to the 1st part of the challenge"""
    target = SetOfCubes(red=12, green=13, blue=14)
    res = 0
    for game_id, sets in games:
        if not any(t > target for t in sets):
            res += game_id

    return res


def solve_p2(games: list) -> int:
    """Solution to the 2nd part of the challenge"""
    res = 0
    for game_id, sets in games:
        min_soc = SetOfCubes()
        for soc in sets:
            # TODO: reimplement using a subtraction and addition?
            for color in SetOfCubes.COLORS:
                if getattr(soc, color) > getattr(min_soc, color):
                    setattr(min_soc, color, getattr(soc, color))
        res += min_soc.power()
    return res



tests = [
    (utils.load_input('test.1.txt', line_parser=parse),
     8, sum([48, 12, 1560, 630, 36])),
]


reals = [
    (utils.load_input(line_parser=parse), 2416, 63307)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
