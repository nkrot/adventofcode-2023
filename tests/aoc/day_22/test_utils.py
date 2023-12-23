import pytest
import networkx as nx

from aoc.day_22 import count_descendants


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
def dag_1_2(dag_1, dag_2):
    return nx.compose(dag_1, dag_2)


def test_digraph_1(dag_1):
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
    counts = count_descendants(dag_1)
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
    counts = count_descendants(dag_2)
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
    counts = count_descendants(dag_1_2)
    assert exp_counts == counts
