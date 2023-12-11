#!/usr/bin/env python

# # #
#
#

import re
import os
from typing import List, Tuple, Any, Union

from aoc import utils
from aoc.utils import to_numbers, dprint


DAY = '05'
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


class Map:

#    @classmethod
#    def from_string(cls, text: str, name: str):
#        obj = cls()
#        obj.name = name
#        dest, src, length = to_numbers(text.split())
#        obj.source = range(src, src+length)
#        obj.destination = range(dest, dest+length)
#        return obj

    def __init__(self, name: str):
        self.name: str = name
        # ranges [start, end] both ends included
        self._sources: List[Tuple[int, int]] = []
        self._destinations: List[Tuple[int, int]] = []

    def add_from_string(self, text: str):
        dest, src, length = to_numbers(text.split())
        self._sources.append(range(src, src+length))
        self._destinations.append(range(dest, dest+length))

    def add(self, src: Tuple[int, int], dest: Tuple[int, int] = None):
        if src:
            start, length = src
            self._sources.append(range(start, start+length))
        if dest:
            raise NotImplementedError("when necessary")

    def __contains__(self, n: int) -> bool:
        """Check if given number is contained in any of the ranges on
        the source side.
        """
        for src in self._sources:
            if n in src:
                return True
        return False

    def __getitem__(self, idx: int) -> int:
        return self.forward(idx)

    def forward(self, idx: int) -> int:
        for src, dest in zip(self._sources, self._destinations):
            try:
                jdx = src.index(idx)
                return dest[jdx]
            except ValueError:
                pass
        return idx

    def backward(self, idx: int) -> int:
        for src, dest in zip(self._sources, self._destinations):
            try:
                jdx = dest.index(idx)
                return src[jdx]
            except ValueError:
                pass
        return idx

#    def destinations(self):
#        """Iterator over destinations in sorted order"""
#        for dest in sorted(self._destinations, key=lambda r: r.start):
#            yield from dest

    def destmin(self):
        first = sorted(self._destinations, key=lambda r: r.start)[0]
        return first.start

    def destmax(self):
        last = sorted(self._destinations, key=lambda r: -r.start)[0]
        return last.stop

    def srcmin(self):
        first = sorted(self._sources, key=lambda r: r.start)[0]
        return first.start

    def srcmax(self):
        last = sorted(self._sources, key=lambda r: -r.start)[0]
        return last.stop

    def __repr__(self):
        return "<{}: name='{}' sources={} destinations={}>".format(
            self.__class__.__name__, self.name, self._sources,
            self._destinations
        )


def parse(lines: List[str]) -> List[Tuple[str, Union[List[int], Map]]]:
    """Parse a line of input into suitable data structure:

    TODO:
    1) no need to have a tuple and store category name (mapping.name).
       get rid of it
    """
    items = []
    for line in lines:
        line = line.strip()
        #print(line)
        if line.startswith("seeds:"):
            numbers = to_numbers(line.split(' ')[1:])
            items.append(("seeds", numbers))
        elif line.endswith(' map:'):
            mapping = Map(line)
            items.append((mapping.name, mapping))
        elif re.match(r'\d+(\s+\d+)+', line):
            items[-1][1].add_from_string(line)
    if DEBUG:
        for item in items:
            print(item)
    return items


def do_test_1(items):
    """Seeds to soil"""
    mapping = items[1][1] # aka "seed-to-soil map"
    for seed, exp_soil in [(79, 81), (14, 14), (55, 57), (13, 13)]:
        soil = mapping[seed]
        print(seed, exp_soil, soil, exp_soil == soil)


def do_test_2(items):
    seeds_and_locations = [(79, 82), (14, 43), (55, 86), (13, 35)]
    for exp_seed, exp_location in seeds_and_locations:
        loc = get_location(exp_seed, items[1:])
        print("seed-to-location",
            exp_seed, exp_location == loc, exp_location, loc)

        seed = get_seed(exp_location, items[1:])
        print("location-to-seed",
            exp_location, exp_seed == seed, exp_seed, seed)


def get_location(seed: int, mappings: List[Tuple[str, Map]]):
    """Let a seed go through the sieves in forward direction"""
    n = seed
    for _, mapping in mappings:
        n = mapping.forward(n)
    return n


def get_seed(location: int, mappings: List[Tuple[str, Map]]):
    """Let a seed go through the sieves in backward direction"""
    n = location
    for _, mapping in reversed(mappings):
        n = mapping.backward(n)
    return n


def solve_p1(items: List[Tuple]) -> int:
    """Solution to the 1st part of the challenge"""
    #do_test_1(items)
    #do_test_2(items)

    seeds = items.pop(0)[-1]
    locations = []
    for seed in seeds:
        locations.append(get_location(seed, items))

    return min(locations)


def solve_p2(items: List[Tuple]) -> int:
    """Solution to the 2nd part of the challenge"""
    name, seeds = items.pop(0)


    seeds_mapping = Map(name)
    for i in range(0, len(seeds), 2):
        start, length = seeds[i], seeds[1+i]
        seeds_mapping.add((start, length))

    if DEBUG:
        # print(seeds_mapping)
        print(seeds_mapping.name, seeds_mapping.srcmin(), seeds_mapping.srcmax())
        for _, mapping in items:
            print(mapping.name, mapping.destmin(), mapping.destmax())

    # Q: What is the lowest location number that corresponds to any of
    #    the initial seed numbers?

    max_loc = items[-1][-1].destmax()

    # for 5.2 it runs 40min on my computer and around 4 minutes with pypy
    for loc in range(max_loc):
        seed = get_seed(loc, items)
        dprint(loc, seed, seed in seeds_mapping)
        if seed in seeds_mapping:
            dprint(f"..min loc {loc} from {seed}")
            return loc


tests = [
    (load_input('test.1.txt'), 35, 46),
]


reals = [
    (load_input(), 227_653_707, 78_775_051)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
