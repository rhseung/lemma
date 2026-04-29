from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, overload

from core.graph.primitives.edge_kind import EdgeKind

if TYPE_CHECKING:
    from core.graph.graph.flow import FlowGraph
    from core.graph.graph.unweighted import UnweightedGraph
    from core.graph.graph.weighted import WeightedGraph
    from core.graph.primitives.weight import Weight
    from core.graph.walk import Walk, WeightedWalk


class Graph:
    """워크로부터 적절한 그래프 구현체를 생성하는 팩토리.

    ``WeightedWalk`` 를 받으면 ``WeightedGraph``, ``flow=True`` 를 주면 ``FlowGraph``,
    그 외에는 ``UnweightedGraph`` 를 반환한다::

        a, b, c = Vertex("a"), Vertex("b"), Vertex("c")

        Graph(a - b - c)  # UnweightedGraph
        Graph(a - 3 - b - 2 - c)  # WeightedGraph[int]
        Graph(a >> 10 >> b, flow=True)  # FlowGraph
        Graph(kind=EdgeKind.DIRECTED)  # 빈 단방향 UnweightedGraph
        Graph(flow=True)  # 빈 FlowGraph
    """

    @overload
    def __new__[W: Weight](cls, walk: WeightedWalk[W], *, flow: Literal[True]) -> FlowGraph[W]: ...
    @overload
    def __new__(cls, walk: WeightedWalk | None = ..., *, flow: Literal[True]) -> FlowGraph: ...
    @overload
    def __new__[W: Weight](cls, walk: WeightedWalk[W]) -> WeightedGraph[W]: ...
    @overload
    def __new__(cls, walk: Walk | None = ..., *, kind: EdgeKind = ...) -> UnweightedGraph: ...

    def __new__(cls, walk=None, *, kind=EdgeKind.UNDIRECTED, flow=False) -> Any:
        from core.graph.graph.flow import FlowGraph
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.graph.weighted import WeightedGraph
        from core.graph.primitives.edge import Edge, WeightedEdge
        from core.graph.walk import Walk, WeightedWalk

        if flow:
            if isinstance(walk, WeightedEdge):
                walk = WeightedWalk([walk])
            return FlowGraph(walk)

        match walk:
            case WeightedEdge():
                walk = WeightedWalk([walk])
            case Edge():
                walk = Walk([walk])

        match walk:
            case WeightedWalk():
                return WeightedGraph(walk, kind=kind)
            case _:
                return UnweightedGraph(walk, kind=kind)

    @classmethod
    def from_edge_list(cls, edges: list, *, kind: EdgeKind = EdgeKind.UNDIRECTED) -> Any:
        """간선 목록으로 그래프를 생성한다. 튜플 길이가 3이면 ``WeightedGraph``, 2이면 ``UnweightedGraph``."""
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.graph.weighted import WeightedGraph

        if edges and len(edges[0]) == 3:
            return WeightedGraph.from_edge_list(edges, kind=kind)
        return UnweightedGraph.from_edge_list(edges, kind=kind)

    @classmethod
    def from_dot(cls, s: str) -> Any:
        """DOT 문자열에서 그래프를 복원한다. 간선에 ``label``이 있으면 ``WeightedGraph``."""
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.graph.weighted import WeightedGraph
        from core.graph.io import _parse_dot

        _, _, edges = _parse_dot(s)
        if any(w is not None for _, _, w in edges):
            return WeightedGraph.from_dot(s)
        return UnweightedGraph.from_dot(s)

    @classmethod
    def from_json(cls, s: str) -> Any:
        """JSON 문자열에서 그래프를 복원한다. ``type`` 필드로 구현체를 결정한다."""
        import json

        from core.graph.graph.flow import FlowGraph
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.graph.weighted import WeightedGraph

        match json.loads(s).get("type"):
            case "WeightedGraph":
                return WeightedGraph.from_json(s)
            case "FlowGraph":
                return FlowGraph.from_json(s)
            case _:
                return UnweightedGraph.from_json(s)

    @classmethod
    def from_adjacency_matrix(
        cls, m: list[list], labels: list[str] | None = None, *, kind: EdgeKind = EdgeKind.UNDIRECTED
    ) -> Any:
        """인접 행렬에서 그래프를 생성한다. ``None`` 값이 있으면 ``WeightedGraph``."""
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.graph.weighted import WeightedGraph

        if any(val is None for row in m for val in row):
            return WeightedGraph.from_adjacency_matrix(m, labels, kind=kind)
        return UnweightedGraph.from_adjacency_matrix(m, labels, kind=kind)
