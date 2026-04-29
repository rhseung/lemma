from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from core.graph.primitives.edge_kind import EdgeKind
from core.graph.primitives.vertex import Vertex
from core.graph.primitives.weight import Weight

if TYPE_CHECKING:
    from core.graph.walk import Walk, WeightedWalk


@dataclass(frozen=True)
class Edge:
    """두 정점 사이의 무가중 간선.

    방향성은 ``kind`` 로 결정된다. 불변 객체로, 해시 가능하다.

    연산자 오버로딩으로 워크(Walk)를 이어 붙일 수 있다::

        a, b, c = Vertex("a"), Vertex("b"), Vertex("c")
        edge = a - b  # Edge(a, b, UNDIRECTED)
        walk = edge - c  # Walk([a-b, b-c])

    Attributes:
        src: 출발 정점.
        dst: 도착 정점.
        kind: 간선의 방향성 종류.
    """

    src: Vertex
    dst: Vertex
    kind: EdgeKind

    def __sub__(self, other: Vertex) -> Walk:
        """``-`` 연산자로 동일 방향성의 다음 간선을 이어 붙여 ``Walk`` 를 반환한다."""
        from core.graph.walk import Walk

        match other:
            case Vertex():
                return Walk([self, Edge(self.dst, other, self.kind)])
            case _:
                return NotImplemented

    def __rshift__(self, other: Vertex) -> Walk:
        """``>>`` 연산자로 단방향 다음 간선을 이어 붙여 ``Walk`` 를 반환한다."""
        from core.graph.walk import Walk

        match other:
            case Vertex():
                return Walk([self, Edge(self.dst, other, EdgeKind.DIRECTED)])
            case _:
                return NotImplemented

    def __lshift__(self, other: Vertex) -> Walk:
        """``<<`` 연산자로 역방향 다음 간선을 이어 붙여 ``Walk`` 를 반환한다."""
        from core.graph.walk import Walk

        match other:
            case Vertex():
                return Walk([self, Edge(other, self.dst, EdgeKind.DIRECTED)])
            case _:
                return NotImplemented

    def __and__(self, other: Vertex) -> Walk:
        """``&`` 연산자로 양방향 다음 간선을 이어 붙여 ``Walk`` 를 반환한다."""
        from core.graph.walk import Walk

        match other:
            case Vertex():
                return Walk([self, Edge(self.dst, other, EdgeKind.BIDIRECTED)])
            case _:
                return NotImplemented

    def __repr__(self) -> str:
        return f"Edge({self.src} {self.kind.value} {self.dst})"

    def __str__(self) -> str:
        return f"{self.src} {self.kind.value} {self.dst}"


@dataclass(frozen=True)
class WeightedEdge[W: Weight]:
    """두 정점 사이의 가중 간선.

    ``weight`` 를 가진다는 점을 제외하면 ``Edge`` 와 동일하다.
    연산자 오버로딩으로 ``WeightedWalk`` 빌더를 생성할 수 있다::

        a, b, c = Vertex("a"), Vertex("b"), Vertex("c")
        edge = WeightedEdge(a, b, EdgeKind.UNDIRECTED, 3)
        builder = edge - 5  # _WeightedWalkBuilder(dst=b, weight=5, ...)
        walk = builder - c  # WeightedWalk([a-3-b, b-5-c])

    Attributes:
        src: 출발 정점.
        dst: 도착 정점.
        kind: 간선의 방향성 종류.
        weight: 간선의 가중치.
    """

    src: Vertex
    dst: Vertex
    kind: EdgeKind
    weight: W

    def __sub__(self, other: W) -> _WeightedWalkBuilder[W]:
        """``-`` 연산자로 다음 가중치를 받아 ``_WeightedWalkBuilder`` 를 반환한다."""
        match other:
            case Weight():
                return _WeightedWalkBuilder(self.dst, other, self.kind, [self])
            case _:
                return NotImplemented

    def __rshift__(self, other: W) -> _WeightedWalkBuilder[W]:
        """``>>`` 연산자로 단방향 다음 가중치를 받아 ``_WeightedWalkBuilder`` 를 반환한다."""
        match other:
            case Weight():
                return _WeightedWalkBuilder(self.dst, other, EdgeKind.DIRECTED, [self])
            case _:
                return NotImplemented

    def __lshift__(self, other: W) -> _WeightedWalkBuilder[W]:
        """``<<`` 연산자로 역방향 다음 가중치를 받아 ``_WeightedWalkBuilder`` 를 반환한다."""
        match other:
            case Weight():
                return _WeightedWalkBuilder(self.dst, other, EdgeKind.DIRECTED, [self])
            case _:
                return NotImplemented

    def __and__(self, other: W) -> _WeightedWalkBuilder[W]:
        """``&`` 연산자로 양방향 다음 가중치를 받아 ``_WeightedWalkBuilder`` 를 반환한다."""
        match other:
            case Weight():
                return _WeightedWalkBuilder(self.dst, other, EdgeKind.BIDIRECTED, [self])
            case _:
                return NotImplemented

    def __repr__(self) -> str:
        return f"WeightedEdge({self.src} {self.kind.value} {self.weight} {self.kind.value} {self.dst})"

    def __str__(self) -> str:
        return f"{self.src} {self.kind.value} {self.weight} {self.kind.value} {self.dst}"


@dataclass
class _WeightedEdgeBuilder[W: Weight]:
    """``Vertex - weight`` 표현식의 중간 빌더.

    출발 정점과 가중치를 보관하다가, 도착 정점을 받으면 ``WeightedEdge`` 를 완성한다::

        builder = Vertex("a") - 3  # _WeightedEdgeBuilder(src=a, weight=3)
        edge = builder - Vertex("b")  # WeightedEdge(a, b, UNDIRECTED, 3)

    Attributes:
        src: 출발 정점.
        weight: 간선에 부여할 가중치.
        kind: 간선의 방향성 종류.
    """

    src: Vertex
    weight: W
    kind: EdgeKind

    def __sub__(self, other: Vertex) -> WeightedEdge[W]:
        """``-`` 연산자로 도착 정점을 받아 무방향 ``WeightedEdge`` 를 완성한다."""
        match other:
            case Vertex():
                return WeightedEdge(self.src, other, self.kind, self.weight)
            case _:
                return NotImplemented

    def __rshift__(self, other: Vertex) -> WeightedEdge[W]:
        """``>>`` 연산자로 도착 정점을 받아 단방향 ``WeightedEdge`` 를 완성한다."""
        match other:
            case Vertex():
                return WeightedEdge(self.src, other, EdgeKind.DIRECTED, self.weight)
            case _:
                return NotImplemented

    def __lshift__(self, other: Vertex) -> WeightedEdge[W]:
        """``<<`` 연산자로 도착 정점을 받아 역방향 ``WeightedEdge`` 를 완성한다."""
        match other:
            case Vertex():
                return WeightedEdge(other, self.src, EdgeKind.DIRECTED, self.weight)
            case _:
                return NotImplemented

    def __and__(self, other: Vertex) -> WeightedEdge[W]:
        """``&`` 연산자로 도착 정점을 받아 양방향 ``WeightedEdge`` 를 완성한다."""
        match other:
            case Vertex():
                return WeightedEdge(self.src, other, EdgeKind.BIDIRECTED, self.weight)
            case _:
                return NotImplemented


@dataclass
class _WeightedWalkBuilder[W: Weight]:
    """``WeightedEdge - weight`` 표현식의 중간 빌더.

    기존 ``WeightedEdge`` 목록과 다음 가중치를 보관하다가,
    도착 정점을 받으면 ``WeightedWalk`` 를 완성한다::

        builder = (a - 3 - b) - 5  # _WeightedWalkBuilder(src=b, weight=5, prior=[a-3-b])
        walk = builder - c  # WeightedWalk([a-3-b, b-5-c])

    Attributes:
        src: 다음 간선의 출발 정점 (이전 간선의 도착 정점).
        weight: 다음 간선에 부여할 가중치.
        kind: 간선의 방향성 종류.
        _prior: 이미 완성된 ``WeightedEdge`` 목록.
    """

    src: Vertex
    weight: W
    kind: EdgeKind
    _prior: list[WeightedEdge[W]] = field(default_factory=list)

    def __sub__(self, other: Vertex) -> WeightedWalk[W]:
        """``-`` 연산자로 도착 정점을 받아 무방향 ``WeightedWalk`` 를 완성한다."""
        from core.graph.walk import WeightedWalk

        match other:
            case Vertex():
                return WeightedWalk(
                    [*self._prior, WeightedEdge(self.src, other, self.kind, self.weight)]
                )
            case _:
                return NotImplemented

    def __rshift__(self, other: Vertex) -> WeightedWalk[W]:
        """``>>`` 연산자로 도착 정점을 받아 단방향 ``WeightedWalk`` 를 완성한다."""
        from core.graph.walk import WeightedWalk

        match other:
            case Vertex():
                return WeightedWalk(
                    [*self._prior, WeightedEdge(self.src, other, EdgeKind.DIRECTED, self.weight)]
                )
            case _:
                return NotImplemented

    def __lshift__(self, other: Vertex) -> WeightedWalk[W]:
        """``<<`` 연산자로 도착 정점을 받아 역방향 ``WeightedWalk`` 를 완성한다."""
        from core.graph.walk import WeightedWalk

        match other:
            case Vertex():
                return WeightedWalk(
                    [*self._prior, WeightedEdge(other, self.src, EdgeKind.DIRECTED, self.weight)]
                )
            case _:
                return NotImplemented

    def __and__(self, other: Vertex) -> WeightedWalk[W]:
        """``&`` 연산자로 도착 정점을 받아 양방향 ``WeightedWalk`` 를 완성한다."""
        from core.graph.walk import WeightedWalk

        match other:
            case Vertex():
                return WeightedWalk(
                    [*self._prior, WeightedEdge(self.src, other, EdgeKind.BIDIRECTED, self.weight)]
                )
            case _:
                return NotImplemented
