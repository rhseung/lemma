import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.graph.primitives.edge import Edge, _WeightedEdgeBuilder
from core.graph.primitives.edge_kind import EdgeKind
from core.graph.primitives.vertex import Vertex


@pytest.fixture
def uvw():
    return Vertex("u"), Vertex("v"), Vertex("w")


class TestVertexBasic:
    def test_label(self):
        v = Vertex("x")
        assert v.label == "x"

    def test_str(self):
        assert str(Vertex("a")) == "a"

    def test_equality(self, uvw):
        u, v, _ = uvw
        assert u == Vertex("u")
        assert u != v

    def test_frozen(self, uvw):
        u, _, _ = uvw
        with pytest.raises((AttributeError, TypeError)):
            u.label = "z"  # type: ignore[misc]

    def test_hashable(self, uvw):
        u, v, _ = uvw
        s = {u, v, Vertex("u")}
        assert len(s) == 2


class TestVertexDSL:
    def test_sub_vertex_returns_edge(self, uvw):
        u, v, _ = uvw
        e = u - v
        assert isinstance(e, Edge)
        assert e.src == u and e.dst == v
        assert e.kind == EdgeKind.UNDIRECTED

    def test_rshift_vertex_returns_directed_edge(self, uvw):
        u, v, _ = uvw
        e = u >> v
        assert isinstance(e, Edge)
        assert e.kind == EdgeKind.DIRECTED

    def test_lshift_vertex_returns_directed_edge_reversed(self, uvw):
        u, v, _ = uvw
        e = u << v
        assert isinstance(e, Edge)
        assert e.src == v and e.dst == u
        assert e.kind == EdgeKind.DIRECTED

    def test_and_vertex_returns_bidirected_edge(self, uvw):
        u, v, _ = uvw
        e = u & v
        assert isinstance(e, Edge)
        assert e.kind == EdgeKind.BIDIRECTED

    def test_sub_weight_returns_builder(self, uvw):
        u, _, _ = uvw
        b = u - 5
        assert isinstance(b, _WeightedEdgeBuilder)
        assert b.src == u and b.weight == 5
        assert b.kind == EdgeKind.UNDIRECTED

    def test_rshift_weight_returns_directed_builder(self, uvw):
        u, _, _ = uvw
        b = u >> 3
        assert isinstance(b, _WeightedEdgeBuilder)
        assert b.kind == EdgeKind.DIRECTED

    def test_and_weight_returns_bidirected_builder(self, uvw):
        u, _, _ = uvw
        b = u & 7
        assert isinstance(b, _WeightedEdgeBuilder)
        assert b.kind == EdgeKind.BIDIRECTED
