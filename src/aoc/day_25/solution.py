"""Solution for Day 25 (AoC 2023)

TODO

https://www.tutorialspoint.com/graph_theory/graph_theory_connectivity.htm
https://networkx.org/documentation/stable/reference/algorithms/connectivity.html#module-networkx.algorithms.connectivity.kcutsets

"""

import os
import re
from typing import Dict, List, Tuple

import networkx as nx

from aoc import utils
from aoc.graph import draw_graph
from aoc.utils import dprint

DAY = '25'
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


def parse(lines: List[str]) -> nx.Graph:
    """Parse a line of input into suitable data structure"""
    g = nx.Graph()
    for line in lines:
        vs = re.split(r'[:\s]+', line)
        u = vs.pop(0)
        # dprint(u, vs, list(zip([u]*len(vs), vs)))
        g.add_edges_from(zip([u]*len(vs), vs))
    # draw_graph(g, "graph.test.1.png")
    return g


def solve_p1(g: nx.Graph) -> int:
    """Solution to the 1st part of the challenge"""
    g.remove_edges_from(nx.minimum_edge_cut(g))
    connected_components = list(nx.connected_components(g))
    return utils.prod(len(nodes) for nodes in connected_components)


def solve_p2(lines: List[str]) -> int:
    """Solution to the 2nd part of the challenge"""
    return 0


tests = [
    (load_input('test.1.txt'), 9*6, None),
]


reals = [
    (load_input(), 551196, None)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
