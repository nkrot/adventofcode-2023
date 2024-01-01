#!/usr/bin/env python

# # #
#
# Ideas how to simplify:
# 1. implement Platform as a mere list (tuple) of strings w/o using Matrix
# 2. implement tilting (to the west) as Dominik did:
#     - split the string by #
#     - sort each part to that O are at the beginning (west) or end (east)
#     - join the parts back
# 3. part 2 can be implemented w/o periodic sequences. Instead:
#    - do tilting cycles and save the resulting Platform
#    - as soon as a results start to repeat,
#      - determine the period of repetition
#      - check if target number of cycles (1 billion) is a multiple of
#        the computed period value

import os
from typing import Dict, List, Union
from collections import defaultdict

from aoc import utils, Matrix
from aoc.utils import dprint

from .estimator import Estimator

DAY = '14'
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
    return utils.load_input(fname, parser=Platform.from_lines)


class Platform(Matrix):

    @classmethod
    def from_file(cls, filepath):
        with open(filepath, 'r') as fd:
            return cls.from_lines(fd.readlines())

    @classmethod
    def from_lines(cls, lines: List[str]):
        lines = [list(line.strip()) for line in lines]
        return cls(lines)

    # def transpose(self):
    #     print("transposing", type(self))
    #     mtx = super().transpose()
    #     print("result is", type(mtx))
    #     return type(self)(mtx)

    def compute_load(self) -> int:
        weight = 0
        n_rows, _ = self.shape()
        for i, rocks in enumerate(self.rows()):
            weight += (n_rows - i) * sum(rock == "O" for rock in rocks)
        return weight


def roll_a_rock(rocks: List[str], pos: int = 0, to_end: bool = False):
    """Roll a round rock to the beginning (default) or to the end
    (if to_end is True) of given list of rocks
    """

    def positions():
        if to_end:
            return range(pos+1, len(rocks))
        return range(pos-1, -1, -1)

    if rocks[pos] == "O":
        # find position where to move the round rock to
        j = None
        for i in positions():
            if rocks[i] == '.':
                j = i
            else:
                break
        # move the round rock
        if j is not None:
            rocks[j], rocks[pos] = rocks[pos], rocks[j]


# TODO: do it recursively for fun
# def roll_a_rock(rocks: List[str], pos: int = 0):
#     if rocks[pos] == "O" and pos > 0 and rocks[pos-1] == ".":
#         for i in range(pos-1, 0-1, -1):
#             if rocks[i] == '.':
#                 rocks[i], rocks[pos] = rocks[pos], rocks[i]
#                 pos = i
#             else:
#                 break

def tilt_north(platform: Platform) -> Platform:
    """New object is returned
    TODO: do it without .transpose()
    """
    plt = platform.transpose()
    plt = tilt_west(plt)
    return plt.transpose()


def tilt_south(platform: Platform) -> Platform:
    """New object is returned
    TODO: do it without .transpose()
    """
    plt = platform.transpose()
    plt = tilt_east(plt)
    return plt.transpose()


def tilt_west(platform: Platform) -> Platform:
    """Changes happen in place"""
    for rocks in platform.rows():
        for j in range(len(rocks)):
            roll_a_rock(rocks, j)
    return platform


def tilt_east(platform: Platform) -> Platform:
    """Changes happen in place"""
    for rocks in platform.rows():
        for j in range(len(rocks)-1, -1, -1):
            roll_a_rock(rocks, j, True)
    return platform


def solve_p1(platform: Platform) -> int:
    """Solution to the 1st part of the challenge"""
    dprint(f"--- solve_p1 ---\n{platform}")
    plt = tilt_north(platform)
    dprint(f"--- Final ---\n{plt}")
    return plt.compute_load()


def solve_p2(platform: Platform) -> int:
    """Solution to the 2nd part of the challenge.

    Idea:
    Perform tilting of the platform for a number of times (hopefully, less
    that 1 billion cycles) and for each possible beam load value collect
    data on at what cycle it occurred (List[int]).
    When enough evidence collected (say, 10 observations for each load
    value), analyse it and find out the repetition pattern (see examples
    in `tests/aoc/day_14/test_estimator.py`).
    Using the repetition pattern check if it would generate the target
    number (1 000 000 000).
    As soon as the repetition pattern that generates the target number was
    found, stop.
    """
    dprint(f"--- solve_p2 ---\n{platform}")
    n_cycles = 1_000_000_000
    plt = platform
    north_beam_loads: Dict[int, List[int]] = defaultdict(list)
    for n_cycle in range(1, n_cycles+1):
        plt = tilt_north(plt)
        plt = tilt_west(plt)
        plt = tilt_south(plt)
        plt = tilt_east(plt)
        north_beam_load = plt.compute_load()
        if is_solution(n_cycles, n_cycle, north_beam_load, north_beam_loads):
            break
    dprint(f"--- Done ---\n{north_beam_loads}")
    dprint(f"--- Final ---\n{plt}")
    dprint(f"North beam load: {north_beam_load}")

    return north_beam_load


def is_solution(
    target_cycle: int,
    current_cycle: int,
    load_value: int,
    storage: Dict[int, Union[List[int], Estimator]]
) -> bool:
    """Check if given beam load value `load_value` is also the beam load value
    that is observed (expected) at the tilting cycle number `target_cycle`.

    Args:
      target_cycle (int):
        the number of the cycle for which we want to find out the beam load value.
      current_cycle (int):
        the number of the current cycle.
      load_value (int):
        beam load value corresponding to the current cycle
      storage:
        a cache to store pairs (load_value, List[current_cycle]) until
        accumulated data is sufficient to make a decision.

    Return
      True or False
    """

    seen_at_steps = storage.get(load_value, [])
    dprint(f"Cycle {current_cycle}:", load_value,
          f"seen in {seen_at_steps}" if seen_at_steps else "")

    if isinstance(seen_at_steps, Estimator):
        # We tried it before, reuse the outcomes.
        return target_cycle in seen_at_steps

    if len(seen_at_steps) > 10:
        estimator = Estimator(debug=False)
        storage[load_value] = estimator.analyse(seen_at_steps)
        dprint(load_value, estimator)
        ok = target_cycle in estimator
        if ok:
            dprint(f"Solved! num_cycles={current_cycle} beam_load={load_value}")
        return ok

    storage[load_value].append(current_cycle)

    return False


tests = [
    (load_input('test.1.txt'), 136, 64),
]

reals = [
    (load_input(), 113486, 104409)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
