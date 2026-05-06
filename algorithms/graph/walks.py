"""DFS / BFS 결과를 시각화용 ``Walk`` / ``UnweightedGraph`` list 로 변환하는 helper.

순수 textbook 알고리즘 (``dfs``, ``bfs``) 은 ``visit(u)`` 콜백만 받기 때문에,
chain 추적·level 그룹핑 같은 부가 로직은 여기서 처리한다. 부모/level 추정은
방문 시점의 in-neighbor 정보로 재구성한다 (알고리즘에 별도 인자 추가 불필요).
"""

from algorithms.graph.bfs import bfs
from algorithms.graph.dfs import dfs
from core import Edge, EdgeKind, UnweightedGraph, Vertex, Walk


def dfs_walks(graph: UnweightedGraph, start: Vertex) -> list[Walk]:
    """DFS 트리를 chain 단위 walk 들로 분할.

    부모 추정: visit 시점에 ``u`` 의 in-neighbor 중 가장 최근에 방문된 정점.
    분기점·방문 점프마다 chain 이 끊기며 새 walk 가 시작된다.
    walk 의 ``kind`` 는 ``DIRECTED`` (parent → child) 로 시각화 시 화살표 표시.
    """
    visited: dict[Vertex, int] = {}
    walks: list[Walk] = []
    current: list[Edge] = []

    def visit(u: Vertex) -> None:
        visited[u] = len(visited)
        if u == start:
            return
        parent = max(
            (e.src for e in graph.in_edges(u) if e.src in visited and e.src != u),
            key=visited.__getitem__,
        )
        if current and current[-1].dst != parent:
            walks.append(Walk(list(current)))
            current.clear()
        current.append(Edge(parent, u, EdgeKind.DIRECTED))

    dfs(graph, start, set(), visit)
    if current:
        walks.append(Walk(current))
    return walks


def bfs_levels(graph: UnweightedGraph, start: Vertex) -> list[Walk | UnweightedGraph]:
    """BFS 결과를 level 별 그룹으로 분할.

    Level 추정: visit 시점에 ``u`` 의 visited in-neighbor 중 최소 level + 1.
    같은 level 의 정점들은 한 ``Walk`` (synthetic chain — 그래프에 없는
    간선이라 ghost edge 로 점선 그려짐). Level 정점 1개 (``start`` 등) 는
    단일 정점 ``UnweightedGraph`` 로 감싼다 (Walk 가 ≥ 1 간선 요구하므로).
    """
    level: dict[Vertex, int] = {start: 0}
    by_level: dict[int, list[Vertex]] = {}

    def visit(u: Vertex) -> None:
        if u != start:
            level[u] = 1 + min(
                level[e.src]
                for e in graph.in_edges(u)
                if e.src in level and e.src != u
            )
        by_level.setdefault(level[u], []).append(u)

    bfs(graph, start, visit)

    groups: list[Walk | UnweightedGraph] = []
    for lv in sorted(by_level):
        verts = by_level[lv]
        if len(verts) == 1:
            g = UnweightedGraph()
            g.add_vertex(verts[0])
            groups.append(g)
        else:
            edges = [
                Edge(verts[i], verts[i + 1], EdgeKind.DIRECTED)
                for i in range(len(verts) - 1)
            ]
            groups.append(Walk(edges))
    return groups
