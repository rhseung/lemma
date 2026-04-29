import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.graph.graph import FlowGraph, Graph, UnweightedGraph, WeightedGraph
from core.graph.primitives.edge_kind import EdgeKind
from core.graph.primitives.vertex import Vertex


@pytest.fixture
def verts():
    return Vertex("a"), Vertex("b"), Vertex("c"), Vertex("d")


class TestGraphInfer:
    def test_infer_unweighted(self, verts):
        a, b, c, _ = verts
        g = Graph(a - b - c)
        assert isinstance(g, UnweightedGraph)

    def test_infer_weighted(self, verts):
        a, b, c, _ = verts
        g = Graph(a - 3 - b - 2 - c)
        assert isinstance(g, WeightedGraph)


class TestUnweightedGraph:
    def test_build_from_walk(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert g.num_vertices == 3
        assert g.num_edges == 2

    def test_has_vertex(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert g.has_vertex(a)
        assert g.has_vertex(b)
        assert not g.has_vertex(Vertex("z"))

    def test_contains_operator(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert a in g
        assert Vertex("z") not in g
        assert (a - b) in g
        assert (a - c) not in g
        assert (a >> b) not in g  # edge exists but wrong kind
        assert (a - b - c) in g
        assert (a - b - c - Vertex("z")) not in g

    def test_has_edge_undirected(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert g.has_edge(a, b)
        assert g.has_edge(b, a)
        assert g.has_edge(b, c)
        assert not g.has_edge(a, c)

    def test_has_edge_with_edge_object(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert (a - b) in g
        assert (b - a) in g
        assert (a - c) not in g

    def test_has_edge_directed(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a >> b >> c)
        assert g.has_edge(a, b)
        assert not g.has_edge(b, a)

    def test_neighbors_undirected(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert set(g.neighbors(b)) == {a, c}

    def test_neighbors_directed(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a >> b >> c)
        assert list(g.neighbors(a)) == [b]
        assert list(g.neighbors(b)) == [c]
        assert list(g.neighbors(c)) == []

    def test_degree(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert g.degree(a) == 1
        assert g.degree(b) == 2
        assert g.degree(c) == 1

    def test_num_edges_directed(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a >> b >> c)
        assert g.num_edges == 2

    def test_num_vertices_len(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert len(g) == 3

    def test_iter_vertices(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert set(g) == {a, b, c}

    def test_add_vertex_manual(self, verts):
        a, b, c, d = verts
        g = UnweightedGraph(a - b - c)
        g.add_vertex(d)
        assert g.has_vertex(d)
        assert g.num_vertices == 4

    def test_add_edge_manual(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g.add_edge(a, b)
        g.add_edge(b, c)
        assert g.num_vertices == 3
        assert g.num_edges == 2

    def test_empty_graph_default(self):
        g = UnweightedGraph()
        assert g.num_vertices == 0
        assert g.num_edges == 0
        assert g.kind == EdgeKind.UNDIRECTED

    def test_contains_walk_true(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert g.contains_walk(a - b - c)

    def test_contains_walk_false(self, verts):
        a, b, c, d = verts
        g = UnweightedGraph(a - b - c)
        assert not g.contains_walk(a - b - c - d)
        assert not g.contains_walk(a >> b >> c)  # kind mismatch

    def test_validate_passes(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        g._validate()

    def test_bidirected_edge(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a & b & c)
        assert g.has_edge(a, b)
        assert g.has_edge(b, a)
        assert g.kind == EdgeKind.BIDIRECTED

    def test_repr(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert "UnweightedGraph" in repr(g)
        assert "V=3" in repr(g)
        assert "E=2" in repr(g)


class TestWeightedGraph:
    def test_build_from_walk(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        assert g.num_vertices == 3
        assert g.num_edges == 2

    def test_has_edge(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        assert g.has_edge(a, b)
        assert g.has_edge(b, a)
        assert not g.has_edge(a, c)

    def test_has_edge_with_weighted_edge_object(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        assert (a - 3 - b) in g
        assert (b - 3 - a) in g
        assert (a - 1 - c) not in g
        assert (a - 5 - b) not in g  # edge exists but wrong weight

    def test_weighted_neighbors(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        nbrs = dict(g.weighted_neighbors(a))
        assert nbrs[b] == 3

    def test_directed_weighted(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a >> 5 >> b >> 10 >> c)
        assert g.has_edge(a, b)
        assert not g.has_edge(b, a)
        nbrs = dict(g.weighted_neighbors(a))
        assert nbrs[b] == 5

    def test_add_edge_manual(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph[int](kind=EdgeKind.UNDIRECTED)
        g.add_edge(a, b, 7)
        g.add_edge(b, c, 4)
        assert g.num_edges == 2

    def test_num_edges_directed(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a >> 1 >> b >> 2 >> c)
        assert g.num_edges == 2

    def test_contains_walk(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        assert g.contains_walk(a - b - c)
        assert g.contains_walk(a - 3 - b - 2 - c)
        assert not g.contains_walk(a - 5 - b - 2 - c)  # weight mismatch
        assert not g.contains_walk(a >> 3 >> b >> 2 >> c)  # kind mismatch

    def test_float_weights(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 1.5 - b - 2.5 - c)
        nbrs = dict(g.weighted_neighbors(b))
        assert nbrs[a] == pytest.approx(1.5)
        assert nbrs[c] == pytest.approx(2.5)

    def test_validate_passes(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        g._validate()

    def test_repr(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        assert "WeightedGraph" in repr(g)
        assert "V=3" in repr(g)
        assert "E=2" in repr(g)


class TestFlowGraph:
    def test_build_from_walk(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        assert g.num_vertices == 3
        assert g.num_edges == 2

    def test_build_empty(self):
        g = FlowGraph()
        assert g.num_vertices == 0
        assert g.num_edges == 0
        assert g.kind == EdgeKind.DIRECTED

    def test_add_edge_manual(self, verts):
        a, b, _, _ = verts
        g = FlowGraph()
        g.add_edge(a, b, capacity=10)
        assert g.num_vertices == 2
        assert g.num_edges == 1

    def test_has_vertex(self, verts):
        a, b, _, _ = verts
        g = FlowGraph()
        g.add_edge(a, b, capacity=10)
        assert g.has_vertex(a)
        assert g.has_vertex(b)
        assert not g.has_vertex(Vertex("z"))

    def test_reverse_edge_created(self, verts):
        a, b, _, _ = verts
        g = FlowGraph()
        g.add_edge(a, b, capacity=10)
        edges = g.flow_edges(b)
        rev = next(e for e in edges if e.dst == a)
        assert rev.capacity == 0.0
        assert not rev._forward

    def test_rev_link_integrity(self, verts):
        a, b, _, _ = verts
        g = FlowGraph()
        g.add_edge(a, b, capacity=10)
        fwd = g.flow_edges(a)[0]
        assert fwd.reverse_edge is not None
        assert fwd.reverse_edge.reverse_edge is fwd

    def test_residual(self, verts):
        a, b, _, _ = verts
        g = FlowGraph()
        g.add_edge(a, b, capacity=10)
        fwd = g.flow_edges(a)[0]
        assert fwd.residual == 10.0
        fwd.flow = 4.0
        assert fwd.residual == 6.0

    def test_neighbors_positive_residual_only(self, verts):
        a, b, _, _ = verts
        g = FlowGraph()
        g.add_edge(a, b, capacity=10)
        fwd = g.flow_edges(a)[0]
        fwd.flow = 10.0
        assert list(g.neighbors(a)) == []

    def test_validate_passes(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        g._validate()

    def test_repr(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        assert "FlowGraph" in repr(g)
        assert "V=3" in repr(g)
        assert "E=2" in repr(g)

    def test_reject_undirected_walk(self, verts):
        a, b, c, _ = verts
        with pytest.raises(ValueError, match="directed"):
            FlowGraph(a - 10 - b - 5 - c)
