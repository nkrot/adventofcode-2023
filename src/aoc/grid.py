import copy
from typing import Any, List, Tuple, Union, Callable
import networkx as nx

from .matrix import T_COORD, Matrix
from .point import Point
from .utils import dprint


class Grid2D:
    """
    The origin is in top left corner
    x axis goes topdown
    y axis goes from left to right

    Grid2D uses Matrix internally and provides a few methods to access
    positions in the matrix. These methods could equally go into the class
    Matrix itself. I dont know which is better.

    TODO:
    provide a default is_vertex: everything that is not `#`.
    >>> WALL = #
    >>> is_vertex = lambda c: c[1] != WALL
    """

    DXY = {
        "N": Point(-1,  0),  # up
        "S": Point( 1,  0),  # down
        "W": Point( 0, -1),  # to the left
        "E": Point( 0,  1),  # to the right
    }

    @classmethod
    def from_file(cls, path: str):
        with open(path) as fd:
            return cls.from_lines(map(str.strip, fd.readlines()))

    @classmethod
    def from_lines(cls, lines: List[str]):
        this = cls()
        chars = [list(line) for line in lines]
        this.matrix = Matrix(chars)
        return this

    def __init__(self):
        self.matrix = None
        self.__delegated_methods = [f for f in dir(Matrix)
                                    if not f.startswith('_')]

    def __str__(self):
        return self.matrix.__str__()

    def __len__(self):
        """Method __len__() cannot be delegated via __getattr__ because
        Python sucks: len() bypasses __getattr__ mechanism for reasons
        Python designers avoid admitting: the lack of brain"""
        return self.matrix.__len__()

    def __iter__(self):
        """See comment to __len__()"""
        return self.matrix.__iter__()

    def __getitem__(self, *args):
        """See comment to __len__()"""
        return self.matrix.__getitem__(*args)

    def __setitem__(self, *args):
        """See comment to __len__()"""
        return self.matrix.__setitem__(*args)

    def __getattr__(self, att):
        # TODO: this method complains about missing __copy__ and __deepcopy__
        # how to fix it w/o implementing __copy__ and __deepcopy__ or
        # implementing them the right way?
        # print(f"invoking method '{att}'")
        def method(*args, **kwargs):
            if att in self.__delegated_methods:
                return getattr(self.matrix, att)(*args, **kwargs)
            # elif att in ('__copy__', '__deepcopy__'):
            #     return getattr(super(),)
            else:
                raise AttributeError(
                    "'{}' object has no attribute '{}'".format(
                        self.__class__.__name__, str(att)))
        return method

    def __copy__(self):
        # TODO: adding this method because __getattr__ complains
        return self

    def __deepcopy__(self, memo):
        # adding this method because __getattr__ complains.
        # how can it be implemented?
        return self

    def neighbor_at(
        self, xy, offset: Union[str, Point, Tuple[int, int]]
    ) -> Tuple[T_COORD, Any]:
        """Return the cell that is located at `offset` from given
        position `xy`. Offset can be in either form:
        1) a tuple of ints [dx, dy]
        2) a string, one of the characters "N", "E", "S", "W" meaning
           "north", "east", "south" and "west"

        If applying offset results in a position outside of the grid,
        a coordnate and None value is returned. No error is raised.

        TODO:
        1) allow xy be similar to a tuple returned by this method,
           that is, Tuple[coordinate, value] ?
        """
        if isinstance(offset, str):
            s = offset.upper()
            if s not in self.DXY:
                raise ValueError(f"Invalid offset spec '{offset}', must be"
                                 f" one of {list(self.DXY.keys())}")
            offset = self.DXY[s]
        xy = Point(offset) + self.matrix.to_coord(xy)
        return self.matrix.to_coord(xy), self.matrix.get(xy)

    def neighbors_at(
        self, xy, spec: Union[str, List[Point]] = "NESW"
    ) -> List[Tuple[T_COORD, Any]]:
        """A shorthand to call neighbor_at() several times"""
        return [self.neighbor_at(xy, s) for s in spec]

#     def north_of(self, xy):
#         return self.neighbor_at(xy, self.DXY["N"])
#
#     def south_of(self, xy):
#         return self.neighbor_at(xy, self.DXY["S"])
#
#     def west_of(self, xy):
#         return self.neighbor_at(xy, self.DXY["W"])
#
#     def east_of(self, xy):
#         return self.neighbor_at(xy, self.DXY["E"])

    def to_graph(self, *args, **kwargs) -> nx.Graph:
        """Create and return a unidirected graph representing current grid
        """
        return graph_from_grid(self, *args, **kwargs)

    def to_digraph(self, *args, **kwargs) -> nx.DiGraph:
        """Create and return a directed graph representing current grid
        """
        return digraph_from_grid(self, *args, **kwargs)



def graph_from_grid(grid: Grid2D, is_vertex: Callable) -> nx.Graph:
    """Create unidirected graph from the selected cells of the grid.

    To decide whether a cell is a vertex in the graph (or should not be
    included as such), the predicate `is_vertex` is used. The predicate
    accepts two arguments: a tuple of ints (representing a coordinate
    of the cell) and the content of the cell (can be any object).

    Edges are created between grid cells that are located in north, east,
    south and west directions of each cell. Diagonal directions are not
    considered.

    Returns:
      A unidirected graph (networkx.Graph)
    """
    vertices = [grid.to_1d(tile[0]) for tile in grid if is_vertex(tile)]
    g = nx.Graph()
    g.add_nodes_from(vertices)
    for u in g.nodes():
        for nbor in grid.neighbors_at(u, "NESW"):
            v = grid.to_1d(nbor[0])
            if g.has_node(v):
                g.add_edge(u, v)
    return g


def digraph_from_grid(
    grid: Grid2D,
    root: Union[Tuple[int, int], Point],
    is_vertex: Callable
) -> nx.DiGraph:
    """Not finished

    Create directed graph from given `grid` starting at position `root`.
    NWES cells are considered only.

    Algorithm:
    Starting at position `root`, traverse the grid in BFS manner, adding
    new vertices (located NESW) and directed edges.

    TODO: allow creating cycles in the graph A -> B -> C -> A ?
    TODO: allow creating a multigraph? what if some cells are not reachable
    from the starting point `root`?
    """
    raise NotImplementedError("Not fully implemented")
    edges = []
    heads: List[Point] = [root]
    visited = []
    while heads:
        node = heads.pop(0)
        visited.append(node)
        for nbor in grid.neighbors_at(node, "NESW"):
            dprint("neighbor", nbor)
            if is_vertex(nbor) and nbor[0] not in visited:
                dprint("..continue")
                heads.append(nbor[0])
                edges.append((node, nbor[0]))
    dprint("Edges (initial)", len(edges), edges)
    # simplify edge end representation
    edges = [
        (grid.to_1d(start), grid.to_1d(end))
        for start, end in edges
    ]
    dprint("Edges (simplified)", len(edges), edges)
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g


# Reading
# delegation
# https://erikscode.space/index.php/2020/08/01/delegate-and-decorate-in-python-part-1-the-delegation-pattern/
# https://www.peterbe.com/plog/must__deepcopy__
