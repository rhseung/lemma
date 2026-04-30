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
    wg += a - 3 - c
    wg += b - 6 - d
    wg += c - 8 - e
    wg += d - 4 - f
    wg += a - 9 - f
    wg += b - 2 - e

    wg.show()

    print(wg[a, c])
