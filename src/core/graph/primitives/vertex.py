from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, overload

from core.graph.primitives.edge_kind import EdgeKind

if TYPE_CHECKING:
    from core.graph.primitives.edge import Edge, _WeightedEdgeBuilder
    from core.graph.primitives.weight import Weight


@dataclass(frozen=True)
class Vertex:
    """그래프의 정점(노드).

    ``label`` 로 식별되는 불변 객체다. 동일한 ``label`` 을 가진 두 정점은 같은 정점으로 취급된다.

    연산자 오버로딩으로 간선과 경로를 직관적으로 표현할 수 있다::

        a, b, c = Vertex("a"), Vertex("b"), Vertex("c")

        a - b          # 무방향 간선 Edge(a, b, UNDIRECTED)
        a >> b         # 단방향 간선 Edge(a, b, DIRECTED)
        a << b         # 단방향 간선 Edge(b, a, DIRECTED)
        a & b          # 양방향 간선 Edge(a, b, BIDIRECTED)

        a - 3 - b      # 가중치 3인 무방향 간선 WeightedEdge(a, b, UNDIRECTED, 3)
        a >> 5 >> b    # 가중치 5인 단방향 간선 WeightedEdge(a, b, DIRECTED, 5)

    Attributes:
        label: 정점을 식별하는 문자열 레이블.
    """

    label: str

    @overload
    def __sub__(self, other: Vertex) -> Edge: ...
    @overload
    def __sub__[W: Weight](self, other: W) -> _WeightedEdgeBuilder[W]: ...

    def __sub__(self, other):
        """``-`` 연산자로 무방향 간선 또는 가중치 빌더를 생성한다.

        - ``Vertex - Vertex`` → 무방향 ``Edge``
        - ``Vertex - weight`` → 도착 정점을 기다리는 ``_WeightedEdgeBuilder``
        - ``Vertex - list[Vertex]`` / ``Vertex - VertexList`` → 스타 ``UnweightedGraph``
        """
        from core.graph.primitives.edge import Edge, _WeightedEdgeBuilder
        from core.graph.primitives.vertex_list import VertexList
        from core.graph.primitives.weight import Weight
        match other:
            case Vertex():
                return Edge(self, other, EdgeKind.UNDIRECTED)
            case Weight():
                return _WeightedEdgeBuilder(self, other, EdgeKind.UNDIRECTED)
            case list() | VertexList():
                from core.graph.graph.unweighted import UnweightedGraph
                g = UnweightedGraph()
                for v in other:
                    g.add_edge(self, v)
                return g
            case _:
                return NotImplemented

    @overload
    def __rshift__(self, other: Vertex) -> Edge: ...
    @overload
    def __rshift__[W: Weight](self, other: W) -> _WeightedEdgeBuilder[W]: ...

    def __rshift__(self, other):
        """``>>`` 연산자로 단방향(출발→도착) 간선 또는 가중치 빌더를 생성한다.

        - ``Vertex >> Vertex`` → 단방향 ``Edge``
        - ``Vertex >> weight`` → 도착 정점을 기다리는 ``_WeightedEdgeBuilder``
        """
        from core.graph.primitives.edge import Edge, _WeightedEdgeBuilder
        from core.graph.primitives.weight import Weight
        match other:
            case Vertex():
                return Edge(self, other, EdgeKind.DIRECTED)
            case Weight():
                return _WeightedEdgeBuilder(self, other, EdgeKind.DIRECTED)
            case _:
                return NotImplemented

    @overload
    def __lshift__(self, other: Vertex) -> Edge: ...
    @overload
    def __lshift__[W: Weight](self, other: W) -> _WeightedEdgeBuilder[W]: ...

    def __lshift__(self, other):
        """``<<`` 연산자로 단방향(도착→출발) 간선 또는 가중치 빌더를 생성한다.

        - ``Vertex << Vertex`` → 단방향 ``Edge`` (other → self 방향)
        - ``Vertex << weight`` → 도착 정점을 기다리는 ``_WeightedEdgeBuilder``
        """
        from core.graph.primitives.edge import Edge, _WeightedEdgeBuilder
        from core.graph.primitives.weight import Weight
        match other:
            case Vertex():
                return Edge(other, self, EdgeKind.DIRECTED)
            case Weight():
                return _WeightedEdgeBuilder(self, other, EdgeKind.DIRECTED)
            case _:
                return NotImplemented

    @overload
    def __and__(self, other: Vertex) -> Edge: ...
    @overload
    def __and__[W: Weight](self, other: W) -> _WeightedEdgeBuilder[W]: ...

    def __and__(self, other):
        """``&`` 연산자로 양방향 간선 또는 가중치 빌더를 생성한다.

        - ``Vertex & Vertex`` → 양방향 ``Edge``
        - ``Vertex & weight`` → 도착 정점을 기다리는 ``_WeightedEdgeBuilder``
        """
        from core.graph.primitives.edge import Edge, _WeightedEdgeBuilder
        from core.graph.primitives.weight import Weight
        match other:
            case Vertex():
                return Edge(self, other, EdgeKind.BIDIRECTED)
            case Weight():
                return _WeightedEdgeBuilder(self, other, EdgeKind.BIDIRECTED)
            case _:
                return NotImplemented

    def __repr__(self) -> str:
        return f"Vertex({self.label!r})"

    def __str__(self) -> str:
        return self.label


def vertices(*labels: str) -> list[Vertex]:
    """레이블 문자열로 ``Vertex`` 목록을 생성한다."""
    return [Vertex(label) for label in labels]
