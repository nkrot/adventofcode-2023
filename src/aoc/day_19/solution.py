#!/usr/bin/env python

# # #
#
#

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

from aoc import utils
from aoc.utils import dprint, group_lines

DAY = '19'
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


@dataclass
class MachinePart:
    x: int
    m: int
    a: int
    s: int

    @classmethod
    def from_text(cls, text: str):
        assert text.startswith('{'), f"Wrong input: {text}"
        categories = {
            m[1]: int(m[2])
            for m in re.finditer(r'([xmas])=(\d+)', text)
        }
        obj = cls(**categories)
        return obj

    def rating(self) -> int:
        """Total rating of the machine part as a sum of all individual
        ratings x+m+a+s"""
        return sum([self.x, self.m, self.a, self.s])


class Workflow:

    @classmethod
    def from_text(cls, text: str):
        obj = cls()
        fields = re.split(r'[{},]', text)
        obj.name = fields.pop(0)
        fields.pop()
        obj.actions = [Action.from_text(field) for field in fields]
        return obj

    def __init__(self):
        self.name: str = None

    def __call__(self, part: MachinePart) -> bool:
        """
        Return
        True if the Machine Part is accepted
        False if it is rejected
        """
        dprint("Applying:", self)
        dprint("..Actions:", self.actions)
        for action in self.actions:
            res = action(part)
            if res in {True, False}:
                return res
        return None

    def __repr__(self):
        return "<{}: name={}>".format(self.__class__.__name__, self.name)


class AcceptWorkflow(Workflow):

    def __init__(self):
        self.name = "A"
        self.actions = [lambda p: True]


class RejectWorkflow(Workflow):

    def __init__(self):
        self.name = "R"
        self.actions = [lambda p: False]


class Action:

    operators = {
        "<": "__lt__",
        ">": "__gt__"
    }

    @classmethod
    def from_text(cls, text: str):
        dprint(f"Action.from_text: '{text}'")
        obj = cls()
        obj.text = text
        m = re.match(r'^([xmas])([<>])(\d+):(.+)$', text)
        if m:
            attname = m[1]
            op = cls.operators[m[2]]
            val = int(m[3])
            iftrue = m[4]
            obj.action = lambda p: (
                cls.workflows[iftrue](p)
                if getattr(getattr(p, attname), op)(val)
                else None
            )
            return obj

        m = re.match(r'^([a-z]+|[AR])$', text)
        if m:
            obj.action = lambda p: cls.workflows[m[1]](p)
            return obj

        raise ValueError(f"Cannot parse Action from: {text}")

    def __call__(self, part: MachinePart):
        dprint("....Executing", self, part)
        res = self.action(part)
        dprint("....Result:", res)
        return res

    def __repr__(self):
        return "<{}: text={}>".format(self.__class__.__name__, self.text)


def parse(lines: List[str]) -> Tuple[Dict[str, Workflow], List[MachinePart]]:
    """Parse a line of input into suitable data structure:
    """
    grps = group_lines(lines)
    workflows = [Workflow.from_text(line) for line in grps[0]]
    workflows.append(AcceptWorkflow())
    workflows.append(RejectWorkflow())
    workflows = {wf.name: wf for wf in workflows}
    parts = [MachinePart.from_text(line) for line in grps[1]]
    return workflows, parts


def solve_p1(args) -> int:
    """Solution to the 1st part of the challenge"""
    Action.workflows, parts = args
    #demo_workflows(Action.workflows)
    #demo_parts(parts)
    accepted_parts = []
    for part in parts:
        dprint("Processing part", part)
        res = Action.workflows["in"](part)
        dprint("Result of processing", res)
        if res:
            accepted_parts.append(part.rating())
    return sum(accepted_parts)


def solve_p2(lines: List[str]) -> int:
    """Solution to the 2nd part of the challenge"""
    return 0


def demo_workflows(workflows: Dict[str, Workflow]):
    # TODO: move this method to tests/
    for wf in workflows.values():
        print(wf)


def demo_parts(parts: List[MachinePart]):
    # TODO: move this method to tests/
    print("--- Demo Parts ---")
    for p in parts:
        print(p)
        print("Rating", p.rating())

    # select parts by x, that are accepted (test.1.txt)
    xs = [787, 2036, 2127]
    total = sum([p.rating() for p in parts if getattr(p, "x") in xs])
    expected_total = 19114
    print("Total rating of 3 accepted pieces", expected_total == total,
          expected_total, total)

tests = [
    (load_input('test.1.txt'), 7540+4623+6951, 167409079868000),
]


reals = [
    (load_input(), 401674, None)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
