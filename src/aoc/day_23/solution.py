#!/usr/bin/env python

# # #
#
#

import os
from collections import Counter
from typing import Callable, List

from aoc import Direction, Grid2D, Point, utils
from aoc.graph import all_simple_paths, draw_graph, contract_edges
from aoc.utils import dprint

DAY = '23'
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
    return utils.load_input(fname, parser=Plan.from_lines)


class Plan(Grid2D):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._entrance = None
        self._exit = None

    @property
    def entrance(self):
        if self._entrance is None:
            self._entrance, _ = self.find(lambda t: t == '.')
        return self._entrance

    @property
    def exit(self):
        if self._exit is None:
            self._exit, _ = self.findall(lambda t: t == '.')[-1]
        return self._exit

    @classmethod
    def is_walkable_tile(cls, tile) -> bool:
        """Check if given tile on the Plan is walkable."""
        xy, value = tile  # Union[Tuple[int, int], Point], str
        res = bool(value and value != "#")
        # dprint(f"is walkable? {tile} -> {res}")
        return res

    @classmethod
    def is_path_tile(cls, tile: str) -> bool:
        # TODO: allow testing tiles goven in the form Tuple[T_COORD, value] ?
        # and just T_COORD (2D or 1D)?
        return tile == "."

    @classmethod
    def is_slope_tile(cls, tile: str) -> bool:
        return tile in '<>^v'


def visualize_path(plan, path):
    for step in path:
        plan[step] = "O"
    print(plan)


def check_path(path: List[int], plan: Plan):
    """Useful for debugging"""
    # does the path contain repeating nodes?
    counts = Counter(path)
    for item, cnt in counts.items():
        if cnt != 1:
            print(f"Vertex {item} occurs {cnt} times")


def solve(
    plan: Plan,
    graph_edge_selector: Callable = None,
    contract_graph: bool = False
) -> int:
    """Common code for both parts.

    `graph_edge_selector` is a function (predicate) that evaluates an edge and
    tells whether it should or should not be included in the path. It is used
    in the 1st part to given preference to slope tiles (<>v^).

    `contract_graph` is a boolean flag that controls whether a heuristics
    should be used to simplify the graph. Using this heuristics considerably
    improves running time but does not work for part 1.
    This heuristic can be used for the part 2.

    Algorithm
    ----------
    From the plan, build a undirected graph that represents walkable tiles.
    Then generate all possible paths from the entrance to the exist points.
    At this point `graph_edge_selector` is used to test all edges (pairs of
    tiles).
    Finally, select the longest path.

    Learnings and TODOs
    -------------------
    1) if there an algorithm for finding the longest path between two vertices
       in a graph without generating *all* paths? There is an algorithm for
       finding a longest path in a graph but it does not have a constraint
       that start and end vertices are given.
    2) A* does not help here because the graph is not directed.
    3) Initially, I used directed graph from the grid. It took me time to
       understand that it is undirected graph. When debugging, it was helful
       to visualize the graph (drawing it as an image) and simplify the graph
       by removing edges with a single incoming and outgoing edge, such that
       the sequence A -> B -> C -> D is converted to just A -> D.
       This is performed by `aoc.graph.contract_edges()`
    4) When producing all paths in the graph between (entrance, exit), it is
       necessary to use generators. On the opposite, using lists results
       in high memory consumption to the point that the script is terminated.
    """
    dprint(plan)
    dprint("Entrance/Exit points:", plan.entrance, plan.exit)

    start = plan.to_1d(plan.entrance)
    end = plan.to_1d(plan.exit)

    # WRONG! directed graph as constructed here does not even provide the
    # desired path. The latter consists of direct and reversed edges.
    #g = plan.to_digraph(plan.entrance, Plan.is_walkable_tile)
    g = plan.to_graph(is_vertex = Plan.is_walkable_tile)
    # print(g)

    # To make computation faster, we will contract long paths into a single
    # edge with `length` attribute set to the number of original edges in it.
    # However, this should be done with care in part 1 that has special
    # treatment of Slopes (namely, the tiles around slope tiles should also
    # be kept so that the moving direction is computed correctly, see
    # `graph_edge_selector`). For now, it is safer to operate on the original
    # graph in part 1.
    if contract_graph:
        g = contract_edges(g, protected_vertices = {start, end})
        #draw_graph(g, "graph.simplified.png")

    # be careful: materializing the list may consume lots of memory
    # paths = list(all_simple_paths(g, start, end, edge_selector))
    # for idx, path in enumerate(paths):
    #     print(f"Path #{idx} (#vertices={len(path)}) {path}")
    #     # check_path(path, plan)
    #     # visualize_path(plan, path)

    def compute_path_length(path: list):
        """If heusristics `contract_graph` was applied, the working graph
        is much smaller than the original graph. We compute the length
        by checking lengths of the edges.
        """
        edges = zip(path, path[1:])
        length = sum(g.edges[u, v].get('length', 1) for u, v in edges)
        return length

    lengths = [
        compute_path_length(path)
        for path in all_simple_paths(g, start, end, graph_edge_selector)
    ]

    return max(lengths)


def solve_p1(plan: Plan) -> int:
    """Solution to the 1st part of the challenge"""

    def must_follow_slopes(u, v, d) -> bool:
        """Decide if we want to go from `u` to `v`.

        If the vertex `u` is not a slope ("."), we can go to `v`.
        If the vertex `u` is a slope (<>v^), then we can go to `v` iff
        the direction between `u` and `v` corresponds to the slope direction.
        """
        u_xy, v_xy = plan.to_coord(u), plan.to_coord(v)
        # normal tile or slope tile
        u_type, v_type = plan[u_xy], plan[v_xy]
        dprint(f"Inspecting the edge {(u, v, d)}: u={(u_xy, u_type)} v={(v_xy, v_type)}")
        if Plan.is_path_tile(u_type):
            dprint("..not a slope => go? {True}")
            return True
        if Plan.is_slope_tile(u_type):
            # determine the direction of the edge between vertices (u, v)
            dxy = Point(v_xy) - u_xy
            drct = Direction(dxy)
            # and compare it to the slope direction
            choose = drct == u_type
            dprint(f"..direction u->v: '{drct}' (dxy={dxy}) same? {drct == u_type} => go? {choose}")
            return choose

    return solve(plan, must_follow_slopes)


def solve_p2_v1(plan: Plan) -> int:
    """Solution to the 2nd part of the challenge that is based on the solution
    to the 1st part. It does not use `graph_edge_selector` because the slopes
    have no special treatment.

    It works. However, it takes circa 20 minutes to run (pypy).
    """
    return solve(plan)


def solve_p2_v2(plan: Plan) -> int:
    """Solution to the 2nd part of the challenge that is based on the solution
    to the 1st part. It does not use `graph_edge_selector` because the slopes
    have no special treatment.

    With some heuristics (contract_graph=True), running time reduces
    from 20 minutes to 7s using pypy and 40s using python.
    """
    return solve(plan, contract_graph=True)


def solve_p2(*args) -> int:
    return solve_p2_v2(*args)


tests = [
    (load_input('test.1.txt'), 94, 154),
]

reals = [
    (load_input(), 2394, 6554)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
