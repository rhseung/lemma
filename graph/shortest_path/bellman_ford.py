"""textbook Bellman-Ford.

``@trace`` 가 ``bellman_ford.visits`` · ``bellman_ford.path`` helper 를 자동 부여한다.
음수 가중치를 허용하며, 음수 사이클 감지가 가능하다.
"""

from collections.abc import Iterator
from typing import Literal

from scaffold import Vertex, WeightedGraph, vertices
from scaffold.trace import trace

type BellmanFordEvent = (
    tuple[Literal["visit"], Vertex, float]
    | tuple[Literal["relax"], Vertex, Vertex, float]
    | tuple[Literal["negative_cycle"], Vertex, Vertex]
)


@trace
def bellman_ford(graph: WeightedGraph, start: Vertex) -> Iterator[BellmanFordEvent]:
    """Bellman-Ford 최단 경로 — 이벤트를 yield 한다.

    - ``("visit", u, dist)``        — 정점 u 의 거리가 확정됨 (V-1 라운드 완료 후)
    - ``("relax", u, v, new_dist)`` — 간선 (u, v) 완화 성공
    - ``("negative_cycle", u, v)``  — 음수 사이클 감지 (V번째 라운드에서 완화 발생)
    """
    raise NotImplementedError


if __name__ == "__main__":
    from scaffold import EdgeKind

    a, b, c, d, e = vertices("a", "b", "c", "d", "e")
    g: WeightedGraph[int] = WeightedGraph(kind=EdgeKind.DIRECTED)
    for u, v, w in [(a, b, 1), (a, c, 4), (b, c, 2), (b, d, 5), (c, e, 1), (d, e, 3)]:
        g.add_edge(u, v, w)

    print("visits:", bellman_ford.visits(g, a))
    print("path a→e:", bellman_ford.path(g, a, e))
