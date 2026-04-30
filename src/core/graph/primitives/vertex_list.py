from __future__ import annotations

from typing import TYPE_CHECKING

from core.graph.primitives.vertex import Vertex

if TYPE_CHECKING:
    from core.graph.graph.unweighted import UnweightedGraph


class VertexList:
    """정점 묶음. ``-`` 연산자로 일괄 간선 생성을 지원한다.

    단일 출발 정점에서 여러 도착 정점으로 향하는 스타 간선, 또는
    두 집합 사이의 완전 이분 간선을 한 표현식으로 생성할 수 있다::

        a, b, c, d = Vertex("a"), Vertex("b"), Vertex("c"), Vertex("d")

        a - vs(b, c, d)         # a-b, a-c, a-d
        vs(a, b) - vs(c, d)     # a-c, a-d, b-c, b-d  (완전 이분)
        [a, b] - vs(c, d)       # 위와 동일 (plain list 왼쪽 피연산자)
    """

    def __init__(self, *vertices: Vertex) -> None:
        self._vertices: list[Vertex] = list(vertices)

    @staticmethod
    def _collect(other: object) -> list[Vertex] | None:
        match other:
            case Vertex():
                return [other]
            case VertexList():
                return other._vertices
            case list():
                return other
            case _:
                return None

    def __sub__(self, other: object) -> UnweightedGraph:
        from core.graph.graph.unweighted import UnweightedGraph

        rights = VertexList._collect(other)
        if rights is None:
            return NotImplemented  # type: ignore[return-value]
        g = UnweightedGraph()
        for u in self._vertices:
            for v in rights:
                g.add_edge(u, v)
        return g

    def __rsub__(self, other: object) -> UnweightedGraph:
        """``[A, B] - vs(C, D)`` — plain list가 왼쪽 피연산자일 때 호출된다."""
        from core.graph.graph.unweighted import UnweightedGraph

        lefts = VertexList._collect(other)
        if lefts is None:
            return NotImplemented  # type: ignore[return-value]
        g = UnweightedGraph()
        for u in lefts:
            for v in self._vertices:
                g.add_edge(u, v)
        return g

    def __iter__(self):
        return iter(self._vertices)

    def __len__(self) -> int:
        return len(self._vertices)

    def __repr__(self) -> str:
        return f"vs({', '.join(str(v) for v in self._vertices)})"


def vs(*vertices: Vertex) -> VertexList:
    """``VertexList`` 생성 헬퍼."""
    return VertexList(*vertices)
