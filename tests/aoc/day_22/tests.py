import networkx as nx
import pytest

from aoc import graph
from aoc.day_22 import count_chain_destruction


@pytest.fixture
def dag_1():
    edges = [
        (1, 3), (1, 4),
        (2, 4),
        (4, 5)
    ]
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g


@pytest.fixture
def dag_2():
    edges = [
        (1, 3), (1, 4),
        (2, 4),
        (3, 6),
        (4, 5),
        (5, 6)
    ]
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g


# def test_draw_graphs(dag_1, dag_2):
#     graph.draw_graph(dag_1, "tests.dag_1.png")
#     graph.draw_graph(dag_2, "tests.dag_2.png")


@pytest.mark.parametrize(
    "dag,expected", [
    ("dag_1", 1+1),  # 1:3, 4:5
    ("dag_2", 1+1),  # 1:3, 4:5
])
def test_count_chain_destruction(dag, expected, request):
    dag = request.getfixturevalue(dag)
    assert expected == count_chain_destruction(dag)
