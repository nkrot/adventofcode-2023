from collections import defaultdict
from typing import Any, Callable, Dict, List

import matplotlib.pyplot as plt
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


def draw_graph(g, outfile = "graph.png"):
    if not outfile.endswith((".png", ".PNG")):
        outfile += ".png"

    opts = dict(
        with_labels = True,
        width = 0.4,
        node_color = 'lightblue',
        node_size = 200,
        #node_shape = "s",
        font_size = 8, # for smaller labels

    )
    plt.figure(figsize=(10,10))
    #nx.draw(g, **opts)
    #nx.draw(g, pos=nx.spring_layout(g, k=1.5), **opts) beautiful but useless
    nx.draw_planar(g, **opts) # looks interesting, suitable for 23
    plt.savefig(outfile)


def contract_edges(g: nx.Graph, protected_vertices: list = None):
    """Remove vertices that have exaclty one incoming and outgoing edge
    creating an edges between neightboring vertices (skip connection).
    A modified copy of the graph is returned. The original graph is not
    modified.

    Returns
    a new simpler graph
    """
    if isinstance(g, nx.Graph):
        return _contract_edges_in_graph(g, protected_vertices)
    raise NotImplementedError("contract_edges() not implemented for {type(g)}")


def _contract_edges_in_graph(
    srcg: nx.Graph,
    protected_vertices: list = None
) -> nx.Graph:
    """
    TODO: write something here
    sets length attribute to edges

    Algorithm
    ----------
    [p - previous, m - middle, n - next]
    Inspect triples of vertices (p, m, n) and remove m (middle) iff there
    exists exactly one edge (p, m) and exactly one edge (m, n)
    """
    g = srcg.copy()
    changed = True
    while changed:
        changed = False
        for m in list(g.nodes()):
            if not g.has_node(m):  # already deleted
                continue
            if protected_vertices and m in protected_vertices:
                continue
            nbors = list(g.neighbors(m))
            if len(nbors) == 2:
                p, n = nbors
                lengths = [g.edges[p, m].get('length', 1),
                           g.edges[m, n].get('length', 1)]
                g.remove_node(m)
                g.add_edge(p, n, length=sum(lengths))
                # BUG: in case of a graph with loops, adding an edge may
                # override an existing edge.
                changed = True
    return g


def _contract_edges_in_digraph(srcdg: nx.DiGraph):
    """Not fully implemented/tested"""
    print("--- Simplify Graph ---")
    dg = srcdg.copy()
    changed = True
    while changed:
        print("--- inspecting the graph ---")
        changed = False
        for a in list(dg.nodes()):
            if not dg.has_node(a):
                continue
            bs = list(dg.predecessors(a))
            for b in bs:
                if len(list(dg.successors(b))) != 1:
                    continue
                cs = list(dg.predecessors(b))
                print(f"{a} <- {bs} <- {cs}")
                for c in cs:
                    edge = (c, a)
                    print(f"..removing vertex {b}; adding edge ({edge})")
                    dg.add_edge(*edge)
                    changed = True
                if changed:
                    dg.remove_node(b)
    print(srcdg)
    print(dg)
    return dg


def get_disconnected_subgraphs(g: nx.DiGraph) -> List[nx.DiGraph]:
    """If given directed graph contains several graphs not connected by
    at least one edge (edge direction does not matter), return subgraphs
    as a list.

    TODO:
    1) does NetworksX has anything suitable for this purpose?
    2) Not tested. This functionality was initially designed for day23p2
       but turned out to be unused for the final solution.
    3) Do not do anything if there is only one graph. Instead, return it
       in a list of one element.
    4) Return a generator instead of list? because many functions in networkx
       return a generator.
    5) For undirected graph, the same can be done using nx.connected_components()
    """
    subgraphs = []
    for idx, vertices in enumerate(nx.weakly_connected_components(g)):
        subg = type(g)()
        subg.add_nodes_from(vertices)
        for v in vertices:
            subg.add_edges_from(g.edges(v))
        subgraphs.append(subg)
        # draw_graph(subg, f"subgraph.dg.{idx}.png")
    return subgraphs


def count_descendants(g: nx.DiGraph) -> Dict[Any, int]:
    """Count the number of all unique descendants of all vertices.
    Descendants are not only direct successors but also successors of
    successors till the leaf vertices.

    seems that the function works for disconnected graphs (a graph with
    disconnected subgraphs)
    """
    assert isinstance(g, nx.DiGraph), f"Wrong type: {type(g)}"
    nodes = defaultdict(set)
    ordered_vertices = list(nx.topological_sort(g))
    for u in reversed(ordered_vertices):
        # method 1
        # descendants = list(nx.descendants(g, u))
        # nodes[u].update(descendants)
        # method 2
        successors = list(g.successors(u))
        nodes[u].update(successors)
        for s in successors:
            nodes[u].update(nodes[s])
    nodes = {
        u: len(vs)
        for u, vs in nodes.items()
    }
    return nodes
