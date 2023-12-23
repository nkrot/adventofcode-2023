from collections import defaultdict
from typing import Any, Dict

import networkx as nx


def count_descendants(g: nx.DiGraph) -> Dict[Any, int]:
    """Count the number of all unique descendants of all vertices.
    Descendants are not only direct successors but also successors of
    successors till the leaf vertices.
    """
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
