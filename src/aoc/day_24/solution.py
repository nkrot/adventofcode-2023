#!/usr/bin/env python

# # #
#
# https://stackoverflow.com/questions/2931573/determining-if-two-rays-intersect


import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

import matplotlib.pyplot as plt

from aoc import Point, Ray, utils, Colorizer
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


COLORS = Colorizer()

def parse(line: str) -> 'Hailstone':
    """Parse a line of input into suitable data structure"""
    numbers = to_numbers(re.findall(r'-?\d+', line))
    hailstone = Hailstone(numbers[:3], numbers[3:], color=next(COLORS))
    dprint(hailstone)
    return hailstone


class Hailstone(Ray):
    """For clearer naming + color attribute

    TODO: move color to Line? looks useful there as well
    """

    def __init__(self, *args, **kwargs):
        self.color = kwargs.pop('color', 'black')
        super().__init__(*args, **kwargs)


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
    hailstones, area = args
    cnt = 0
    for i in range(len(hailstones)):
        for j in range(i+1, len(hailstones)):
            p = hailstones[i] & hailstones[j]
            dprint(f"Collide at: {p}")
            if p and p in area:
                cnt += 1
    return cnt


def solve_p2(hailstones: List[Hailstone]) -> int:
    """Solution to the 2nd part of the challenge"""
    print(hailstones)
    explore_collisions(hailstones)
    explore_collisions_in_each_plain(hailstones)
    return 0


def explore_collisions(hailstones):
    for i, h1 in enumerate(hailstones):
        for j in range(i+1, len(hailstones)):
            h2 = hailstones[j]
            p = h1 & h2
            print((i, j), p, h1, h2)
        print()


def explore_collisions_in_each_plain(hailstones):
    """explore whether the trajectories intersect in each of the planes
    X-Y, X-Z, Y-Z
    """
    axes = {0: 'x', 1: 'y', 2: 'z'}
    for d1, d2 in [(0,1), (1,2), (0,2)]:
        plane = (axes[d1], axes[d2])
        print(f"--- Collisions in the plane {(d1, d2)} ---")
        # make all hailstones 2D
        hailstones_2d = [
            Hailstone((h.s[d1], h.s[d2]), (h.d[d1], h.d[d2]), color=h.color)
            for h in hailstones
        ]
        # compute and print intersection points
        explore_collisions(hailstones_2d)

        # draw trajectories of flying hailstones (as arrows)
        outfile = "test.1.{}.png".format("-".join(map(str, plane)))
        draw_trajectories(hailstones_2d, plane, outfile)


def draw_trajectories(
    hailstones: List[Hailstone],
    labels: List[str],
    filename: str = None
):

    # used to compute how long an error will be and corresponds to the
    # number of nanoseconds the hailstone flies.
    n_steps = 16  # set manually
    # min and max values long X and Y axes
    xlims = (-15, 35)
    ylims = (-23, 35) # set manually

    arrow_props = dict(
        linewidth = 0.5,
        length_includes_head = True,
        width = 0.1,   # tail width
        head_width = 1,
        color = 'black'
    )

    fig = plt.figure()

    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html
    for hail in hailstones:
        # variant 1
        # start, end = hail.s, hail.s + hail.d
        # line = plt.axline(start, end, color=hail.color, linewidth=0.5)
        # plt.annotate('ugly', xy=end, xytext=start, arrowprops={})

        # variant 2
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.arrow.html
        arrow_props['color'] = hail.color
        line = plt.arrow(*hail.s, *(hail.d * n_steps), **arrow_props)

        fig.add_artist(line)

    if len(labels) == 2:
        plt.xlabel(labels[0])
        plt.ylabel(labels[1])

    if xlims: plt.xlim(xlims)
    if ylims: plt.ylim(ylims)
    plt.grid(True, linestyle="dotted")

    if filename:
        print(f"Saving plot to the file: {filename}")
        plt.savefig(filename)
    else:
        plt.show()

    plt.close(fig)


tests = [
    #((load_input('test.1.txt'), Area(7, 27)), 2, None),
    (load_input('test.1.txt'), None, 24+13+10),
]


reals = [
    ((load_input(), Area(2e14, 4e14)), 17867, None)
    # (load_input(), None, -1)

]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
