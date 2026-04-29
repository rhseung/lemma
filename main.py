import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import core.graph as g

if __name__ == "__main__":
    a, b, c, d, e, f, s, t = g.vertices("a", "b", "c", "d", "e", "f", "s", "t")

    wg = g.WeightedGraph(
        a - 4 - b - 2 - c - 7 - d - 1 - e - 5 - f,
        kind=g.EdgeKind.UNDIRECTED,
    )
    wg.add_edge(a, c, 3)
    wg.add_edge(b, d, 6)
    wg.add_edge(c, e, 8)
    wg.add_edge(d, f, 4)
    wg.add_edge(a, f, 9)
    wg.add_edge(b, e, 2)

    wg.show()
