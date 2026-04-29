from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, overload

from core.graph.primitives.edge_kind import EdgeKind

if TYPE_CHECKING:
    from core.graph.graph.unweighted import UnweightedGraph
    from core.graph.graph.weighted import WeightedGraph
    from core.graph.primitives.edge import Edge, WeightedEdge
    from core.graph.primitives.vertex import Vertex
    from core.graph.primitives.weight import Weight
    from core.graph.walk import Walk, WeightedWalk


class _AbstractGraph(ABC):
    """모든 그래프 구현체의 공통 인터페이스를 정의하는 추상 기반 클래스.

    ``UnweightedGraph`` 와 ``WeightedGraph`` 가 이 클래스를 상속받는다.
    직접 인스턴스화하지 않고, ``Graph`` 팩토리를 통해 생성한다.

    Attributes:
        kind: 그래프를 구성하는 간선들의 방향성 종류.
    """

    kind: EdgeKind

    @abstractmethod
    def add_vertex(self, v: Vertex) -> None:
        """정점을 그래프에 추가한다. 이미 존재하면 아무것도 하지 않는다."""
        ...

    @abstractmethod
    def has_vertex(self, v: Vertex) -> bool:
        """정점이 그래프에 존재하면 ``True`` 를 반환한다."""
        ...

    @abstractmethod
    def _has_edge(self, u: Vertex, v: Vertex) -> bool:
        """``u → v`` 간선 존재 여부의 내부 구현. 서브클래스에서 정점 쌍으로 구현한다."""
        ...

    @overload
    def has_edge(self, u: Vertex, v: Vertex, /) -> bool: ...
    @overload
    def has_edge(self, edge: Edge | WeightedEdge, /) -> bool: ...

    def has_edge(self, u_or_edge: Vertex | Edge | WeightedEdge, v: Vertex | None = None, /) -> bool:
        """``u → v`` 간선이 그래프에 존재하면 ``True`` 를 반환한다.

        두 가지 호출 형태를 지원한다::

            g.has_edge(u, v)  # 정점 두 개
            g.has_edge(edge)  # Edge 또는 WeightedEdge 객체
        """
        from core.graph.primitives.edge import Edge, WeightedEdge

        match u_or_edge:
            case Edge() | WeightedEdge():
                return self._has_edge(u_or_edge.src, u_or_edge.dst)
            case _:
                assert v is not None
                return self._has_edge(u_or_edge, v)

    @abstractmethod
    def neighbors(self, v: Vertex) -> Iterable[Vertex]:
        """정점 ``v`` 에서 이동 가능한 인접 정점들을 반환한다."""
        ...

    @abstractmethod
    def vertices(self) -> Iterable[Vertex]:
        """그래프에 포함된 모든 정점을 반환한다."""
        ...

    @property
    @abstractmethod
    def num_vertices(self) -> int:
        """그래프의 정점 수."""
        ...

    @property
    @abstractmethod
    def num_edges(self) -> int:
        """그래프의 간선 수."""
        ...

    @abstractmethod
    def _validate(self) -> None:
        """내부 자료구조의 일관성을 검증한다. 주로 테스트에서 사용한다."""
        ...

    @abstractmethod
    def _to_graphviz(self) -> object:
        """Graphviz 렌더링 객체를 반환한다."""
        ...

    def show(self) -> None:
        """그래프를 PDF로 렌더링해 시스템 뷰어로 연다."""
        self._to_graphviz().view(cleanup=True)  # type: ignore[missing-attribute]

    def _repr_svg_(self) -> str:
        """Jupyter Notebook에서 SVG로 인라인 렌더링할 때 호출된다."""
        return self._to_graphviz().pipe("svg").decode()  # type: ignore[missing-attribute]

    def degree(self, v: Vertex) -> int:
        """정점 ``v`` 의 차수(degree)를 반환한다.

        무방향 그래프에서는 연결된 간선 수, 단방향 그래프에서는 진출 차수(out-degree)다.
        """
        return sum(1 for _ in self.neighbors(v))

    def contains_path(self, walk: Walk | WeightedWalk) -> bool:
        """워크를 구성하는 모든 간선이 그래프에 존재하면 ``True`` 를 반환한다.

        ``walk in graph`` 연산자로도 동일하게 확인할 수 있다.
        """
        return all(self.has_edge(e.src, e.dst) for e in walk.edges)

    def __contains__(self, item: Vertex | Edge | WeightedEdge | Walk | WeightedWalk) -> bool:
        """``in`` 연산자로 정점, 간선, 워크의 포함 여부를 확인한다.

        - ``vertex in graph`` → :meth:`has_vertex` 호출
        - ``edge in graph`` → :meth:`has_edge` 호출
        - ``walk in graph`` → :meth:`contains_path` 호출
        """
        from core.graph.primitives.edge import Edge, WeightedEdge
        from core.graph.primitives.vertex import Vertex
        from core.graph.walk import Walk, WeightedWalk

        match item:
            case Walk() | WeightedWalk():
                return self.contains_path(item)
            case Edge() | WeightedEdge():
                return self.has_edge(item)
            case Vertex():
                return self.has_vertex(item)
            case _:
                return NotImplemented

    def __len__(self) -> int:
        """``len(graph)`` 로 정점 수를 반환한다."""
        return self.num_vertices

    def __iter__(self) -> Iterator[Vertex]:
        """``for v in graph`` 로 모든 정점을 순회한다."""
        return iter(self.vertices())


class _Graph:
    """워크 타입에 따라 적절한 그래프 구현체를 반환하는 팩토리 클래스.

    ``Graph = _Graph()`` 싱글톤으로 노출된다. 직접 인스턴스화하지 않는다.

    ``WeightedWalk`` 를 받으면 ``WeightedGraph``, 그 외에는 ``UnweightedGraph`` 를 반환한다::

        Graph(a - b - c)  # UnweightedGraph
        Graph(a - 3 - b - 2 - c)  # WeightedGraph[int]
        Graph(kind=EdgeKind.DIRECTED)  # 빈 UnweightedGraph (단방향)
    """

    @overload
    def __call__[W: Weight](self, walk: WeightedWalk[W]) -> WeightedGraph[W]: ...
    @overload
    def __call__(self, walk: Walk | None = None, *, kind: EdgeKind = ...) -> UnweightedGraph: ...

    def __call__(self, walk=None, *, kind=EdgeKind.UNDIRECTED):
        """워크를 받아 그래프를 생성한다.

        Args:
            walk: 그래프 초기화에 사용할 워크. ``None`` 이면 빈 그래프를 생성한다.
            kind: ``walk`` 가 ``None`` 일 때 사용할 간선 방향성. 기본값은 무방향.

        Returns:
            ``WeightedWalk`` 입력 시 ``WeightedGraph``, 그 외에는 ``UnweightedGraph``.
        """
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.graph.weighted import WeightedGraph
        from core.graph.walk import WeightedWalk

        match walk:
            case WeightedWalk():
                return WeightedGraph(walk, kind=kind)
            case _:
                return UnweightedGraph(walk, kind=kind)


Graph = _Graph()
"""워크로부터 그래프를 생성하는 팩토리 싱글톤.

``WeightedWalk`` 를 넘기면 ``WeightedGraph``, 그 외에는 ``UnweightedGraph`` 를 반환한다.

Example::

    a, b, c = Vertex("a"), Vertex("b"), Vertex("c")

    g1 = Graph(a - b - c)            # UnweightedGraph
    g2 = Graph(a - 3 - b - 2 - c)   # WeightedGraph[int]
    g3 = Graph(kind=EdgeKind.DIRECTED)  # 빈 단방향 UnweightedGraph
"""
