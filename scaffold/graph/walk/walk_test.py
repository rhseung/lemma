import pytest

from scaffold.graph.graph.unweighted import UnweightedGraph
from scaffold.graph.graph.weighted import WeightedGraph
from scaffold.graph.primitives.edge import Edge
from scaffold.graph.primitives.edge_kind import EdgeKind
from scaffold.graph.primitives.vertex import Vertex
from scaffold.graph.walk import Path as GPath
from scaffold.graph.walk import Trail, Walk, WeightedWalk


@pytest.fixture
def verts():
    return Vertex("a"), Vertex("b"), Vertex("c"), Vertex("d")


class TestWalk:
    def test_basic_chain(self, verts):
        a, b, c, _ = verts
        w = a - b - c
        assert isinstance(w, Walk)
        assert w.length == 2

    def test_vertices_property(self, verts):
        a, b, c, _ = verts
        w = a - b - c
        assert w.vertices == [a, b, c]

    def test_kind_undirected(self, verts):
        a, b, c, _ = verts
        w = a - b - c
        assert w.kind == EdgeKind.UNDIRECTED

    def test_kind_directed(self, verts):
        a, b, c, _ = verts
        w = a >> b >> c
        assert w.kind == EdgeKind.DIRECTED

    def test_kind_bidirected(self, verts):
        a, b, c, _ = verts
        w = a & b & c
        assert w.kind == EdgeKind.BIDIRECTED

    def test_is_closed_false(self, verts):
        a, b, c, _ = verts
        w = a - b - c
        assert not w.is_closed

    def test_is_closed_true(self, verts):
        a, b, c, _ = verts
        w = a - b - c - a
        assert w.is_closed

    def test_disconnected_edges_raise(self, verts):
        a, b, c, d = verts
        e1 = Edge(a, b, EdgeKind.UNDIRECTED)
        e2 = Edge(c, d, EdgeKind.UNDIRECTED)
        with pytest.raises(ValueError, match="connected"):
            Walk([e1, e2])

    def test_mixed_kind_edges_raise(self, verts):
        a, b, c, _ = verts
        e1 = Edge(a, b, EdgeKind.UNDIRECTED)
        e2 = Edge(b, c, EdgeKind.DIRECTED)
        with pytest.raises(ValueError, match="same kind"):
            Walk([e1, e2])

    def test_empty_edges_raise(self):
        with pytest.raises(ValueError, match="at least one"):
            Walk([])

    def test_as_graph_returns_unweighted(self, verts):
        a, b, c, _ = verts
        g = (a - b - c).as_graph()
        assert isinstance(g, UnweightedGraph)

    def test_walk_allows_repeated_vertex(self, verts):
        a, b, _, _ = verts
        w = a - b - a - b
        assert w.length == 3

    def test_walk_allows_repeated_edge(self, verts):
        a, b, _, _ = verts
        w = a - b - a
        assert w.length == 2


class TestWeightedWalk:
    def test_basic_chain(self, verts):
        a, b, c, _ = verts
        w = a - 3 - b - 2 - c
        assert isinstance(w, WeightedWalk)
        assert w.length == 2

    def test_weight_sum(self, verts):
        a, b, c, _ = verts
        w = a - 3 - b - 2 - c
        assert w.weight == 5

    def test_vertices_property(self, verts):
        a, b, c, _ = verts
        w = a - 3 - b - 2 - c
        assert w.vertices == [a, b, c]

    def test_kind_directed(self, verts):
        a, b, c, _ = verts
        w = a >> 1 >> b >> 4 >> c
        assert w.kind == EdgeKind.DIRECTED

    def test_is_closed_true(self, verts):
        a, b, c, _ = verts
        w = a - 1 - b - 2 - c - 3 - a
        assert w.is_closed

    def test_as_graph_returns_weighted(self, verts):
        a, b, c, _ = verts
        g = (a - 3 - b - 2 - c).as_graph()
        assert isinstance(g, WeightedGraph)

    def test_weight_float(self, verts):
        a, b, c, _ = verts
        w = a - 1.5 - b - 2.5 - c
        assert w.weight == pytest.approx(4.0)


class TestTrail:
    def test_valid_trail(self, verts):
        a, b, c, _ = verts
        t = Trail([*(a - b - c).edges])
        assert t.length == 2

    def test_repeated_edge_raises(self, verts):
        a, b, _, _ = verts
        e = Edge(a, b, EdgeKind.UNDIRECTED)
        with pytest.raises(ValueError, match="repeated edge"):
            Trail([e, Edge(b, a, EdgeKind.UNDIRECTED), Edge(a, b, EdgeKind.UNDIRECTED)])

    def test_repeated_vertex_allowed(self, verts):
        a, b, c, _ = verts
        t = Trail([*(a - b - c - a).edges])
        assert t.length == 3


class TestPath:
    def test_valid_path(self, verts):
        a, b, c, _ = verts
        p = GPath([*(a - b - c).edges])
        assert p.length == 2

    def test_repeated_vertex_raises(self, verts):
        a, b, c, _ = verts
        with pytest.raises(ValueError, match="repeated vertex"):
            GPath([*(a - b - c - a).edges])

    def test_path_is_also_trail(self, verts):
        a, b, c, _ = verts
        p = GPath([*(a - b - c).edges])
        assert isinstance(p, Trail)
        assert isinstance(p, Walk)


class TestReverseChain:
    """``A << B << C << D`` 가 ``D >> C >> B >> A`` 와 동일한 walk를 만드는지."""

    def test_reverse_chain_unweighted(self, verts):
        a, b, c, d = verts
        back = a << b << c << d
        fwd = d >> c >> b >> a
        assert [(e.src, e.dst) for e in back.edges] == [(e.src, e.dst) for e in fwd.edges]

    def test_reverse_chain_weighted(self, verts):
        a, b, c, d = verts
        back = a << 3 << b << 5 << c << 7 << d
        fwd = d >> 7 >> c >> 5 >> b >> 3 >> a
        assert [(e.src, e.dst, e.weight) for e in back.edges] == [
            (e.src, e.dst, e.weight) for e in fwd.edges
        ]

    def test_reverse_chain_three_vertices(self, verts):
        a, b, c, _ = verts
        w = a << b << c
        assert w.length == 2
        assert w.edges[0].src == c and w.edges[0].dst == b
        assert w.edges[1].src == b and w.edges[1].dst == a
