#!/usr/bin/env python

# # #
#
#

import re
import os
import sys
from typing import List, Union
from dataclasses import dataclass
from collections import Counter
from itertools import product

from aoc.utils import load_input, run_tests, run_real, to_numbers

DAY = '07'
DEBUG = int(os.environ.get('DEBUG', 0))


class Card:
    RANKS = "_23456789TJQKA"  # low to high

    def __init__(self, src: Union[str, 'Card']):
        if isinstance(self, type(src)):
            self.label: str = src.label
        else:
            self.label: str = src

    @property
    def strength(self) -> int:
        return self.RANKS.index(self.label) + 1

    def __lt__(self, other: 'Card') -> bool:
        return self.strength < other.strength

    def __eq__(self, other: 'Card') -> bool:
        return self.label == other.label

    def __repr__(self):
        return "<{}: label={} strength={}>".format(
            self.__class__.__name__, self.label, self.strength)


class JokerCard(Card):
    #RANKS = "J23456789TQKA"  # low to high

    @property
    def strength(self) -> int:
        """Regardless of the label, the strength of the Joker is constant
        and is the lowest.
        """
        return 1


@dataclass
class Hand:
    cards: List[Card]
    bid: int
    strength: int = None
    rank: int = 0

    def __iter__(self):
        return iter(self.cards)

    def win(self):
        return self.rank * self.bid

    def __lt__(self, other: 'Hand') -> bool:
        ts1, ts2 = self._set_strength(), other._set_strength()
        if ts1 < ts2:
            return True
        elif ts1 == ts2:
            for a, b in zip(self.cards, other.cards):
                if a != b:
                    return a < b
        return False

    def _set_strength(self) -> int:
        """Compute and set hand type strength if not yet set.
        If already set, use existing value.

        Returns
          int: hand type strength
        """
        if self.strength is None:
            self.strength = self.compute_strength()

        return self.strength

    def compute_strength(self) -> int:
        """Compute hand strength based on the available cards and
        return it (without setting).
        """
        counts = Counter(self.label)
        c_diff = len(counts)
        c_most_common = counts.most_common(1)[0][1]
        # print(c_diff, counts)

        strength = 0
        if c_diff == 1:
            strength = 7  # five of a kind
        elif c_most_common == 4:
            strength = 6  # four of a kind
        elif c_diff == 2 and c_most_common == 3:
            strength = 5  # full house
        elif c_most_common == 3:
            strength = 4  # three of a kind
        elif c_diff == 3:
            strength = 3  # two pair
        elif c_most_common == 2:
            strength = 2  # one pair
        elif c_diff == 5:
            strength = 1  # high card
        if DEBUG:
            print("Strength", strength, self.label(), self)
        return strength

    @property
    def label(self):
        return "".join(card.label for card in self.cards)


class JokerHand(Hand):
    """A hand of cards with special Joker logic"""

    def __init__(self, src = None, **kwargs):
        if isinstance(self, type(src)):
            super().__init__(cards=src.cards, bid=src.bid)
            self.strength: int = src.strength
            self.rank: int = src.rank
        else:
            # not tested
            super().__init__(**kwargs)

    def compute_strength(self) -> int:
        """Compute hand strength based on the available cards and
        return it (without setting). Joker card receives a special
        treatment.
        """
        jokers, normal_cards = [], []
        for card in self.cards:
            if isinstance(card, JokerCard):
                jokers.append(card)
            else:
                normal_cards.append(card)

        counts = Counter(card.label for card in normal_cards)
        c_diff = len(counts)
        c_jks = len(jokers)
        c_most_common = counts.most_common(1)[0][1] if c_diff else 0

        if DEBUG:
            print(c_diff, counts)

        strength = 0
        if c_diff == 1 or c_jks == 5:
            strength = 7  # five of a kind
        elif c_most_common == 4 - c_jks:
            strength = 6  # four of a kind
        elif c_diff == 2 and c_most_common == 3 - c_jks:
            strength = 5  # full house
        elif c_most_common == 3 - c_jks:
            strength = 4  # three of a kind
        elif c_diff == 3:
            strength = 3  # two pair
        elif c_most_common == 2 - c_jks:
            strength = 2  # one pair
        elif c_diff == 5 - c_jks :
            strength = 1  # high card
        if DEBUG:
            print("Strength", strength, self.label(), self)
        return strength


def play_joker(hand: Hand):
    """
    In joker game, joker card can pretend it is a different card and thus
    increase type strength of a hand.

    Here we try to find the best card the joker can be and set
    Hand.strength to the best value.

    This is a very stupid approach.
    """
    max_strength = hand.compute_strength()

    jokers = []
    for idx, card in enumerate(hand):
        if isinstance(card, JokerCard):
            jokers.append(card)

    #print(jokers)

    if jokers:
        for labels in set(product(*[Card.RANKS[1:]]*len(jokers))):
            # print(len(labels), labels)
            for card, new_label in zip(jokers, labels):
                card.label = new_label
            new_strength = hand.compute_strength()
            if new_strength > max_strength:
                max_strength = new_strength

        # Restore the original label of JokerCard to ensure Hand strength
        # is computed correctly when card strengths come into play.
        for card in jokers:
            card.label = "J"

    hand.strength = max_strength


def parse(line: str) -> Hand:
    """Parse a line of input into suitable data structure"""
    fields = line.strip().split()
    cards = [Card(ch) for ch in fields[0]]
    hand = Hand(cards=cards, bid=int(fields[1]))
    return hand


def solve_p1(hands: List[Hand]) -> int:
    """Solution to the 1st part of the challenge"""
    hands = sorted(hands)
    for r, hand in enumerate(hands):
        hand.rank = 1+r
    if DEBUG:
        for hand in hands:
            print(hand)
    res = sum(hand.win() for hand in hands)
    return res


def solve_p2(*args) -> int:
    return solve_p2_v2(*args)


def solve_p2_v2(hands: List[Hand]) -> int:

    for hand in hands:
        hand.cards = [
            JokerCard(card) if card.label == 'J' else card
            for card in hand
        ]
    hands = [JokerHand(hand) for hand in hands]

    return solve_p1(hands)


def solve_p2_v1(hands: List[Hand]) -> int:
    """Solution to the 2nd part of the challenge"""

    # convert joker cards to a JokerCard that have a different behaviour
    for hand in hands:
        hand.cards = [
            JokerCard(card) if card.label == 'J' else card
            for card in hand
        ]
        # print_hand(hand)
        play_joker(hand)

    return solve_p1(hands)


def print_hand(hand):
    """TODO: something beautiful"""
    print(hand)


tests = [
    (load_input('test.1.txt', line_parser=parse),
     765 * 1 + 220 * 2 + 28 * 3 + 684 * 4 + 483 * 5, 5905),
]


reals = [
    (load_input(line_parser=parse), 250946742, 251824095)
]


if __name__ == '__main__':
    run_tests(DAY, tests, solve_p1, solve_p2)
    run_real(DAY, reals, solve_p1, solve_p2)
