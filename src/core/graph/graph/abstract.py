from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Literal

from core.graph.primitives.edge_kind import EdgeKind
from core.graph.primitives.endpoints import HasEndpoints

if TYPE_CHECKING:
    from core.graph.primitives.edge import Edge, WeightedEdge
    from core.graph.primitives.vertex import Vertex
    from core.graph.walk import Walk, WeightedWalk


class _AbstractGraph[E: HasEndpoints](ABC):
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
    def out_edges(self, v: Vertex) -> list[E]:
        """정점 ``v`` 에서 나가는 간선들을 반환한다."""
        ...

    @abstractmethod
    def in_edges(self, v: Vertex) -> list[E]:
        """정점 ``v`` 로 들어오는 간선들을 반환한다."""
        ...

    @abstractmethod
    def vertices(self) -> list[Vertex]:
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

    @classmethod
    @abstractmethod
    def from_edge_list(cls, edges: list, *, kind: EdgeKind = EdgeKind.UNDIRECTED) -> _AbstractGraph:
        """간선 목록으로 그래프를 생성한다."""
        ...

    @abstractmethod
    def to_edge_list(self) -> list[tuple]:
        """간선을 튜플 목록으로 반환한다."""
        ...

    @classmethod
    @abstractmethod
    def from_dot(cls, s: str) -> _AbstractGraph:
        """DOT 문자열에서 그래프를 복원한다."""
        ...

    @abstractmethod
    def to_dot(self) -> str:
        """그래프를 DOT 언어 문자열로 직렬화한다."""
        ...

    @classmethod
    @abstractmethod
    def from_json(cls, s: str) -> _AbstractGraph:
        """JSON 문자열에서 그래프를 복원한다."""
        ...

    @abstractmethod
    def to_json(self) -> str:
        """그래프를 JSON 문자열로 직렬화한다."""
        ...

    @classmethod
    @abstractmethod
    def from_adjacency_matrix(
        cls, m: list[list], labels: list[str] | None = None, *, kind: EdgeKind = EdgeKind.UNDIRECTED
    ) -> _AbstractGraph:
        """인접 행렬에서 그래프를 생성한다."""
        ...

    @abstractmethod
    def to_adjacency_matrix(self) -> list[list]:
        """인접 행렬을 반환한다."""
        ...

    @abstractmethod
    def _validate(self) -> None:
        """내부 자료구조의 일관성을 검증한다. 주로 테스트에서 사용한다."""
        ...

    @abstractmethod
    def _to_graphviz(self) -> Any:
        """Graphviz 렌더링 객체를 반환한다."""
        ...

    @property
    def A(self) -> list[list]:
        """인접 행렬. ``to_adjacency_matrix()`` 와 동일."""
        return self.to_adjacency_matrix()

    def show(self, *, format: Literal["pdf", "svg", "png"] = "png") -> None:
        """그래프를 렌더링해 시스템 뷰어로 연다."""
        dot = self._to_graphviz()
        dot.format = format
        dot.view(cleanup=True)

    def _repr_svg_(self) -> str:
        """Jupyter Notebook에서 SVG로 인라인 렌더링할 때 호출된다."""
        svg = self._to_graphviz().pipe("svg").decode()
        return svg.replace("<svg ", '<svg style="background:transparent;" ', 1)

    def neighbors(self, v: Vertex) -> list[Vertex]:
        """정점 ``v`` 에서 이동 가능한 인접 정점들을 반환한다."""
        return [e.dst for e in self.out_edges(v)]

    def out_degree(self, v: Vertex) -> int:
        """정점 ``v`` 의 진출 차수(out-degree)를 반환한다."""
        return len(self.out_edges(v))

    def in_degree(self, v: Vertex) -> int:
        """정점 ``v`` 의 진입 차수(in-degree)를 반환한다."""
        return len(self.in_edges(v))

    def degree(self, v: Vertex) -> int:
        """정점 ``v`` 의 차수를 반환한다.

        무방향 그래프에서는 연결된 간선 수, 단방향 그래프에서는 진출 차수(out-degree)다.
        """
        return self.out_degree(v)

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
