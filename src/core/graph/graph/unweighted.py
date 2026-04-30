from __future__ import annotations

import json as _json

from core.graph.graph.abstract import _AbstractGraph
from core.graph.io import _parse_dot
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

    def delete_vertex(self, v: Vertex) -> None:
        """정점과 인접 간선을 모두 제거한다. 없으면 ``KeyError``."""
        if not self.has_vertex(v):
            raise KeyError(f"Vertex {v!r} not found")
        label = v.label
        for other_label in self._adj:
            if other_label != label:
                self._adj[other_label] = [l for l in self._adj[other_label] if l != label]
        del self._adj[label]
        del self._vertices[label]

    def delete_edge(self, u: Vertex, v: Vertex) -> None:
        """``u``, ``v`` 를 잇는 간선을 제거한다. 없으면 ``KeyError``."""
        if not self.has_edge(u, v):
            raise KeyError(f"Edge ({u!r}, {v!r}) not found")
        self._adj[u.label].remove(v.label)
        if self.kind != EdgeKind.DIRECTED:
            self._adj[v.label].remove(u.label)

    def reverse(self) -> UnweightedGraph:
        """모든 간선 방향을 반전한 새 그래프를 반환한다. ``DIRECTED`` 전용."""
        if self.kind != EdgeKind.DIRECTED:
            raise ValueError("reverse() requires a directed graph")
        g = UnweightedGraph(kind=EdgeKind.DIRECTED)
        for v in self.vertices():
            g.add_vertex(v)
        for v in self.vertices():
            for e in self.out_edges(v):
                g.add_edge(e.dst, e.src)
        return g

    def complement(self) -> UnweightedGraph:
        """없는 간선을 잇고 있는 간선을 제거한 여그래프를 반환한다."""
        verts = self.vertices()
        g = UnweightedGraph(kind=self.kind)
        for v in verts:
            g.add_vertex(v)
        for i, u in enumerate(verts):
            for j, v in enumerate(verts):
                if u == v:
                    continue
                if self.kind != EdgeKind.DIRECTED and j <= i:
                    continue
                if not self.has_edge(u, v):
                    g.add_edge(u, v)
        return g

    def _add_edge_from(self, edge: Edge) -> None:
        self.add_edge(edge.src, edge.dst)

    def __iadd__(self, other: object) -> UnweightedGraph:
        """``g += v`` / ``g += edge`` / ``g += walk`` / ``g += graph`` — in-place 추가."""
        from core.graph.walk import Walk

        match other:
            case Vertex():
                self.add_vertex(other)
            case Edge():
                self.add_edge(other.src, other.dst)
            case Walk():
                for e in other.edges:
                    self.add_edge(e.src, e.dst)
            case UnweightedGraph():
                for v in other.vertices():
                    self.add_vertex(v)
                for v in other.vertices():
                    for e in other.out_edges(v):
                        if not self.has_edge(e.src, e.dst):
                            self.add_edge(e.src, e.dst)
            case _:
                return NotImplemented  # type: ignore[return-value]
        return self

    def __invert__(self) -> UnweightedGraph:
        """``~g`` — :meth:`complement` 위임."""
        return self.complement()

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
        dot.attr(bgcolor="transparent")
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

    @classmethod
    def from_edge_list(
        cls,
        edges: list[tuple[Vertex | str, Vertex | str]],
        *,
        kind: EdgeKind = EdgeKind.UNDIRECTED,
    ) -> UnweightedGraph:
        """간선 목록으로 그래프를 생성한다.

        Args:
            edges: ``(u, v)`` 튜플의 목록. ``Vertex`` 또는 레이블 문자열 모두 허용.
            kind: 간선의 방향성.
        """
        g = cls(kind=kind)
        for u, v in edges:
            g.add_edge(
                Vertex(u) if isinstance(u, str) else u, Vertex(v) if isinstance(v, str) else v
            )
        return g

    def to_edge_list(self) -> list[tuple[str, str]]:
        """간선을 ``(u_label, v_label)`` 튜플 목록으로 반환한다.

        무방향·양방향 그래프에서는 각 간선을 한 번만 포함한다.
        """
        seen: set[frozenset] = set()
        result: list[tuple[str, str]] = []
        for label, nbrs in self._adj.items():
            for nlabel in nbrs:
                if self.kind != EdgeKind.DIRECTED:
                    key = frozenset((label, nlabel))
                    if key in seen:
                        continue
                    seen.add(key)
                result.append((label, nlabel))
        return result

    def to_dot(self) -> str:
        """그래프를 DOT 언어 문자열로 직렬화한다."""
        return self._to_graphviz().source  # type: ignore[attr-defined]

    @classmethod
    def from_dot(cls, s: str) -> UnweightedGraph:
        """DOT 문자열에서 그래프를 복원한다."""
        kind, vertex_labels, edges = _parse_dot(s)
        g = cls(kind=kind)
        for label in vertex_labels:
            g.add_vertex(Vertex(label))
        for u, v, _ in edges:
            g.add_edge(Vertex(u), Vertex(v))
        return g

    def to_json(self) -> str:
        """그래프를 JSON 문자열로 직렬화한다."""
        return _json.dumps(
            {
                "type": "UnweightedGraph",
                "kind": self.kind.name.lower(),
                "vertices": [v.label for v in self.vertices()],
                "edges": self.to_edge_list(),
            }
        )

    @classmethod
    def from_json(cls, s: str) -> UnweightedGraph:
        """JSON 문자열에서 그래프를 복원한다."""
        data = _json.loads(s)
        kind = EdgeKind[data["kind"].upper()]
        g = cls(kind=kind)
        for label in data["vertices"]:
            g.add_vertex(Vertex(label))
        for u, v in data["edges"]:
            g.add_edge(Vertex(u), Vertex(v))
        return g

    def to_adjacency_matrix(self) -> list[list[int]]:
        """인접 행렬을 반환한다. 행·열 순서는 ``vertices()``와 동일하다.

        간선이 있으면 ``1``, 없으면 ``0``.
        """
        verts = self.vertices()
        idx = {v.label: i for i, v in enumerate(verts)}
        n = len(verts)
        mat = [[0] * n for _ in range(n)]
        for label, nbrs in self._adj.items():
            for nlabel in nbrs:
                mat[idx[label]][idx[nlabel]] = 1
        return mat

    @classmethod
    def from_adjacency_matrix(
        cls,
        m: list[list[int]],
        labels: list[str] | None = None,
        *,
        kind: EdgeKind = EdgeKind.UNDIRECTED,
    ) -> UnweightedGraph:
        """인접 행렬에서 그래프를 생성한다.

        Args:
            m: n x n 정수 행렬. 0이면 간선 없음, 0이 아니면 간선 있음.
            labels: 정점 레이블 목록. ``None``이면 ``"0"``, ``"1"``, ... 을 사용.
            kind: 간선의 방향성.
        """
        n = len(m)
        if labels is None:
            labels = [str(i) for i in range(n)]
        verts = [Vertex(label) for label in labels]
        g = cls(kind=kind)
        for v in verts:
            g.add_vertex(v)
        for i in range(n):
            for j in range(n):
                if m[i][j]:
                    g.add_edge(verts[i], verts[j])
        return g

    def __repr__(self) -> str:
        return (
            f"UnweightedGraph({self.kind.name.lower()}, V={self.num_vertices}, E={self.num_edges})"
        )
