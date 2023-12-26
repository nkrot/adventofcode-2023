#!/usr/bin/env python

# # #
#
# https://stackoverflow.com/questions/2931573/determining-if-two-rays-intersect


import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from aoc import utils, Ray, Point
from aoc.utils import dprint, to_numbers

DAY = '24'
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
    return utils.load_input(fname, line_parser=parse)


def parse(line: str) -> Ray:
    """Parse a line of input into suitable data structure"""
    numbers = to_numbers(re.findall(r'-?\d+', line))
    ray = Ray(numbers[:3], numbers[3:])
    dprint(ray)
    return ray


@dataclass
class Area:
    min: int
    max: int

    def __contains__(self, point: Union[Point, Tuple[int]]) -> bool:
        """Check if given point is in the current Area."""
        # check is 2D, although point can be 3D
        tests = [self.min <= point[i] <= self.max for i in [0, 1]]
        dprint(f"in area? {tests}")
        return all(tests)


def solve_p1(args) -> int:
    """Solution to the 1st part of the challenge"""
    rays, area = args
    cnt = 0
    for i in range(len(rays)):
        for j in range(i+1, len(rays)):
            p = rays[i] & rays[j]
            dprint(f"Intersect at: {p}")
            if p and p in area:
                cnt += 1
    return cnt


def solve_p2(lines: List[str]) -> int:
    """Solution to the 2nd part of the challenge"""
    return 0


tests = [
    ((load_input('test.1.txt'), Area(7, 27)), 2, None),
]


reals = [
    ((load_input(), Area(2e14, 4e14)), 17867, None)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
