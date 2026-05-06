from collections.abc import Callable

from core import UnweightedGraph, Vertex, vertices


def dfs(
    graph: UnweightedGraph,
    u: Vertex,
    visited: set[Vertex],
    visit: Callable[[Vertex], None],
) -> None:
    """recursive textbook DFS — 각 정점에 처음 도달할 때 ``visit(u)`` 를 호출한다.

    ``visited`` 는 호출자가 빈 set 을 만들어 넘긴다 (재귀 사이에서 공유).
    """
    visited.add(u)
    visit(u)
    for v in graph.neighbors(u):
        if v not in visited:
            dfs(graph, v, visited, visit)


if __name__ == "__main__":
    a, b, c, d, e, f = vertices("a", "b", "c", "d", "e", "f")
    g = UnweightedGraph()
    for u, v in [(a, b), (a, c), (b, d), (b, e), (c, f)]:
        g.add_edge(u, v)

    dfs(g, a, set(), print)
