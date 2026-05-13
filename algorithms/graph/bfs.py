"""textbook iterative BFS.

``@trace`` 가 ``bfs.visits`` · ``bfs.levels`` helper 를 자동 부여한다.
``visited.add`` 는 push 시점 — textbook BFS 표준 (큐 중복 방지).
"""

from collections import deque
from collections.abc import Iterator

from algorithms.graph.trace import BFSEvent, trace
from core import UnweightedGraph, Vertex, vertices


@trace
def bfs(graph: UnweightedGraph, start: Vertex) -> Iterator[BFSEvent]:
    """iterative BFS — ``("visit", u, level: int)`` 이벤트를 yield 한다."""
    visited: set[Vertex] = {start}
    queue: deque[tuple[Vertex, int]] = deque([(start, 0)])
    while queue:
        u, level = queue.popleft()
        yield "visit", u, level
        for v in graph.neighbors(u):
            if v not in visited:
                visited.add(v)
                queue.append((v, level + 1))


if __name__ == "__main__":
    a, b, c, d, e, f = vertices("a", "b", "c", "d", "e", "f")
    g = UnweightedGraph()
    for u, v in [(a, b), (a, c), (b, d), (b, e), (c, f)]:
        g.add_edge(u, v)

    for u in bfs.visits(g, a):
        print(u)
    print("levels:", bfs.levels(g, a))
