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


@pytest.fixture
def graph_2():
    # circular graph
    edges = [(1,2), (2,3), (3,4), (4,5), (5,6), (6,7), (7,8), (8,9), (9,1)]
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


def test_contract_edges_in_graph_1(graph_1):
    g = graph.contract_edges(graph_1)
    exp_nodes = set(graph_1.nodes()) - {5, 7}
    exp_edges = [
        (1, 2, {}),
        (2, 3, {}), (2, 6, {'length': 2}),
        # (2, 5), -- deleted
        (3, 4, {}), (3, 6, {}),
        (4, 6, {}), (4, 8, {}),
        # (5, 6), -- deleted
        # (6, 7), -- deleted
        (6, 8, {'length': 2}),
        #(7, 8), -- deleted
        (8, 9, {})
    ]
    # print(g.nodes())
    # print(g.edges(data=True))
    assert sorted(exp_nodes) == sorted(g.nodes())
    assert sorted(exp_edges) == sorted(g.edges(data=True))


def test_contract_edges_in_graph_2(graph_2):
    g = graph.contract_edges(graph_2, [1, 5, 7])
    exp_nodes = [1, 5, 7]
    exp_edges = [
        (1, 5, {'length': 4}),
        (5, 7, {'length': 2}),
        (1, 7, {'length': 3}),
    ]
    # print(g.nodes())
    # print(g.edges(data=True))
    assert sorted(exp_nodes) == sorted(g.nodes())
    assert sorted(exp_edges) == sorted(g.edges(data=True))


# Unclear cases
# 1) graph.contract_edges(graph_2, [1,5]) (graph_2 is circular) will create
#    a graph with just two nodes [1, 5] and only one edge, though logically
#    there are two edges 1-[2,3,4]->5 and 5-[6,7,8,9]->1. Now that a single
#    edge remains, what should length be: 4 or 5?

# contract_edges() needs more tests

def OFF_test_draw_graph(graph_1, graph_2):
    graph.draw_graph(graph_1, "tests.graph.1.png")
    graph.draw_graph(graph_2, "tests.graph.2.png")
