"""textbook Kruskal MST (Union-Find 기반).

``@mst`` 가 ``kruskal(g)`` 호출 시 MST ``WeightedGraph`` 를 직접 반환한다.
간선을 가중치 오름차순으로 정렬한 뒤, 사이클이 생기지 않는 간선만 MST 에 추가한다.
음수 가중치 허용. 무방향 그래프 전용.
"""

from collections.abc import Iterator
from typing import Literal

from scaffold import Vertex, Weight, WeightedGraph, vertices
from scaffold.trace import mst
from sets.union_find import UnionFind

type KruskalEvent[W: Weight] = (
    tuple[Literal["add_edge"], Vertex, Vertex, W] | tuple[Literal["skip_edge"], Vertex, Vertex, W]
)


@mst
def kruskal[W: Weight](graph: WeightedGraph[W]) -> Iterator[KruskalEvent[W]]:
    """Kruskal MST — 이벤트를 yield 한다.

    - ``("add_edge", u, v, w)``  — MST 에 추가된 간선
    - ``("skip_edge", u, v, w)`` — 사이클을 만들어 제외된 간선
    """
    uf = UnionFind([v.label for v in graph.vertices()])
    edge_list = sorted(graph.to_edge_list(), key=lambda e: e[2])

    for u, v, w in edge_list:
        if uf.union(u.label, v.label):
            yield "add_edge", u, v, w
        else:
            yield "skip_edge", u, v, w


if __name__ == "__main__":
    a, b, c, d, e = vertices("a", "b", "c", "d", "e")
    g: WeightedGraph[int] = WeightedGraph()
    for u, v, w in [(a, b, 1), (a, c, 4), (b, c, 2), (b, d, 5), (c, e, 1), (d, e, 3)]:
        g.add_edge(u, v, w)

    print("MST:", kruskal(g))
    for event in kruskal.events(g):
        match event:
            case ("add_edge", u, v, w):
                print(f"  add   {u}-{w}-{v}")
            case ("skip_edge", u, v, w):
                print(f"  skip  {u}-{w}-{v}")
