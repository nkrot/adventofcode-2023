#!/usr/bin/env python

# # #
#
#

import os
from typing import List, Tuple
from collections import Counter

from aoc import utils, Matrix
from aoc.utils import dprint

DAY = '13'
DEBUG = int(os.environ.get('DEBUG', 0))


def solve_part_1(fname: str):
    res = solve_p1(load_input(fname))
    print(res)


def solve_part_2(fname: str):
    res = solve_p2(load_input(fname))
    print(res)


class Pattern(Matrix):

    @classmethod
    def from_lines(cls, lines: List[str]):
        tiles = [list(line) for line in lines]
        return cls(tiles)

    # if implemented like this, .transpose() is broken. Is my understanding
    # of inheritance correct? Should Pattern use inheritance or composition
    # wrt to Matrix?
    # def __init__(self, lines: List[str]):
    #     tiles = [list(line) for line in lines]
    #     super().__init__(tiles)


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    return utils.load_input(fname, parser=parse)


def parse(lines: List[str]) -> List[Pattern]:
    """Parse a line of input into suitable data structure:
    """
    patterns = [Pattern.from_lines(lns) for lns in utils.group_lines(lines)]
    if DEBUG:
        print("--- Parse --")
        for f in patterns:
            dprint(repr(f))
        print("--- /Parse ---")
    return patterns


def find_reflection_across_vertical_line(pattern: Pattern) -> List[int]:
    # Find reflection points in each row.
    # A reflection point is a column number after each the point is located.
    reflections = Counter()
    for row in pattern.rows():
        for i in range(1, len(row)):
            head = list(reversed(row[:i]))
            tail = row[i:]
            ok = all(h == t for h, t in zip(head, tail))
            dprint(f"Checking '{''.join(head)}' >< '{''.join(tail)}' -- {'OK' if ok else ''}")
            #dprint(list(zip(head, tail)), ok)
            if ok:
                reflections[i] += 1

    # Select reflection points that occur in every row
    # These are the reflection points of the whole field
    n_rows, _ = pattern.shape()
    refl_columns = [
        n_col
        for n_col, cnt in reflections.items()
        if cnt == n_rows
    ]
    dprint("Reflections", refl_columns)

    return refl_columns


def find_reflections(pattern: Pattern) -> Tuple[List[int], List[int]]:
    dprint("Searching reflection column lines...")

    columns = find_reflection_across_vertical_line(pattern)
    dprint("Columns", columns)

    dprint("Searching reflection row lines...")
    rows = find_reflection_across_vertical_line(pattern.transpose())
    dprint("Rows", rows)

    dprint("Rows and columns", rows, columns)

    return (rows, columns)


def compute_score(rows: List[int], columns: List[int]) -> int:
    """Given reflection points in rows and columns in a Pattern, compute
    the score of that pattern."""
    return sum(columns) + sum(rows) * 100


def fix_smudge_and_score(pattern: Pattern) -> int:
    """Brute force algorithm that performs all transformations of a pattern,
    finds a pattern with a different reflection line(s), determined by
    a different score, and returns the new score.
    """

    dprint(f"\nPattern:\n{pattern}")

    def flip(obj: str) -> str:
        """Rock to Ash and viceversa"""
        return "#" if obj == "." else "."

    initial_reflections = find_reflections(pattern)
    initial_score = compute_score(*initial_reflections)

    for xy, obj in pattern:
        pattern[xy] = flip(obj)

        reflections = find_reflections(pattern)
        score = compute_score(*reflections)

        if score and score != initial_score:
            dprint("Initial:", initial_score, initial_reflections)
            dprint("New:", score, reflections)
            # Subtract initial from new ones, because of the requirement:
            # < fix the smudge that causes a *different* reflection line to be valid.
            adjusted_reflections = [
                set(current) - set(initial)
                for current, initial in zip(reflections, initial_reflections)
            ]
            dprint("Diffs", adjusted_reflections)
            return compute_score(*adjusted_reflections)

        pattern[xy] = obj  # restore initial state

    return initial_score


def solve_p1(patterns: List[Pattern]) -> int:
    """Solution to the 1st part of the challenge"""
    scores = [
        compute_score(*find_reflections(pattern))
        for pattern in patterns
    ]
    return sum(scores)


def solve_p2(patterns: List[Pattern]) -> int:
    """Solution to the 2nd part of the challenge"""
    return sum(fix_smudge_and_score(pattern) for pattern in patterns)


tests = [
    (load_input('test.1.txt'), 5+100*4, 400),
    (load_input('test.1.2.txt'), 400, 100),
]


reals = [
    (load_input(), 35538, 30442)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
