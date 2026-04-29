import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.graph.graph import Graph, UnweightedGraph, WeightedGraph
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
        assert g.has_edge(a - b)
        assert g.has_edge(b - a)
        assert not g.has_edge(a - c)

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

    def test_contains_path_true(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert g.contains_path(a - b - c)

    def test_contains_path_false(self, verts):
        a, b, c, d = verts
        g = UnweightedGraph(a - b - c)
        assert not g.contains_path(a - b - c - d)

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
        assert g.has_edge(a - 3 - b)
        assert g.has_edge(b - 3 - a)
        assert not g.has_edge(a - 1 - c)

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

    def test_contains_path(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        assert g.contains_path(a - b - c)
        assert g.contains_path(a - 3 - b - 2 - c)

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
