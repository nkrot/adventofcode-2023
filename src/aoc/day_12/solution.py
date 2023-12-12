#!/usr/bin/env python

# # #
#
#

import os
import sys
from typing import Callable, Dict, List, Tuple

from aoc import utils
from aoc.utils import dprint, to_numbers

sys.setrecursionlimit(1500)  # otherwise python raises RecursionError

DAY = '12'
DEBUG = int(os.environ.get('DEBUG', 0))


def solve_part_1(fname: str):
    res = solve_p1(load_input(fname))
    print(res)


def solve_part_2(fname: str):
    res = solve_p2(load_input(fname))
    print(res)


def parse(line: str) -> Tuple[List[int], List[int]]:
    """Parse a line of input into suitable data structure:
    """
    record, checksums = line.split()
    condition_record = ["?.#".index(ch) - 1 for ch in record]
    checksums = to_numbers(checksums.split(','))
    #dprint("Input", condition_record, checksums)
    return condition_record, checksums

# How to cache function results
#https://stackoverflow.com/questions/815110/is-there-a-decorator-to-simply-cache-function-return-values

# user time -p
# T.0.p2: True 525152 525152
# pypy   | w/o memoization | 13,84
# pypy   | w/  memoization |  0,24
# python | w/o memoization | 52,94
# python | w/  memoization |  0,14

# user time -p
# --- Day 12 p.2 ---
# True 5071883216318 5071883216318
# pypy   | w/o memoization | probably days :)
# pypy   | w/  memoization | 34,32
# python | w/o memoization | ???
# python | w/  memoization | 77,56

class memoize(dict):
    """Decorator for memoizing 3 arguments of the function and the result"""
    def __init__(self, func: Callable):
        self.nargs = 3  # how many arguments to cache
        self.function = func

    def __call__(self, *args, **kwargs):
        self.args = args[:self.nargs]
        return self[self._to_key()]

    def __missing__(self, key):
        self[key] = self.function(*self.args)
        return self[key]

    def _to_key(self) -> Tuple[str]:
        return tuple(str(arg) for arg in self.args)


@memoize
def count_arrangements(
    springs: List[int],
    checksums: List[int],
    current_grp_count: int = 0,
    level: int = 0
) -> int:
    """Returns number of correct arrangements"""

    indent = ' ' * level
    dprint("{}Solving[{}]:{}\t{} {}".format(
            indent, level,
           " ".join(str(n).rjust(3) for n in springs),
           checksums, current_grp_count))

    def vv(val):
        dprint(f"{indent}Result[{level}]: {val}")
        return val

    if not springs:
        if not current_grp_count and not checksums:
            # no recent groups behind and not expected groups ahead
            return vv(1)
        elif len(checksums) == 1 and current_grp_count == checksums[0]:
            # the last group has been consumed correctly
            return vv(1)
        else:
            # the last group does not match expectation
            return vv(0)

    elif springs[0] == 0:
        if current_grp_count:
            # we have just reached the end of a group
            if checksums and current_grp_count == checksums[0]:
                # so far so good: a group has just been consumed
                return vv(count_arrangements(springs[1:], checksums[1:], 0, level+1))
            else:
                # mistake
                return vv(0)
        else:
            # we are between the groups or at the beginning of the springs record
            return vv(count_arrangements(springs[1:], checksums, 0, level+1))

    elif springs[0] == 1:
        # we are within a group
        return vv(count_arrangements(springs[1:], checksums, current_grp_count+1, level+1))

    elif springs[0] == -1:
        return sum([
            vv(count_arrangements(spring + springs[1:], checksums, current_grp_count, level))
            for spring in ([0], [1])
        ])


# TODO: implement debugging as a decorator
# def tap(func):
#     dprint("Starting...")
#     res = func()
#     dprint("Done.. Result=", res)
#     return res


def solve_p1(records: List[Tuple[List[int], List[int]]]) -> int:
    """Solution to the 1st part of the challenge"""
    # counts = [count_arrangements(record, checksums)
    #           for record, checksums in book]
    counts = []
    for idx, record in enumerate(records):
        #print(f"Starting case {idx}...")
        counts.append(count_arrangements(*record))
        #print("Done. Result =", counts[-1])
    dprint("All computed counts", counts)
    return sum(counts)


def solve_p2(records: List[Tuple[List[int], List[int]]]) -> int:
    """Solution to the 2nd part of the challenge"""
    unfolded_records = [
        [springs + ([-1] + springs) * 4, checksums*5]
        for springs, checksums in records
    ]
    return solve_p1(unfolded_records)


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    return utils.load_input(fname, line_parser=parse)


tests = [
    #(load_input('test.1.txt'), sum([1, 1, 1, 1, 1, 1]), None),
    (load_input('test.2.txt'),
     sum([1, 4, 1, 1, 4, 10]),
     sum([1, 16384, 1, 16, 2500, 506250])),

    # test.2.txt L#6
    #([parse("?###???????? 3,2,1")], sum([10]), None),
    # decomposing test.2.txt L#6
    #([parse(".......? 1")], 1, None),
    #([parse("......?? 1")], 2, None),
    #([parse("??? 1")], 3, None),
    #([parse(".???? 2,1")], 1, None),
]


reals = [
    (load_input(), 7694, 5071883216318)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
