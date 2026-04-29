from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any, Literal, overload

from core.graph.primitives.edge_kind import EdgeKind

if TYPE_CHECKING:
    from core.graph.graph.flow import FlowGraph
    from core.graph.graph.unweighted import UnweightedGraph
    from core.graph.graph.weighted import WeightedGraph
    from core.graph.primitives.edge import Edge, WeightedEdge
    from core.graph.primitives.vertex import Vertex
    from core.graph.primitives.weight import Weight
    from core.graph.walk import Walk, WeightedWalk


class _AbstractGraph[E](ABC):
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
    def get_vertex(self, label: str) -> Vertex:
        """레이블로 정점 객체를 반환한다. 없으면 ``KeyError``."""
        ...

    @abstractmethod
    def get_edge(self, u: Vertex, v: Vertex) -> E:
        """``u``, ``v`` 를 잇는 간선 객체를 반환한다. 없으면 ``KeyError``."""
        ...

    @abstractmethod
    def has_edge(self, u: Vertex, v: Vertex) -> bool:
        """``u``, ``v`` 를 잇는 간선이 그래프에 존재하면 ``True`` 를 반환한다."""
        ...

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
    def _to_graphviz(self) -> Any:
        """Graphviz 렌더링 객체를 반환한다."""
        ...

    def show(self) -> None:
        """그래프를 PDF로 렌더링해 시스템 뷰어로 연다."""
        self._to_graphviz().view(cleanup=True)

    def _repr_svg_(self) -> str:
        """Jupyter Notebook에서 SVG로 인라인 렌더링할 때 호출된다."""
        return self._to_graphviz().pipe("svg").decode()

    def degree(self, v: Vertex) -> int:
        """정점 ``v`` 의 차수(degree)를 반환한다.

        무방향 그래프에서는 연결된 간선 수, 단방향 그래프에서는 진출 차수(out-degree)다.
        """
        return sum(1 for _ in self.neighbors(v))

    def contains_edge(self, edge: Edge | WeightedEdge) -> bool:
        """간선의 kind와 (있다면) weight까지 엄격하게 비교해 포함 여부를 반환한다."""
        from core.graph.primitives.edge import WeightedEdge

        if not (edge.kind == self.kind and self.has_edge(edge.src, edge.dst)):
            return False
        if isinstance(edge, WeightedEdge):
            found = self.get_edge(edge.src, edge.dst)
            return isinstance(found, WeightedEdge) and found.weight == edge.weight
        return True

    def contains_walk(self, walk: Walk | WeightedWalk) -> bool:
        """워크를 구성하는 모든 간선이 그래프에 존재하면 ``True`` 를 반환한다.

        간선의 kind가 그래프와 다르거나, ``WeightedWalk`` 의 가중치가 맞지 않으면 ``False``.
        ``walk in graph`` 연산자로도 동일하게 확인할 수 있다.
        """
        from core.graph.primitives.edge import WeightedEdge
        from core.graph.walk import WeightedWalk

        if walk.kind != self.kind:
            return False
        if isinstance(walk, WeightedWalk):
            for e in walk.edges:
                if not self.has_edge(e.src, e.dst):
                    return False
                found = self.get_edge(e.src, e.dst)
                if not (isinstance(found, WeightedEdge) and found.weight == e.weight):
                    return False
            return True
        return all(self.has_edge(e.src, e.dst) for e in walk.edges)

    def __contains__(self, item: Vertex | Edge | WeightedEdge | Walk | WeightedWalk) -> bool:
        """``in`` 연산자로 정점, 간선, 워크의 포함 여부를 확인한다.

        - ``vertex in graph`` → :meth:`has_vertex` 호출
        - ``edge in graph`` → :meth:`has_edge` 호출
        - ``walk in graph`` → :meth:`contains_walk` 호출
        """
        from core.graph.primitives.edge import Edge, WeightedEdge
        from core.graph.primitives.vertex import Vertex
        from core.graph.walk import Walk, WeightedWalk

        match item:
            case Walk() | WeightedWalk():
                return self.contains_walk(item)
            case WeightedEdge() | Edge():
                return self.contains_edge(item)
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
        from core.graph.walk import WeightedWalk

        if flow:
            return FlowGraph(walk)
        match walk:
            case WeightedWalk():
                return WeightedGraph(walk, kind=kind)
            case _:
                return UnweightedGraph(walk, kind=kind)
