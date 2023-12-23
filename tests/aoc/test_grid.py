import networkx as nx
import pytest

from aoc import Grid2D


@pytest.fixture
def grid_01(datadir):
    return Grid2D.from_file(datadir / "grid.01.txt")


def test_load_grid_01(grid_01):
    assert isinstance(grid_01, Grid2D)
    assert (3, 6) == grid_01.shape()

def test_find_cell(grid_01):
    cell = grid_01.find(lambda t: t == '.')
    assert ((0, 1), ".") == cell

@pytest.mark.parametrize(
    "start,offset,expected",
    [
        # north of: outside of the grid
        ((0, 0), (-1, 0), ((-1, 0), None)),
        ((0, 0), "n",     ((-1, 0), None)),
        # south of
        ((0, 0), (1, 0),  ((1, 0), "#")),
        ((0, 0), "s",     ((1, 0), "#")),
        # east of
        ((0, 0), (0, 1),  ((0, 1), ".")),
        ((0, 0), "e",     ((0, 1), ".")),
        # west of: outside of the grid
        ((0, 0), (0, -1), ((0, -1), None)),
        ((0, 0), "w",     ((0, -1), None)),
    ]
)
def test_grid_01_neighbor_at(start, offset, expected, grid_01):
    cell = grid_01.neighbor_at(start, offset)
    assert expected == cell


def test_grid_01_to_graph(grid_01):
    exp_nodes = [1,7,8,9,10,16]
    exp_edges = [(1,7), (7,8), (8,9), (9,10), (10,16)]
    g = grid_01.to_graph(lambda c: c[1] == ".")
    assert isinstance(g, nx.Graph)
    assert exp_nodes == list(g.nodes())
    assert exp_edges == list(g.edges())

# TODO
# neighbors_at()
