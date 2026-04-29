from __future__ import annotations

from core.graph.graph.base import _AbstractGraph
from core.graph.primitives.edge import Edge
from core.graph.primitives.edge_kind import EdgeKind
from core.graph.primitives.vertex import Vertex
from core.graph.walk import Walk


class UnweightedGraph(_AbstractGraph[Edge]):
    """가중치 없는 그래프.

    인접 리스트 방식으로 정점과 간선을 관리한다.
    ``Walk`` 로부터 직접 생성하거나, 빈 그래프를 만든 뒤 ``add_edge`` 로 채울 수 있다::

        a, b, c = Vertex("a"), Vertex("b"), Vertex("c")

        g = UnweightedGraph(a - b - c)  # Walk로부터 생성
        g = UnweightedGraph(kind=EdgeKind.DIRECTED)  # 빈 단방향 그래프
        g.add_edge(a, b)  # 수동으로 간선 추가

    Attributes:
        kind: 그래프의 간선 방향성 종류.
    """

    def __init__(self, walk: Walk | None = None, *, kind: EdgeKind = EdgeKind.UNDIRECTED) -> None:
        """그래프를 초기화한다.

        Args:
            walk: 그래프를 초기화할 워크. ``None`` 이면 빈 그래프를 생성한다.
            kind: ``walk`` 가 ``None`` 일 때 사용할 간선 방향성.
        """
        self.kind = walk.kind if walk is not None else kind
        self._vertices: dict[str, Vertex] = {}
        self._adj: dict[str, list[str]] = {}

        if walk is not None:
            for edge in walk.edges:
                self.add_edge(edge.src, edge.dst)

    @property
    def num_vertices(self) -> int:
        """그래프의 정점 수."""
        return len(self._vertices)

    @property
    def num_edges(self) -> int:
        """그래프의 간선 수.

        단방향 그래프에서는 방향 있는 간선 수를 그대로 반환하고,
        무방향·양방향 그래프에서는 양방향으로 저장된 값을 2로 나눠 반환한다.
        """
        total = sum(len(nbrs) for nbrs in self._adj.values())
        return total if self.kind == EdgeKind.DIRECTED else total // 2

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

    def add_edge(self, u: Vertex, v: Vertex) -> None:
        """간선을 그래프에 추가한다.

        두 정점이 없으면 자동으로 추가된다. 무방향·양방향 그래프에서는
        반대 방향 간선도 함께 추가된다.

        Args:
            u: 출발 정점.
            v: 도착 정점.
        """
        self.add_vertex(u)
        self.add_vertex(v)
        if v.label not in self._adj[u.label]:
            self._adj[u.label].append(v.label)
        if self.kind != EdgeKind.DIRECTED and u.label not in self._adj[v.label]:
            self._adj[v.label].append(u.label)

    def has_edge(self, u: Vertex, v: Vertex) -> bool:
        """``u``, ``v`` 를 잇는 간선이 그래프에 존재하면 ``True`` 를 반환한다."""
        if not (self.has_vertex(u) and self.has_vertex(v)):
            return False
        return v.label in self._adj[u.label]

    def get_edge(self, u: Vertex, v: Vertex) -> Edge:
        """``u``, ``v`` 를 잇는 간선 객체를 반환한다. 없으면 ``KeyError``."""
        if not self.has_edge(u, v):
            raise KeyError(f"Edge ({u}, {v}) not found")
        return Edge(u, v, self.kind)

    def out_edges(self, v: Vertex) -> list[Edge]:
        """정점 ``v`` 에서 나가는 간선들을 반환한다."""
        return [Edge(v, self._vertices[label], self.kind) for label in self._adj[v.label]]

    def in_edges(self, v: Vertex) -> list[Edge]:
        """정점 ``v`` 로 들어오는 간선들을 반환한다."""
        if self.kind != EdgeKind.DIRECTED:
            return [Edge(self._vertices[label], v, self.kind) for label in self._adj[v.label]]
        return [
            Edge(self._vertices[u_label], v, self.kind)
            for u_label, nbrs in self._adj.items()
            if v.label in nbrs
        ]

    def vertices(self) -> list[Vertex]:
        """그래프에 포함된 모든 정점을 반환한다."""
        return list(self._vertices.values())

    def _validate(self) -> None:
        """내부 인접 리스트의 일관성을 검증한다.

        - 모든 레이블이 정점 사전에 존재하는지 확인한다.
        - 무방향·양방향 그래프에서는 대칭성(u→v이면 v→u)을 확인한다.
        """
        for label, nbrs in self._adj.items():
            assert label in self._vertices
            for nlabel in nbrs:
                assert nlabel in self._vertices
        if self.kind != EdgeKind.DIRECTED:
            for label, nbrs in self._adj.items():
                for nlabel in nbrs:
                    assert label in self._adj[nlabel]

    def _to_graphviz(self) -> object:
        """Graphviz 렌더링 객체를 생성한다."""
        import graphviz

        dot = graphviz.Graph() if self.kind == EdgeKind.UNDIRECTED else graphviz.Digraph()
        for v in self._vertices.values():
            dot.node(v.label)
        seen: set[frozenset] = set()
        for label, nbrs in self._adj.items():
            for nlabel in nbrs:
                if self.kind != EdgeKind.DIRECTED:
                    key: frozenset = frozenset([label, nlabel])
                    if key in seen:
                        continue
                    seen.add(key)
                attrs = {"dir": "both"} if self.kind == EdgeKind.BIDIRECTED else {}
                dot.edge(label, nlabel, **attrs)
        return dot

    def __repr__(self) -> str:
        return (
            f"UnweightedGraph({self.kind.name.lower()}, V={self.num_vertices}, E={self.num_edges})"
        )
