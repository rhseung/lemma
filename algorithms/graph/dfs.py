"""textbook recursive DFS.

``@trace`` 가 ``dfs.visits`` · ``dfs.walks`` helper 를 자동 부여한다.
"""

from collections.abc import Iterator

from algorithms.graph.trace import DFSEvent, trace
from core import UnweightedGraph, Vertex, vertices


@trace
def dfs(graph: UnweightedGraph, start: Vertex) -> Iterator[DFSEvent]:
    """recursive DFS — ``("visit", u, parent)`` 이벤트를 yield 한다."""
    visited: set[Vertex] = set()

    def go(u: Vertex, parent: Vertex | None = None) -> Iterator[DFSEvent]:
        visited.add(u)
        yield "visit", u, parent
        for v in graph.neighbors(u):
            if v not in visited:
                yield from go(v, u)

    yield from go(start)


if __name__ == "__main__":
    a, b, c, d, e, f = vertices("a", "b", "c", "d", "e", "f")
    g = UnweightedGraph()
    for u, v in [(a, b), (a, c), (b, d), (b, e), (c, f)]:
        g.add_edge(u, v)

    for u in dfs.visits(g, a):
        print(u)
    print("walks:", dfs.walks(g, a))
