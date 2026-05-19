"""textbook Prim MST (lazy min-heap 기반).

``@mst`` 가 ``prim(g, start)`` 호출 시 MST ``WeightedGraph`` 를 직접 반환한다.
시작 정점에서 출발해 MST 를 확장한다. 음수 가중치 허용. 무방향 그래프 전용.
"""

import heapq
from collections.abc import Iterator
from typing import Literal

from scaffold import Vertex, Weight, WeightedGraph, vertices
from scaffold.trace import mst

type PrimEvent[W: Weight] = (
    tuple[Literal["add_edge"], Vertex, Vertex, W] | tuple[Literal["skip_edge"], Vertex, Vertex, W]
)


@mst
def prim[W: Weight](graph: WeightedGraph[W], start: Vertex) -> Iterator[PrimEvent[W]]:
    """Prim MST (lazy) — 이벤트를 yield 한다.

    - ``("add_edge", u, v, w)``  — MST 에 추가된 간선
    - ``("skip_edge", u, v, w)`` — 도착 정점이 이미 MST 안에 있어 제외된 간선
    """
    in_mst: set[str] = {start.label}
    heap: list[tuple[W, Vertex, Vertex]] = []

    for v, w in graph.weighted_neighbors(start):
        heapq.heappush(heap, (w, start, v))

    while heap:
        w, u, v = heapq.heappop(heap)
        if v.label in in_mst:
            yield "skip_edge", u, v, w
            continue
        in_mst.add(v.label)
        yield "add_edge", u, v, w
        for nb, nw in graph.weighted_neighbors(v):
            if nb.label not in in_mst:
                heapq.heappush(heap, (nw, v, nb))


if __name__ == "__main__":
    a, b, c, d, e = vertices("a", "b", "c", "d", "e")
    g: WeightedGraph[int] = WeightedGraph()
    for u, v, w in [(a, b, 1), (a, c, 4), (b, c, 2), (b, d, 5), (c, e, 1), (d, e, 3)]:
        g.add_edge(u, v, w)

    print("MST:", prim(g, a))
    for event in prim.events(g, a):
        match event:
            case ("add_edge", u, v, w):
                print(f"  add   {u}-{w}-{v}")
            case ("skip_edge", u, v, w):
                print(f"  skip  {u}-{w}-{v}")
