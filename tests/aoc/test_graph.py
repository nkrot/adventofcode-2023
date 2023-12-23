import networkx as nx
import pytest

from aoc import graph

@pytest.fixture
def graph_1():
    edges = [
        (1, 2),
        (2, 3), (2, 5),
        (3, 4), (3, 6),
        (4, 6), (4, 8),
        (5, 6),
        (6, 7),
        (7, 8),
        (8, 9)
    ]
    g = nx.Graph()
    g.add_edges_from(edges)
    return g


def test_graph_1(graph_1):
    assert sorted(graph_1.nodes()) == list(range(1, 10))


def test_all_simple_paths_same_start_and_end(graph_1):
    assert list(graph.all_simple_paths(graph_1, 2, 2)) == []


def test_all_simple_paths_1(graph_1):
    exp_paths = [
        [1,2,5,6, 7,8,9],
        [1,2,5,6, 4,8,9],
        [1,2,5,6, 3,4,8,9],

        [1,2,3, 6, 7,8,9],
        [1,2,3, 6, 4,8,9],

        [1,2,3, 4, 6,7,8,9],
        [1,2,3, 4, 8,9]
    ]
    paths = list(graph.all_simple_paths(graph_1, 1, 9))
    # for exp_path in exp_paths:
    #     if exp_path not in paths:
    #         print(f"Missing: {exp_path}")
    assert len(exp_paths) == len(paths)
    assert sorted(exp_paths) == sorted(paths)


def test_all_simple_paths_with_edge_selector(graph_1):
    exp_paths = [
        [1,2,5,6, 7,8,9],
        # [1,2,5,6, 4,8,9],
        # [1,2,5,6, 3,4,8,9],

        [1,2,3, 6, 7,8,9],
        # [1,2,3, 6, 4,8,9],

        [1,2,3, 4, 6,7,8,9],
        [1,2,3, 4, 8,9]
    ]

    def is_valid_edge(u, v, d) -> bool:
        # print(f"Validating edge: {(u, v), d}")
        return u < v

    paths = list(graph.all_simple_paths(graph_1, 1, 9, is_valid_edge))
    # for exp_path in exp_paths:
    #     if exp_path not in paths:
    #         print(f"Missing: {exp_path}")

    assert len(exp_paths) == len(paths)
    assert sorted(exp_paths) == sorted(paths)
