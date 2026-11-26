"""Audit enumeration of simple undirected graphs using pynauty."""

from __future__ import annotations

from collections.abc import Iterable
from math import comb, factorial
from operator import index
from typing import TYPE_CHECKING

from .. import OrbitAudit, orbit_completeness

if TYPE_CHECKING:
    from pynauty import Graph


def _graph_edges(graph: Graph, n_vertices: int) -> set[tuple[int, int]]:
    if (
        type(graph.number_of_vertices) is not int
        or graph.number_of_vertices != n_vertices
    ):
        raise ValueError(f"each graph must have {n_vertices} vertices")
    if graph.directed or graph.vertex_coloring:
        raise ValueError("expected a simple uncolored undirected graph")

    # The undirected pynauty constructor interprets either direction as the
    # same edge. Normalize indices before constructing a plain pynauty graph.
    def valid_vertex(vertex):
        return type(vertex) is int and 0 <= vertex < n_vertices

    edges = set()
    for source, neighbors in graph.adjacency_dict.items():
        if not valid_vertex(source):
            raise ValueError("graph vertices must be integer indices in range")
        for target in neighbors:
            if not valid_vertex(target):
                raise ValueError("graph vertices must be integer indices in range")
            if source == target:
                raise ValueError("simple graphs cannot contain loops")
            edges.add((min(source, target), max(source, target)))
    return edges


def audit_pynauty_graphs(
    graphs: Iterable[Graph],
    n_vertices: int,
    *,
    edge_count: int | None = None,
) -> OrbitAudit:
    """Audit representatives of simple undirected graphs on up to 13 vertices.

    The expected total counts all labeled graphs, or those with exactly
    edge_count edges. Orders come from the exact unscaled portion of
    pynauty's automorphism group-size report. Treat graph representatives as
    pairwise non-isomorphic when interpreting a complete result.
    """
    import pynauty

    n_vertices = index(n_vertices)
    if not 0 <= n_vertices <= 13:
        raise ValueError(
            "pynauty audit requires 0 through 13 vertices for exact group orders"
        )
    possible_edges = comb(n_vertices, 2)
    if edge_count is not None:
        edge_count = index(edge_count)
        if not 0 <= edge_count <= possible_edges:
            raise ValueError(f"edge count must be between 0 and {possible_edges}")
    expected = (
        1 << possible_edges if edge_count is None else comb(possible_edges, edge_count)
    )
    group_order = factorial(n_vertices)

    def stabilizer_orders():
        for graph in graphs:
            if not isinstance(graph, pynauty.Graph):
                raise TypeError("expected pynauty.Graph instances")
            edges = _graph_edges(graph, n_vertices)
            if edge_count is not None and len(edges) != edge_count:
                raise ValueError(f"each graph must have edge count {edge_count}")
            if n_vertices == 0:
                yield 1
                continue

            # nauty scales at 10**10. Up to 13!, all intermediate products
            # are exact binary64 integers below that threshold (and 2**53).
            adjacency = {}
            for source, target in edges:
                adjacency.setdefault(source, []).append(target)
            normalized = pynauty.Graph(n_vertices, adjacency_dict=adjacency)
            _, mantissa, exponent, _, _ = pynauty.autgrp(normalized)
            if (
                exponent != 0
                or not mantissa.is_integer()
                or not 0 < mantissa <= group_order
            ):
                raise ValueError("pynauty did not return an exact group order")
            order = int(mantissa)
            if group_order % order != 0:
                raise ValueError(
                    "pynauty group order does not divide the permutation group order"
                )
            yield order

    return orbit_completeness(group_order, stabilizer_orders(), expected)
