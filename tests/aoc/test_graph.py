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

@pytest.fixture
def dag_1():
    """Graph that is constructed from test.1.txt"""
    edges = [(1, 2), (1, 3),
             (2, 4), (2, 5),
             (3, 4), (3, 5),
             (4, 6),
             (5, 6),
             (6, 7)]
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g

@pytest.fixture
def dag_2():
    edges = [
        (10, 12),
        (11, 13),
        (12, 14), (12, 15),
        (13, 15), (13, 16),
    ]
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g

@pytest.fixture
def dag_3():
    edges = [
        (1, 3), (1, 5),
        (2, 3),
        (3, 4),
        (4, 6),
        (5, 6)
    ]
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g

@pytest.fixture
def dag_1_2(dag_1, dag_2):
    return nx.compose(dag_1, dag_2)


# def test_draw_graph(dag_3):
#     draw_graph(dag_3, "tests.dag_3.png")

# def OFF_test_draw_graph(graph_1, graph_2):
#     graph.draw_graph(graph_1, "tests.graph.1.png")
#     graph.draw_graph(graph_2, "tests.graph.2.png")


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

def test_dag_1(dag_1):
    assert list(dag_1.nodes()) == [1, 2, 3, 4, 5, 6, 7]

def test_count_descendants_dag_1(dag_1):
    exp_counts = {
        1: len([2, 3, 4, 5, 6, 7]),
        2: len([4, 5, 6, 7]),
        3: len([4, 5, 6, 7]),
        4: len([6, 7]),
        5: len([6, 7]),
        6: len([7]),
        7: len([]),
    }
    counts = graph.count_descendants(dag_1)
    assert exp_counts == counts


def test_count_descendants_dag_2(dag_2):
    exp_counts = {
        10: len([12, 14, 15]),
        11: len([13, 15, 16]),
        12: len([14, 14]),
        13: len([15, 16]),
        14: len([]),
        15: len([]),
        16: len([]),
    }
    counts = graph.count_descendants(dag_2)
    assert exp_counts == counts


def test_count_descendants_dag_1_2(dag_1_2):
    exp_counts = {
        1: len([2, 3, 4, 5, 6, 7]),
        2: len([4, 5, 6, 7]),
        3: len([4, 5, 6, 7]),
        4: len([6, 7]),
        5: len([6, 7]),
        6: len([7]),
        7: len([]),
        10: len([12, 14, 15]),
        11: len([13, 15, 16]),
        12: len([14, 14]),
        13: len([15, 16]),
        14: len([]),
        15: len([]),
        16: len([]),
    }
    counts = graph.count_descendants(dag_1_2)
    assert exp_counts == counts


def test_count_descendants_dag_3(dag_3):
    exp_counts = {
        1: len([3, 4, 5, 6]),
        2: len([3, 4, 6]),
        3: len([4, 6]),
        4: len([6]),
        5: len([6]),
        6: len([]),
    }
    counts = graph.count_descendants(dag_3)
    assert exp_counts == counts
