from typing import Callable

import networkx as nx


def _empty_generator():
    yield from ()


def all_simple_paths(g: nx.Graph, start, end, is_valid_edge: Callable = None):
    """
    This function is a reimplementation of `all_simple_paths` from
    https://networkx.org/documentation/stable/_modules/networkx/algorithms/simple_paths.html#all_simple_paths
    extended to accept an additional argument to test the edge.

    `is_valid_edge()` is function that accepts 3 arguments: u, v and dictionary
    where dictionary if edge data (G.edges[u, v]). It is implemented like this
    to imitate `weight` parameter of astar (https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.astar.astar_path.html#networkx.algorithms.shortest_paths.astar.astar_path)
    """
    if start not in g:
        raise nx.NodeNotFound(f"start node {start} not in graph")
    if end not in g:
        raise nx.NodeNotFound(f"end node {end} not in graph")

    if start == end:
        return _empty_generator()

    return _all_simple_paths_in_graph(g, start, end, is_valid_edge)


def OK_all_simple_paths_in_graph(g: nx.Graph, start, end, visited):
    """my own implementation (recursive)
    TODO: add support for is_valid_edge
    """
    if start in visited:
        return _empty_generator()
    if start == end:
        yield list(visited) + [end]
    else:
        visited.append(start)
        for child in g[start]:
            yield from _all_simple_paths_in_graph(g, child, end, visited)
        visited.pop()


def _all_simple_paths_in_graph(
    g: nx.Graph, start, end, is_valid_edge: Callable = None
):
    """
    Adaptation of _all_simple_paths_graph() from this page
    https://networkx.org/documentation/stable/_modules/networkx/algorithms/simple_paths.html#all_simple_paths
    """
    # print(f"\npaths between {start} and {end}?")
    visited = {start: True}
    queue = [iter(g[start])]
    while queue:
        children = queue[-1]
        child = next(children, None)
        # print(f"child: {child}")
        # print(f"visited: {visited}")
        if child is None:
            queue.pop()
            visited.popitem()
        else:
            if child in visited:
                continue
            if is_valid_edge is not None:
                parent = list(visited)[-1]
                if not is_valid_edge(parent, child, g.edges[parent, child]):
                    continue
            if child == end:
                yield list(visited) + [child]
            else:
                visited[child] = True
                queue.append(iter(g[child]))
