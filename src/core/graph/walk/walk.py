from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from core.graph.primitives.edge import Edge, WeightedEdge, _WeightedWalkBuilder
from core.graph.primitives.edge_kind import EdgeKind
from core.graph.primitives.vertex import Vertex
from core.graph.primitives.weight import Weight

if TYPE_CHECKING:
    from core.graph.graph.unweighted import UnweightedGraph
    from core.graph.graph.weighted import WeightedGraph


@dataclass
class Walk:
    """정점과 간선의 순서열. 정점·간선 중복을 모두 허용하는 가장 일반적인 경로 표현.

    ``Trail`` (간선 비중복) 과 ``Path`` (정점·간선 비중복) 의 부모 클래스다.
    간선 목록으로부터 생성되며, 모든 간선은 동일한 방향성을 가져야 하고
    연속된 간선끼리 연결되어 있어야 한다::

        a, b, c = Vertex("a"), Vertex("b"), Vertex("c")
        walk = a - b - c     # Walk([a-b, b-c])

    Attributes:
        edges: 워크를 구성하는 간선 목록.
        kind: 워크에 속한 간선들의 방향성 종류 (자동 설정).
    """

    edges: list[Edge]
    kind: EdgeKind = field(init=False)

    def __post_init__(self) -> None:
        if not self.edges:
            raise ValueError("Walk must contain at least one edge")
        for i in range(len(self.edges) - 1):
            if self.edges[i].dst != self.edges[i + 1].src:
                raise ValueError("Edges in a walk must be connected")
            if self.edges[i].kind != self.edges[i + 1].kind:
                raise ValueError("All edges in a walk must have the same kind")
        self.kind = self.edges[0].kind
        self._validate()

    def _validate(self) -> None:
        """서브클래스에서 추가 제약 조건을 검증한다. 기본 구현은 아무것도 하지 않는다."""
        pass

    @property
    def length(self) -> int:
        """워크의 길이 (간선 수)."""
        return len(self.edges)

    @property
    def vertices(self) -> list[Vertex]:
        """워크에 포함된 정점 목록 (순서대로, 중복 포함)."""
        return [self.edges[0].src, *(e.dst for e in self.edges)]

    @property
    def is_closed(self) -> bool:
        """시작 정점과 끝 정점이 같으면 ``True`` (닫힌 워크)."""
        return self.edges[0].src == self.edges[-1].dst

    def as_graph(self) -> UnweightedGraph:
        """이 워크를 ``UnweightedGraph`` 로 변환한다."""
        from core.graph.graph.unweighted import UnweightedGraph
        return UnweightedGraph(self)

    def __sub__(self, other: Vertex) -> Walk:
        """``-`` 연산자로 동일 방향성의 다음 정점을 이어 붙여 새로운 ``Walk`` 를 반환한다."""
        match other:
            case Vertex():
                return Walk([*self.edges, Edge(self.edges[-1].dst, other, self.kind)])
            case _:
                return NotImplemented

    def __rshift__(self, other: Vertex) -> Walk:
        """``>>`` 연산자로 단방향 다음 정점을 이어 붙여 새로운 ``Walk`` 를 반환한다."""
        match other:
            case Vertex():
                return Walk([*self.edges, Edge(self.edges[-1].dst, other, EdgeKind.DIRECTED)])
            case _:
                return NotImplemented

    def __lshift__(self, other: Vertex) -> Walk:
        """``<<`` 연산자로 역방향 다음 정점을 이어 붙여 새로운 ``Walk`` 를 반환한다."""
        match other:
            case Vertex():
                return Walk([*self.edges, Edge(other, self.edges[-1].dst, EdgeKind.DIRECTED)])
            case _:
                return NotImplemented

    def __and__(self, other: Vertex) -> Walk:
        """``&`` 연산자로 양방향 다음 정점을 이어 붙여 새로운 ``Walk`` 를 반환한다."""
        match other:
            case Vertex():
                return Walk([*self.edges, Edge(self.edges[-1].dst, other, EdgeKind.BIDIRECTED)])
            case _:
                return NotImplemented

    def __repr__(self) -> str:
        return f"Walk({self})"

    def __str__(self) -> str:
        ret = str(self.edges[0])
        for edge in self.edges[1:]:
            ret += f" {edge.kind.value} {edge.dst}"
        return ret


@dataclass
class WeightedWalk[W: Weight]:
    """정점과 가중 간선의 순서열. 정점·간선 중복을 모두 허용하는 가장 일반적인 가중 경로 표현.

    ``Walk`` 의 가중치 버전으로, 각 간선마다 가중치를 가진다.
    연산자 오버로딩으로 가중치를 포함한 경로를 직관적으로 표현할 수 있다::

        a, b, c = Vertex("a"), Vertex("b"), Vertex("c")
        walk = a - 3 - b - 2 - c   # WeightedWalk([a-3-b, b-2-c])
        walk.weight                 # 5

    Attributes:
        edges: 워크를 구성하는 가중 간선 목록.
        kind: 워크에 속한 간선들의 방향성 종류 (자동 설정).
    """

    edges: list[WeightedEdge[W]]
    kind: EdgeKind = field(init=False)

    def __post_init__(self) -> None:
        if not self.edges:
            raise ValueError("WeightedWalk must contain at least one edge")
        for i in range(len(self.edges) - 1):
            if self.edges[i].dst != self.edges[i + 1].src:
                raise ValueError("Edges in a walk must be connected")
            if self.edges[i].kind != self.edges[i + 1].kind:
                raise ValueError("All edges in a walk must have the same kind")
        self.kind = self.edges[0].kind

    @property
    def length(self) -> int:
        """워크의 길이 (간선 수)."""
        return len(self.edges)

    @property
    def weight(self) -> W:
        """워크에 포함된 모든 간선의 가중치 합계."""
        total = self.edges[0].weight
        for e in self.edges[1:]:
            total = total + e.weight
        return total

    @property
    def vertices(self) -> list[Vertex]:
        """워크에 포함된 정점 목록 (순서대로, 중복 포함)."""
        return [self.edges[0].src, *(e.dst for e in self.edges)]

    @property
    def is_closed(self) -> bool:
        """시작 정점과 끝 정점이 같으면 ``True`` (닫힌 워크)."""
        return self.edges[0].src == self.edges[-1].dst

    def as_graph(self) -> WeightedGraph[W]:
        """이 가중 워크를 ``WeightedGraph`` 로 변환한다."""
        from core.graph.graph.weighted import WeightedGraph
        return WeightedGraph(self)

    def __sub__(self, other: W) -> _WeightedWalkBuilder[W]:
        """``-`` 연산자로 다음 가중치를 받아 ``_WeightedWalkBuilder`` 를 반환한다."""
        match other:
            case Weight():
                last = self.edges[-1]
                return _WeightedWalkBuilder(last.dst, other, self.kind, list(self.edges))
            case _:
                return NotImplemented

    def __rshift__(self, other: W) -> _WeightedWalkBuilder[W]:
        """``>>`` 연산자로 단방향 다음 가중치를 받아 ``_WeightedWalkBuilder`` 를 반환한다."""
        match other:
            case Weight():
                last = self.edges[-1]
                return _WeightedWalkBuilder(last.dst, other, EdgeKind.DIRECTED, list(self.edges))
            case _:
                return NotImplemented

    def __lshift__(self, other: W) -> _WeightedWalkBuilder[W]:
        """``<<`` 연산자로 역방향 다음 가중치를 받아 ``_WeightedWalkBuilder`` 를 반환한다."""
        match other:
            case Weight():
                last = self.edges[-1]
                return _WeightedWalkBuilder(last.dst, other, EdgeKind.DIRECTED, list(self.edges))
            case _:
                return NotImplemented

    def __and__(self, other: W) -> _WeightedWalkBuilder[W]:
        """``&`` 연산자로 양방향 다음 가중치를 받아 ``_WeightedWalkBuilder`` 를 반환한다."""
        match other:
            case Weight():
                last = self.edges[-1]
                return _WeightedWalkBuilder(last.dst, other, EdgeKind.BIDIRECTED, list(self.edges))
            case _:
                return NotImplemented

    def __repr__(self) -> str:
        return f"WeightedWalk({self})"

    def __str__(self) -> str:
        ret = str(self.edges[0])
        for edge in self.edges[1:]:
            ret += f" {edge.kind.value} {edge.weight} {edge.kind.value} {edge.dst}"
        return ret
