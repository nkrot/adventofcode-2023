#!/usr/bin/env python

# # #
#
#

import os
import re
import sys
from typing import Dict, List, Tuple, Optional

from aoc import utils
from aoc.utils import dprint, to_numbers

DAY = '15'
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
    return utils.load_input(fname, parser=parse)


def parse(lines: List[str]) -> List[str]:
    return lines[0].split(',')


def compute_hash(text: str, start: int = 0):
    value = start
    for ch in text:
        value += ord(ch)
        value *= 17
        value %= 256
    dprint(f"HASH '{text}' {start} --> {value}")
    return value


def solve_p1(steps: List[str]) -> int:
    """Solution to the 1st part of the challenge"""
    return sum(compute_hash(step) for step in steps)


class Step:
    """
    An instruction that is either a lens or an instruction to remove a lens,
    based on the operation
    rn=1  --> (LENS)   label=rn, focal_length=1;       operation is =
    cm-   --> (REMOVE) label=cm, focal_length=None;    operation is -
    """
    def __init__(self, text: str):
        self.label = None
        self.focal_length = None
        self._hash = None
        self._parse_and_set(text)

    def _parse_and_set(self, text: str):
        m = re.match(r'(.+)=(\d+)', text)
        if m:
            self.label = m[1]
            self.focal_length = int(m[2])
            return
        m = re.match(r'(.+)-$', text)
        if m:
            self.label = m[1]
            return
        raise ValueError(f"Cannot parse: '{text}'")

    def is_add(self):
        return bool(self.focal_length is not None)

    def is_remove(self):
        return bool(self.focal_length is None)

    def __eq__(self, other: 'Step'):
        return self.label == other.label

    def __hash__(self):
        if self._hash is None:
            self._hash = compute_hash(self.label)
        return self._hash

    def __str__(self):
        if self.focal_length is None:
            return f"[{self.label}]"
        else:
            return f"[{self.label} {self.focal_length}]"

    def __repr__(self):
        s = "<{}: label={} hash={}".format(
            self.__class__.__name__, self.label, hash(self))
        if self.focal_length is not None:
            s += f" focal_length={self.focal_length}"
        return s + ">"


def get_index(items, item) -> Optional[int]:
    """Need to have this coprophagy because python sucks because its architect sucks"""
    try:
        idx = items.index(item)
        return idx
    except ValueError:
        return None


def allocate(boxes: List[List[Step]], step: Step):
    if step.is_remove():
        for box in boxes:
            idx = get_index(box, step)
            if idx is not None:
                box.pop(idx)

    if step.is_add():
        box = boxes[hash(step)]
        idx = get_index(box, step)
        if idx is None:
            box.append(step)
        else:
            box[idx] = step


def compute_focusing_power(boxes) -> int:
    focusing_power = 0
    for bidx, box in enumerate(boxes):
        for lidx, lens in enumerate(box):
            focusing_power += (bidx+1) * (lidx+1) * lens.focal_length
    return focusing_power


def solve_p2(steps: List[str]) -> int:
    """Solution to the 2nd part of the challenge"""
    boxes = [[] for _ in range(256)]
    for txt in steps:
        step = Step(txt)
        allocate(boxes, step)
    if DEBUG:
        print_boxes(boxes)
    return compute_focusing_power(boxes)


def print_boxes(boxes):
    for idx, box in enumerate(boxes):
        values = " ".join(str(s) for s in box)
        print(f"Box {idx}: {values}")


tests = [
    (load_input('test.1.txt'), 1320, 145),
]


reals = [
    (load_input(), 517551, 286097)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
