from collections import deque
from collections.abc import Callable

from core import UnweightedGraph, Vertex, vertices


def bfs(
    graph: UnweightedGraph,
    start: Vertex,
    visit: Callable[[Vertex], None],
) -> None:
    """iterative textbook BFS — 각 정점에 처음 도달할 때 ``visit(u)`` 를 호출한다.

    ``visited.add`` 는 push 시점 (textbook BFS 표준 — 큐 중복 방지).
    """
    visited: set[Vertex] = {start}
    queue: deque[Vertex] = deque([start])
    while queue:
        u = queue.popleft()
        visit(u)
        for v in graph.neighbors(u):
            if v not in visited:
                visited.add(v)
                queue.append(v)


if __name__ == "__main__":
    a, b, c, d, e, f = vertices("a", "b", "c", "d", "e", "f")
    g = UnweightedGraph()
    for u, v in [(a, b), (a, c), (b, d), (b, e), (c, f)]:
        g.add_edge(u, v)

    bfs(g, a, print)
