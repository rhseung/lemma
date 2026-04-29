from __future__ import annotations

from typing import TYPE_CHECKING

from core.graph.graph.base import _AbstractGraph
from core.graph.primitives.edge_kind import EdgeKind
from core.graph.primitives.flow_edge import FlowEdge
from core.graph.primitives.vertex import Vertex
from core.graph.primitives.weight import Weight

if TYPE_CHECKING:
    from core.graph.walk import WeightedWalk


class FlowGraph[W: Weight](_AbstractGraph[FlowEdge[W]]):
    """유량 그래프.

    각 간선은 ``capacity`` (최대 유량)와 ``flow`` (현재 유량)를 가진다.
    ``add_edge`` 로 정방향 간선을 추가하면 역방향(residual) 간선이 자동 생성된다.
    Dinic 같은 최대 유량 알고리즘의 기반 자료구조다.

    항상 단방향(``DIRECTED``) 그래프다.

    DSL과 객체형 방식 모두 지원한다::

        # DSL 방식
        s, a, t = Vertex("s"), Vertex("a"), Vertex("t")
        g = FlowGraph(s >> 10 >> a >> 5 >> t)

        # 객체형 방식
        g = FlowGraph()
        g.add_edge(s, a, capacity=10)
        g.add_edge(a, t, capacity=5)
    """

    def __init__(self, walk: WeightedWalk[W] | None = None) -> None:
        """그래프를 초기화한다.

        Args:
            walk: 그래프를 초기화할 가중 워크. 간선의 가중치가 용량이 된다.
                  ``None`` 이면 빈 그래프를 생성한다.
        """
        self.kind = EdgeKind.DIRECTED
        self._vertices: dict[str, Vertex] = {}
        self._adj: dict[str, list[FlowEdge[W]]] = {}
        self._num_edges: int = 0

        if walk is not None:
            if walk.kind != EdgeKind.DIRECTED:
                raise ValueError(f"FlowGraph requires directed edges (>>), got {walk.kind.value!r}")
            for edge in walk.edges:
                self.add_edge(edge.src, edge.dst, edge.weight)

    @property
    def num_vertices(self) -> int:
        """그래프의 정점 수."""
        return len(self._vertices)

    @property
    def num_edges(self) -> int:
        """사용자가 추가한 정방향 간선 수."""
        return self._num_edges

    def add_vertex(self, v: Vertex) -> None:
        """정점을 그래프에 추가한다. 이미 존재하면 아무것도 하지 않는다."""
        if v.label not in self._vertices:
            self._vertices[v.label] = v
            self._adj[v.label] = []

    def has_vertex(self, v: Vertex) -> bool:
        """정점이 그래프에 존재하면 ``True`` 를 반환한다."""
        return v.label in self._vertices

    def get_vertex(self, label: str) -> Vertex:
        """레이블로 정점 객체를 반환한다. 없으면 ``KeyError``."""
        return self._vertices[label]

    def add_edge(self, u: Vertex, v: Vertex, capacity: W) -> None:
        """정방향 간선과 역방향 간선 쌍을 추가한다.

        Args:
            u: 출발 정점.
            v: 도착 정점.
            capacity: 정방향 간선의 최대 유량. 역방향은 초기 용량 0.
        """
        self.add_vertex(u)
        self.add_vertex(v)
        fwd = FlowEdge(u, v, capacity)
        assert fwd.reverse_edge is not None
        self._adj[u.label].append(fwd)
        self._adj[v.label].append(fwd.reverse_edge)
        self._num_edges += 1

    def has_edge(self, u: Vertex, v: Vertex) -> bool:
        if not (self.has_vertex(u) and self.has_vertex(v)):
            return False
        return any(e.dst == v and e.forward for e in self._adj[u.label])

    def get_edge(self, u: Vertex, v: Vertex) -> FlowEdge:
        """``u`` 에서 ``v`` 로의 정방향 간선 객체를 반환한다. 역방향(residual) 간선은 제외. 없으면 ``KeyError``."""
        if self.has_vertex(u):
            for e in self._adj[u.label]:
                if e.dst == v and e.forward:
                    return e
        raise KeyError(f"Edge {u} → {v} not found")

    def out_edges(self, v: Vertex) -> list[FlowEdge[W]]:
        """정점 ``v`` 에서 나가는 정방향 간선들을 반환한다."""
        return [e for e in self._adj[v.label] if e.forward]

    def in_edges(self, v: Vertex) -> list[FlowEdge[W]]:
        """정점 ``v`` 로 들어오는 정방향 간선들을 반환한다."""
        result = []
        for e in self._adj[v.label]:
            if not e.forward:
                assert e.reverse_edge is not None
                result.append(e.reverse_edge)
        return result

    def neighbors_residual(self, v: Vertex) -> list[Vertex]:
        """잔여 용량이 있는 인접 정점을 반환한다. 최대 유량 알고리즘에서 사용한다."""
        return [e.dst for e in self._adj[v.label] if e.flow < e.capacity]

    def edges(self, v: Vertex) -> list[FlowEdge[W]]:
        """정점 ``v`` 의 모든 간선을 반환한다 (역방향 포함). Dinic 등 알고리즘에서 사용한다."""
        return self._adj[v.label]

    def vertices(self) -> list[Vertex]:
        """그래프에 포함된 모든 정점을 반환한다."""
        return list(self._vertices.values())

    def _validate(self) -> None:
        """내부 구조의 일관성을 검증한다.

        - 모든 간선 엔드포인트가 정점 사전에 존재하는지 확인.
        - ``0 ≤ flow ≤ capacity`` 제약 확인.
        - 역방향 간선 순환 참조 무결성 확인.
        """
        for label, edges in self._adj.items():
            assert label in self._vertices
            for e in edges:
                assert e.dst.label in self._vertices
                assert e.flow <= e.capacity, f"flow 제약 위반: {e}"
                assert e.reverse_edge is not None
                assert e.reverse_edge.reverse_edge is e

    def _to_graphviz(self) -> object:
        """Graphviz 렌더링 객체를 생성한다. 정방향 간선만 표시한다."""
        import graphviz

        dot = graphviz.Digraph()
        for v in self._vertices.values():
            dot.node(v.label)
        for edges in self._adj.values():
            for e in edges:
                if e.forward:
                    dot.edge(e.src.label, e.dst.label, label=f"{e.flow}/{e.capacity}")
        return dot

    def __repr__(self) -> str:
        return f"FlowGraph(directed, V={self.num_vertices}, E={self.num_edges})"
