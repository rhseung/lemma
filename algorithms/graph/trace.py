"""Traversal 이벤트 + ``@trace`` 데코레이터.

textbook 알고리즘은 ``(event_type, *args)`` 형태의 튜플만 yield 하면 된다.
``@trace`` 가 ``.visits`` · ``.walks`` · ``.levels`` · ``.path`` 시각화 helper 를 자동 부여한다.

## 이벤트 형식

| 알고리즘 | yield 형식 |
|---------|-----------|
| DFS | ``("visit", u, parent: Vertex \\| None)`` |
| BFS | ``("visit", u, level: int)`` |
| Dijkstra / Bellman-Ford | ``("visit", u, dist: float)``, ``("relax", u, v, new_dist: float)`` |
| Kruskal / Prim | ``("add_edge", u, v, w)``, ``("skip_edge", u, v, w)`` |

## helper 메서드 ↔ 이벤트 대응

| 메서드 | 소비하는 이벤트 |
|-------|----------------|
| ``.visits()`` | ``("visit", u, _)`` |
| ``.walks()`` | ``("visit", u, parent: Vertex)`` |
| ``.levels()`` | ``("visit", u, level: int)`` |
| ``.path()`` | ``("relax", u, v, new_dist)`` |
"""

import functools
from collections.abc import Callable, Iterator
from typing import Any, Literal

from core import Edge, EdgeKind, UnweightedGraph, Vertex, Walk, WeightedGraph, WeightedPath

# ── per-algorithm event types ────────────────────────────────────────────────

type DFSEvent = tuple[Literal["visit"], Vertex, Vertex | None]
type BFSEvent = tuple[Literal["visit"], Vertex, int]
type DijkstraEvent = (
    tuple[Literal["visit"], Vertex, float]
    | tuple[Literal["relax"], Vertex, Vertex, float]
)

# generic fallback — use the specific aliases above in algorithm files
type TraversalEvent = tuple
type TraversalFn[E: tuple] = Callable[..., Iterator[E]]


class _Traced[E: tuple]:
    """``@trace`` 로 wrap 된 traversal 함수.

    - ``.visits(g, s)``     — ``"visit"`` 이벤트의 정점 list
    - ``.walks(g, s)``      — ``"visit"`` 이벤트 parent 로 chain Walk list (DFS)
    - ``.levels(g, s)``     — ``"visit"`` 이벤트 level 로 그룹 list (BFS)
    - ``.path(g, s, t)``    — ``"relax"`` 이벤트로 최단 경로 재구성 (Dijkstra 등)
    """

    def __init__(self, fn: Callable[..., Iterator[E]]) -> None:
        self._fn = fn
        functools.update_wrapper(self, fn)

    def __call__(self, *args: Any, **kwargs: Any) -> Iterator[E]:
        """원본 generator — raw 이벤트 stream."""
        return self._fn(*args, **kwargs)

    def visits(self, graph: Any, start: Vertex) -> list[Vertex]:
        """``"visit"`` 이벤트만 골라 정점 list 반환 (방문 순서).

        DFS / BFS / Dijkstra 모두 사용 가능.
        """
        return [
            args[0]
            for type_, *args in self._fn(graph, start)
            if type_ == "visit"
        ]

    def walks(self, graph: UnweightedGraph, start: Vertex) -> list[Walk]:
        """``"visit"`` 이벤트 parent (``Vertex | None``) → chain 단위 Walk list.

        이전 간선 ``dst`` 와 새 ``parent`` 가 다르면 chain 끊김.
        DFS 결과 시각화 (chain-based) 에 적합.
        """
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

    def levels(
        self, graph: UnweightedGraph, start: Vertex
    ) -> list[Walk | UnweightedGraph]:
        """``"visit"`` 이벤트 level (``int``) → level 그룹 list.

        같은 level 정점들은 synthetic Walk (ghost edge 점선) 로, 단일 정점 level 은
        UnweightedGraph 로 감싼다. BFS 결과 시각화 (level-based) 에 적합.
        """
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
                    Edge(verts[i], verts[i + 1], EdgeKind.DIRECTED)
                    for i in range(len(verts) - 1)
                ]
                groups.append(Walk(edges))
        return groups

    def path[W: (int, float)](
        self, graph: WeightedGraph[W], start: Vertex, end: Vertex
    ) -> WeightedPath[W]:
        """``"relax"`` 이벤트로 최단 경로 재구성.

        Dijkstra / Bellman-Ford 에서 ``("relax", u, v, new_dist)`` 를 수집해
        predecessor map 을 만들고 ``end`` 에서 ``start`` 로 역추적한다.
        """
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
            graph.get_edge(path_verts[i], path_verts[i + 1])
            for i in range(len(path_verts) - 1)
        ]
        return WeightedPath(edges)


def trace[E: tuple](fn: Callable[..., Iterator[E]]) -> _Traced[E]:
    """textbook generator 에 ``.visits`` · ``.walks`` · ``.levels`` · ``.path`` helper 부여.

    원본 함수는 ``(event_type, *args)`` 튜플을 yield 하면 된다.
    """
    return _Traced(fn)
