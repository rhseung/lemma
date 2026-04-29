from core.graph.graph import FlowGraph, Graph, UnweightedGraph, WeightedGraph
from core.graph.primitives import Edge, EdgeKind, FlowEdge, Vertex, Weight, WeightedEdge
from core.graph.walk import Path, Trail, Walk, WeightedWalk


def vertices(*labels: str) -> list[Vertex]:
    return [Vertex(label) for label in labels]


__all__ = [
    "Edge",
    "EdgeKind",
    "FlowEdge",
    "FlowGraph",
    "Graph",
    "Path",
    "Trail",
    "UnweightedGraph",
    "Vertex",
    "Walk",
    "WeightedEdge",
    "WeightedGraph",
    "WeightedWalk",
    "Weight",
    "vertices",
]
