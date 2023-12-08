#!/usr/bin/env python

# # #
#
#

import re
import os
import sys
from typing import List, Tuple
from dataclasses import dataclass
from operator import attrgetter

from aoc.utils import load_input, run_tests, run_real, to_numbers

DAY = '04'
DEBUG = int(os.environ.get('DEBUG', 0))


@dataclass
class Card:
    winning_numbers: List[int]
    my_numbers: List[int]
    count: int = 1  # how many instances of this card is available


def parse(line: str) -> Card:
    """Parse a line of input into suitable data structure"""
    parts = re.split(r'\s*[:|]\s*', line)
    numbers = [to_numbers(p.split()) for p in parts[1:]]
    return Card(winning_numbers=numbers[0], my_numbers=numbers[1])


def solve_p1(cards: List[Card]) -> int:
    """Solution to the 1st part of the challenge"""
    total = 0
    for card in cards:
        common = set(card.winning_numbers) & set(card.my_numbers)
        if common:
            worth = 2 ** (len(common) - 1)
            total += worth
    return total


def solve_p2(cards: List[Card]) -> int:
    """Solution to the 2nd part of the challenge"""
    for idx, card in enumerate(cards):
        common = set(card.winning_numbers) & set(card.my_numbers)
        for j in range(1, 1+len(common)):
            i = idx + j
            if i < len(cards):
                cards[i].count += card.count
    total = sum(map(attrgetter("count"), cards))
    return total


tests = [
    (load_input('test.1.txt', line_parser=parse), 13, 30),
]


reals = [
    (load_input(line_parser=parse), 22193, 5625994)
]


if __name__ == '__main__':
    run_tests(DAY, tests, solve_p1, solve_p2)
    run_real(DAY, reals, solve_p1, solve_p2)
