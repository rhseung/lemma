import functools
from collections.abc import Callable, Iterator
from typing import Any

from scaffold import Edge, EdgeKind, UnweightedGraph, Vertex, Walk, WeightedGraph, WeightedPath
from scaffold.graph.primitives.weight import Weight


class _Traced[E: tuple]:
    """``@trace`` 로 wrap 된 traversal 함수.

    - ``.visits(g, s)``  — ``"visit"`` 이벤트의 정점 list
    - ``.walks(g, s)``   — ``"visit"`` 이벤트 parent 로 chain Walk list (DFS)
    - ``.levels(g, s)``  — ``"visit"`` 이벤트 level 로 그룹 list (BFS)
    - ``.path(g, s, t)`` — ``"relax"`` 이벤트로 최단 경로 재구성 (Dijkstra 등)
    """

    def __init__(self, fn: Callable[..., Iterator[E]]) -> None:
        self._fn = fn
        functools.update_wrapper(self, fn)

    def __call__(self, *args: Any, **kwargs: Any) -> Iterator[E]:
        return self._fn(*args, **kwargs)

    def visits(self, graph: Any, start: Vertex) -> list[Vertex]:
        return [args[0] for type_, *args in self._fn(graph, start) if type_ == "visit"]

    def walks(self, graph: UnweightedGraph, start: Vertex) -> list[Walk]:
        walks: list[Walk] = []
        current: list[Edge] = []
        for type_, *args in self._fn(graph, start):
            if type_ != "visit":
                continue
            u, parent = args[0], args[1] if len(args) > 1 else None
            if parent is None or isinstance(parent, int):
                continue
            if current and current[-1].dst != parent:
                walks.append(Walk(list(current)))
                current.clear()
            current.append(Edge(parent, u, EdgeKind.DIRECTED))
        if current:
            walks.append(Walk(current))
        return walks

    def levels(self, graph: UnweightedGraph, start: Vertex) -> list[Walk | UnweightedGraph]:
        by_level: dict[int, list[Vertex]] = {}
        for type_, *args in self._fn(graph, start):
            if type_ != "visit":
                continue
            u, level = args[0], args[1] if len(args) > 1 else None
            if not isinstance(level, int):
                continue
            by_level.setdefault(level, []).append(u)

        groups: list[Walk | UnweightedGraph] = []
        for lv in sorted(by_level):
            verts = by_level[lv]
            if len(verts) == 1:
                g = UnweightedGraph()
                g.add_vertex(verts[0])
                groups.append(g)
            else:
                edges = [
                    Edge(verts[i], verts[i + 1], EdgeKind.DIRECTED) for i in range(len(verts) - 1)
                ]
                groups.append(Walk(edges))
        return groups

    def path[W: (int, float)](
        self, graph: WeightedGraph[W], start: Vertex, end: Vertex
    ) -> WeightedPath[W]:
        pred: dict[Vertex, Vertex] = {}
        for type_, *args in self._fn(graph, start):
            if type_ == "relax":
                u, v = args[0], args[1]
                pred[v] = u
        path_verts: list[Vertex] = []
        v = end
        while v != start:
            if v not in pred:
                raise ValueError(f"No path from {start} to {end}")
            path_verts.append(v)
            v = pred[v]
        path_verts.append(start)
        path_verts.reverse()
        edges = [
            graph.get_edge(path_verts[i], path_verts[i + 1]) for i in range(len(path_verts) - 1)
        ]
        return WeightedPath(edges)


def trace[E: tuple](fn: Callable[..., Iterator[E]]) -> _Traced[E]:
    """textbook generator 에 ``.visits`` · ``.walks`` · ``.levels`` · ``.path`` helper 부여."""
    return _Traced(fn)


__all__ = ["_Traced", "trace"]
