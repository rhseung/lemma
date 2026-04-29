import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import core.graph as g

if __name__ == "__main__":
    # ── 정점 생성 ──────────────────────────────────────────────────────────
    a, b, c, d, s, t = g.vertices("a", "b", "c", "d", "s", "t")

    # ── Walk / WeightedWalk ────────────────────────────────────────────────
    walk = a - b - c - d
    walk_w = a - 3 - b - 5 - c - 2 - d
    print("=== Walk ===")
    print(walk, f"length={walk.length}", f"vertices={walk.vertices}")
    print(
        walk_w, f"length={walk_w.length}", f"weight={walk_w.weight}", f"vertices={walk_w.vertices}"
    )

    # ── Graph 팩토리 (타입 추론) ───────────────────────────────────────────
    print("\n=== Graph factory ===")
    ug = g.Graph(a - b - c)  # UnweightedGraph
    wg = g.Graph(a - 3 - b - 5 - c)  # WeightedGraph[int]
    fg = g.Graph(s >> 10 >> a >> 5 >> t, flow=True)  # FlowGraph
    print(ug)
    print(wg)
    print(fg)

    # ── 정점 / 간선 포함 여부 ─────────────────────────────────────────────
    print("\n=== contains ===")
    print(f"a in ug: {a in ug}")
    print(f"Vertex('z') in ug: {g.Vertex('z') in ug}")
    print(f"(a - b) in ug: {(a - b) in ug}")
    print(f"(a - c) in ug: {(a - c) in ug}")
    print(f"(a >> b) in ug: {(a >> b) in ug}")  # kind 불일치

    print(f"(a - 3 - b) in wg: {(a - 3 - b) in wg}")
    print(f"(a - 9 - b) in wg: {(a - 9 - b) in wg}")  # weight 불일치

    # ── contains_edge (명시적 함수) ────────────────────────────────────────
    print("\n=== contains_edge ===")
    print(f"wg.contains_edge(a - 3 - b): {wg.contains_edge(a - 3 - b)}")
    print(f"wg.contains_edge(a - 9 - b): {wg.contains_edge(a - 9 - b)}")

    # ── contains_walk ─────────────────────────────────────────────────────
    print("\n=== contains_walk ===")
    print(f"wg.contains_walk(a - b - c): {wg.contains_walk(a - b - c)}")  # 가중치 생략 → True
    print(
        f"wg.contains_walk(a - 3 - b - 5 - c): {wg.contains_walk(a - 3 - b - 5 - c)}"
    )  # 정확히 일치
    print(
        f"wg.contains_walk(a - 9 - b - 5 - c): {wg.contains_walk(a - 9 - b - 5 - c)}"
    )  # weight 불일치

    # ── 인접 / 차수 ───────────────────────────────────────────────────────
    print("\n=== neighbors / degree ===")
    ug2 = g.UnweightedGraph(a - b - c - d)
    print(f"neighbors(b): {list(ug2.neighbors(b))}")
    print(f"degree(b): {ug2.degree(b)}")
    print(f"degree(a): {ug2.degree(a)}")

    # ── 방향 그래프 ───────────────────────────────────────────────────────
    print("\n=== directed ===")
    dg = g.UnweightedGraph(a >> b >> c)
    print(f"has_edge(a→b): {dg.has_edge(a, b)}")
    print(f"has_edge(b→a): {dg.has_edge(b, a)}")
    print(f"neighbors(b): {list(dg.neighbors(b))}")
    print(f"neighbors(c): {list(dg.neighbors(c))}")

    # ── FlowGraph ─────────────────────────────────────────────────────────
    print("\n=== FlowGraph ===")
    flow = g.FlowGraph()
    flow.add_edge(s, a, capacity=10)
    flow.add_edge(s, b, capacity=8)
    flow.add_edge(a, t, capacity=6)
    flow.add_edge(b, t, capacity=9)
    print(flow)
    print(f"neighbors(s) before flow: {list(flow.neighbors(s))}")

    fwd = flow.flow_edges(s)[0]
    fwd.flow = 10.0
    print(f"neighbors(s) after saturating s→a: {list(flow.neighbors(s))}")

    rev = fwd.reverse_edge
    assert rev is not None
    print(f"reverse edge: {rev}")
    print(f"rev.reverse_edge is fwd: {rev.reverse_edge is fwd}")
