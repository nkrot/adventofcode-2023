#!/usr/bin/env python

# # #
#
#

import re
import os
import sys
from typing import List
from dataclasses import dataclass

from aoc.utils import load_input, run_tests, run_real, to_numbers, prod

DAY = '06'
DEBUG = int(os.environ.get('DEBUG', 0))


@dataclass
class RaceRecord:
    time: int = 0 # milliseconds
    distance: int = 0  # millimeters
    wins: int = 0


def parse(lines: List[str]) -> List[RaceRecord]:
    """Parse lines of input into suitable data structure"""
    races = []
    for line in lines:
        fields = line.strip().replace(':', '').split()
        name = fields.pop(0).lower()
        numbers = to_numbers(fields)
        if not races:
            races = [RaceRecord() for _ in numbers]
        for n, r in zip(numbers, races):
            setattr(r, name, n)
    if DEBUG:
        for race in races:
            print(race)
    return races


def run_a_race(t_press: int, race: RaceRecord):
    if t_press > race.time:
        return False

    speed = t_press
    t_race = race.time - t_press
    d = t_race * speed
    if d > race.distance:
        race.wins += 1
        if DEBUG:
            print(f"Win at {t_press}: {race}")
        return True

    return False


def solve_p1(races: List[RaceRecord]) -> int:
    """Solution to the 1st part of the challenge"""
    max_time = max(r.time for r in races)

    for t_press in range(max_time+1):
        speed = t_press
        for race in races:
            run_a_race(t_press, race)

    wins = [r.wins for r in races if r.wins]

    return prod(wins)


def solve_p2(races: List[RaceRecord]) -> int:
    """Solution to the 2nd part of the challenge"""

    race = RaceRecord()
    for att in {"time", "distance"}:
        value = "".join(str(getattr(r, att)) for r in races)
        setattr(race, att, int(value))

    t_mid = race.time // 2 + 1

    for t_first in range(t_mid):
        if run_a_race(t_first, race):
            break

    for t_last in range(t_mid):
        if run_a_race(race.time - t_last, race):
            break

    return race.time - t_first - t_last + 1


tests = [
    (load_input('test.1.txt', parser=parse), 4*8*9, 71503),
]


reals = [
    (load_input(parser=parse), 3317888, 24655068)
]


if __name__ == '__main__':
    run_tests(DAY, tests, solve_p1, solve_p2)
    run_real(DAY, reals, solve_p1, solve_p2)
