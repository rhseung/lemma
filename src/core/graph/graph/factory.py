from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, overload

from core.graph.primitives.edge_kind import EdgeKind

if TYPE_CHECKING:
    from core.graph.graph.flow import FlowGraph
    from core.graph.graph.unweighted import UnweightedGraph
    from core.graph.graph.weighted import WeightedGraph
    from core.graph.primitives.vertex import Vertex
    from core.graph.primitives.weight import Weight
    from core.graph.walk import Walk, WeightedWalk


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
        from core.graph.primitives.edge import Edge, WeightedEdge
        from core.graph.walk import Walk, WeightedWalk

        if flow:
            if isinstance(walk, WeightedEdge):
                walk = WeightedWalk([walk])
            return FlowGraph(walk)

        match walk:
            case WeightedEdge():
                walk = WeightedWalk([walk])
            case Edge():
                walk = Walk([walk])

        match walk:
            case WeightedWalk():
                return WeightedGraph(walk, kind=kind)
            case _:
                return UnweightedGraph(walk, kind=kind)

    # --- I/O ---

    @classmethod
    def from_edge_list(cls, edges: list, *, kind: EdgeKind = EdgeKind.UNDIRECTED) -> Any:
        """간선 목록으로 그래프를 생성한다. 튜플 길이가 3이면 ``WeightedGraph``, 2이면 ``UnweightedGraph``."""
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.graph.weighted import WeightedGraph

        if edges and len(edges[0]) == 3:
            return WeightedGraph.from_edge_list(edges, kind=kind)
        return UnweightedGraph.from_edge_list(edges, kind=kind)

    @classmethod
    def from_dot(cls, s: str) -> Any:
        """DOT 문자열에서 그래프를 복원한다. 간선에 ``label``이 있으면 ``WeightedGraph``."""
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.graph.weighted import WeightedGraph
        from core.graph.io import _parse_dot

        _, _, edges = _parse_dot(s)
        if any(w is not None for _, _, w in edges):
            return WeightedGraph.from_dot(s)
        return UnweightedGraph.from_dot(s)

    @classmethod
    def from_json(cls, s: str) -> Any:
        """JSON 문자열에서 그래프를 복원한다. ``type`` 필드로 구현체를 결정한다."""
        import json

        from core.graph.graph.flow import FlowGraph
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.graph.weighted import WeightedGraph

        match json.loads(s).get("type"):
            case "WeightedGraph":
                return WeightedGraph.from_json(s)
            case "FlowGraph":
                return FlowGraph.from_json(s)
            case _:
                return UnweightedGraph.from_json(s)

    @classmethod
    def from_adjacency_matrix(
        cls, m: list[list], labels: list[str] | None = None, *, kind: EdgeKind = EdgeKind.UNDIRECTED
    ) -> Any:
        """인접 행렬에서 그래프를 생성한다. ``None`` 값이 있으면 ``WeightedGraph``."""
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.graph.weighted import WeightedGraph

        if any(val is None for row in m for val in row):
            return WeightedGraph.from_adjacency_matrix(m, labels, kind=kind)
        return UnweightedGraph.from_adjacency_matrix(m, labels, kind=kind)

    # --- 패턴 생성자 ---

    @staticmethod
    def path(*vertices: Vertex, kind: EdgeKind = EdgeKind.UNDIRECTED) -> UnweightedGraph:
        """정점들을 일렬로 이은 경로 그래프를 생성한다.

        n개 정점 → n-1개 간선. 양 끝 정점의 차수는 1, 중간 정점의 차수는 2::

            A - B - C - D
        """
        from itertools import pairwise

        from core.graph.graph.unweighted import UnweightedGraph

        g = UnweightedGraph(kind=kind)
        for v in vertices:
            g.add_vertex(v)
        for u, v in pairwise(vertices):
            g.add_edge(u, v)
        return g

    @staticmethod
    def cycle(*vertices: Vertex, kind: EdgeKind = EdgeKind.UNDIRECTED) -> UnweightedGraph:
        """정점들을 순환으로 이은 순환 그래프를 생성한다.

        n개 정점 → n개 간선. 모든 정점의 차수는 2. 마지막 정점과 첫 정점이 연결된다::

            A - B
            |   |
            D - C
        """
        from itertools import pairwise

        from core.graph.graph.unweighted import UnweightedGraph

        g = UnweightedGraph(kind=kind)
        for v in vertices:
            g.add_vertex(v)
        for u, v in pairwise(vertices):
            g.add_edge(u, v)
        g.add_edge(vertices[-1], vertices[0])
        return g

    @staticmethod
    def complete(*vertices: Vertex, kind: EdgeKind = EdgeKind.UNDIRECTED) -> UnweightedGraph:
        """모든 정점 쌍을 잇는 완전 그래프(K_n)를 생성한다.

        n개 정점 → n(n-1)/2개 간선. ``DIRECTED``이면 토너먼트 그래프(n(n-1)개 간선)::

            A-B, A-C, A-D
                 B-C, B-D
                      C-D
        """
        from core.graph.graph.unweighted import UnweightedGraph

        g = UnweightedGraph(kind=kind)
        for v in vertices:
            g.add_vertex(v)
        for i, u in enumerate(vertices):
            for v in vertices[i + 1 :]:
                g.add_edge(u, v)
                if kind == EdgeKind.DIRECTED:
                    g.add_edge(v, u)
        return g

    @staticmethod
    def bipartite(
        left: list[Vertex],
        right: list[Vertex],
        *,
        kind: EdgeKind = EdgeKind.UNDIRECTED,
    ) -> UnweightedGraph:
        """두 집합 사이를 모두 이은 완전 이분 그래프(K_{m,n})를 생성한다.

        같은 집합 내부에는 간선이 없다. m x n개 간선::

            L1 - R1, L1 - R2
            L2 - R1, L2 - R2
        """
        from core.graph.graph.unweighted import UnweightedGraph

        g = UnweightedGraph(kind=kind)
        for v in left + right:
            g.add_vertex(v)
        for u in left:
            for v in right:
                g.add_edge(u, v)
        return g

    @staticmethod
    def star(
        center: Vertex, /, *leaves: Vertex, kind: EdgeKind = EdgeKind.UNDIRECTED
    ) -> UnweightedGraph:
        """중심 정점과 모든 잎 정점을 잇는 별 그래프(K_{1,n})를 생성한다.

        첫 번째 인자가 center. 잎끼리는 간선이 없다. n개 잎 → n개 간선::

              B
              |
            C-A-D
              |
              E
        """
        from core.graph.graph.unweighted import UnweightedGraph

        g = UnweightedGraph(kind=kind)
        g.add_vertex(center)
        for leaf in leaves:
            g.add_edge(center, leaf)
        return g

    @staticmethod
    def wheel(
        center: Vertex, /, *rim: Vertex, kind: EdgeKind = EdgeKind.UNDIRECTED
    ) -> UnweightedGraph:
        """rim의 순환 위에 center를 허브로 연결한 바퀴 그래프를 생성한다.

        첫 번째 인자가 center. n개 rim → rim cycle n개 + spoke n개 = 2n개 간선::

            rim cycle: A-B-C-D-A
            spokes   : H-A, H-B, H-C, H-D
        """
        from itertools import pairwise

        from core.graph.graph.unweighted import UnweightedGraph

        g = UnweightedGraph(kind=kind)
        g.add_vertex(center)
        for v in rim:
            g.add_vertex(v)
        for u, v in pairwise(rim):
            g.add_edge(u, v)
        g.add_edge(rim[-1], rim[0])
        for v in rim:
            g.add_edge(center, v)
        return g

    @staticmethod
    def grid(rows: int, cols: int, *, kind: EdgeKind = EdgeKind.UNDIRECTED) -> UnweightedGraph:
        """rows x cols 격자 그래프를 생성한다.

        정점은 자동 생성되며 레이블은 ``v{r}{c}`` 형식. 각 정점은 상하좌우 이웃과 연결된다::

            v00-v01-v02
             |   |   |
            v10-v11-v12
             |   |   |
            v20-v21-v22
        """
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.primitives.vertex import Vertex

        verts = [[Vertex(f"v{r}{c}") for c in range(cols)] for r in range(rows)]
        g = UnweightedGraph(kind=kind)
        for row in verts:
            for v in row:
                g.add_vertex(v)
        for r in range(rows):
            for c in range(cols):
                if c + 1 < cols:
                    g.add_edge(verts[r][c], verts[r][c + 1])
                if r + 1 < rows:
                    g.add_edge(verts[r][c], verts[r + 1][c])
        return g

    @staticmethod
    def petersen() -> UnweightedGraph:
        """페테르센 그래프를 생성한다.

        정점 10개(o0-o4, i0-i4), 간선 15개, 3-정규 무방향 그래프.
        외부 5-cycle + 내부 pentagram + spoke 5개로 구성된다::

            outer cycle : o0-o1-o2-o3-o4-o0
            inner pentagram: i0-i2-i4-i1-i3-i0
            spokes      : o0-i0, o1-i1, o2-i2, o3-i3, o4-i4

        See Also:
            https://en.wikipedia.org/wiki/Petersen_graph
        """
        from core.graph.graph.unweighted import UnweightedGraph
        from core.graph.primitives.vertex import Vertex

        outer = [Vertex(f"o{i}") for i in range(5)]
        inner = [Vertex(f"i{i}") for i in range(5)]
        g = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        for v in outer + inner:
            g.add_vertex(v)
        for i in range(5):
            g.add_edge(outer[i], outer[(i + 1) % 5])  # 외부 5-cycle
            g.add_edge(inner[i], inner[(i + 2) % 5])  # 내부 pentagram
            g.add_edge(outer[i], inner[i])  # spokes
        return g
