"""textbook Dijkstra (min-heap 기반).

``@trace`` 가 ``dijkstra.visits`` · ``dijkstra.path`` helper 를 자동 부여한다.
음수 가중치가 없는 그래프에서 최단 경로를 구한다.
"""

import heapq
from collections.abc import Iterator
from math import inf

from algorithms.graph.trace import TraversalEvent, trace
from core import Vertex, WeightedGraph, vertices


@trace
def dijkstra(graph: WeightedGraph, start: Vertex) -> Iterator[TraversalEvent]:
    """Dijkstra 최단 경로 — 이벤트를 yield 한다.

    - ``("visit", u, dist)``      — u 를 priority queue 에서 추출 (거리 확정)
    - ``("relax", u, v, new_dist)`` — 간선 (u, v) 완화 성공
    """
    dist: dict[Vertex, float] = dict.fromkeys(graph.vertices(), inf)
    dist[start] = 0.0
    counter = 0
    heap: list[tuple[float, int, Vertex]] = [(0.0, counter, start)]

    while heap:
        d, _, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        yield "visit", u, d
        for v, w in graph.weighted_neighbors(u):
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                yield "relax", u, v, new_dist
                counter += 1
                heapq.heappush(heap, (new_dist, counter, v))


if __name__ == "__main__":
    from core import EdgeKind

    a, b, c, d, e = vertices("a", "b", "c", "d", "e")
    g: WeightedGraph[int] = WeightedGraph(kind=EdgeKind.DIRECTED)
    for u, v, w in [(a, b, 1), (a, c, 4), (b, c, 2), (b, d, 5), (c, e, 1), (d, e, 3)]:
        g.add_edge(u, v, w)

    print("visits:", dijkstra.visits(g, a))
    print("path a→e:", dijkstra.path(g, a, e))
