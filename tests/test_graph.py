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
        edges = g.edges(b)
        rev = next(e for e in edges if e.dst == a)
        assert rev.capacity == 0.0
        assert not rev._forward

    def test_rev_link_integrity(self, verts):
        a, b, _, _ = verts
        g = FlowGraph()
        g.add_edge(a, b, capacity=10)
        fwd = g.edges(a)[0]
        assert fwd.reverse_edge is not None
        assert fwd.reverse_edge.reverse_edge is fwd

    def test_residual(self, verts):
        a, b, _, _ = verts
        g = FlowGraph()
        g.add_edge(a, b, capacity=10)
        fwd = g.edges(a)[0]
        assert fwd.residual == 10.0
        fwd.flow = 4
        assert fwd.residual == 6.0

    def test_neighbors_all_forward(self, verts):
        a, b, _, _ = verts
        g = FlowGraph()
        g.add_edge(a, b, capacity=10)
        fwd = g.edges(a)[0]
        fwd.flow = 10
        assert list(g.neighbors(a)) == [b]

    def test_neighbors_residual_positive_residual_only(self, verts):
        a, b, _, _ = verts
        g = FlowGraph()
        g.add_edge(a, b, capacity=10)
        fwd = g.edges(a)[0]
        fwd.flow = 10
        assert list(g.neighbors_residual(a)) == []

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


class TestUnweightedGraphIO:
    def test_from_edge_list_string_labels(self):
        g = UnweightedGraph.from_edge_list([("a", "b"), ("b", "c")])
        assert g.num_vertices == 3
        assert g.num_edges == 2
        assert g.has_edge(Vertex("a"), Vertex("b"))

    def test_from_edge_list_vertex_objects(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph.from_edge_list([(a, b), (b, c)])
        assert g.num_edges == 2

    def test_from_edge_list_directed(self):
        g = UnweightedGraph.from_edge_list([("a", "b"), ("b", "c")], kind=EdgeKind.DIRECTED)
        assert g.kind == EdgeKind.DIRECTED
        assert g.has_edge(Vertex("a"), Vertex("b"))
        assert not g.has_edge(Vertex("b"), Vertex("a"))

    def test_to_edge_list_undirected(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        edges = g.to_edge_list()
        assert len(edges) == 2
        assert ("a", "b") in edges
        assert ("b", "c") in edges

    def test_to_edge_list_directed(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a >> b >> c)
        edges = g.to_edge_list()
        assert ("a", "b") in edges
        assert ("b", "c") in edges
        assert len(edges) == 2

    def test_to_json_from_json_roundtrip(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        g2 = UnweightedGraph.from_json(g.to_json())
        assert g2.num_vertices == 3
        assert g2.num_edges == 2
        assert g2.kind == EdgeKind.UNDIRECTED
        assert set(g2.to_edge_list()) == set(g.to_edge_list())

    def test_json_directed_roundtrip(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a >> b >> c)
        g2 = UnweightedGraph.from_json(g.to_json())
        assert g2.kind == EdgeKind.DIRECTED
        assert g2.has_edge(Vertex("a"), Vertex("b"))
        assert not g2.has_edge(Vertex("b"), Vertex("a"))

    def test_to_dot_from_dot_roundtrip(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        g2 = UnweightedGraph.from_dot(g.to_dot())
        assert g2.num_vertices == 3
        assert g2.num_edges == 2

    def test_dot_directed_roundtrip(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a >> b >> c)
        g2 = UnweightedGraph.from_dot(g.to_dot())
        assert g2.kind == EdgeKind.DIRECTED

    def test_to_adjacency_matrix(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        mat = g.to_adjacency_matrix()
        assert len(mat) == 3
        # 대칭 행렬 확인
        for i in range(3):
            for j in range(3):
                assert mat[i][j] == mat[j][i]

    def test_adjacency_matrix_roundtrip(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        labels = [v.label for v in g.vertices()]
        mat = g.to_adjacency_matrix()
        g2 = UnweightedGraph.from_adjacency_matrix(mat, labels)
        assert g2.num_edges == g.num_edges

    def test_A_property(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert g.to_adjacency_matrix() == g.A

    def test_isolated_vertex_preserved_in_dot(self, verts):
        a, b, c, d = verts
        g = UnweightedGraph(a - b - c)
        g.add_vertex(d)
        g2 = UnweightedGraph.from_dot(g.to_dot())
        assert g2.num_vertices == 4

    def test_isolated_vertex_preserved_in_json(self, verts):
        a, b, c, d = verts
        g = UnweightedGraph(a - b - c)
        g.add_vertex(d)
        g2 = UnweightedGraph.from_json(g.to_json())
        assert g2.num_vertices == 4


class TestWeightedGraphIO:
    def test_from_edge_list_string_labels(self):
        g = WeightedGraph.from_edge_list([("a", "b", 3), ("b", "c", 2)])
        assert g.num_edges == 2
        assert g.get_edge(Vertex("a"), Vertex("b")).weight == 3

    def test_from_edge_list_vertex_objects(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph.from_edge_list([(a, b, 5), (b, c, 7)])
        assert g.get_edge(a, b).weight == 5

    def test_to_edge_list(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        edges = g.to_edge_list()
        assert len(edges) == 2
        assert ("a", "b", 3) in edges
        assert ("b", "c", 2) in edges

    def test_to_json_from_json_roundtrip(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        g2 = WeightedGraph.from_json(g.to_json())
        assert g2.num_edges == 2
        assert g2.get_edge(Vertex("a"), Vertex("b")).weight == 3

    def test_to_dot_from_dot_roundtrip(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        g2 = WeightedGraph.from_dot(g.to_dot())
        assert g2.num_edges == 2
        assert g2.get_edge(Vertex("a"), Vertex("b")).weight == 3

    def test_dot_directed_weights(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a >> 5 >> b >> 10 >> c)
        g2 = WeightedGraph.from_dot(g.to_dot())
        assert g2.kind == EdgeKind.DIRECTED
        assert g2.get_edge(Vertex("a"), Vertex("b")).weight == 5

    def test_float_weights_roundtrip(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 1.5 - b - 2.5 - c)
        g2 = WeightedGraph.from_dot(g.to_dot())
        assert g2.get_edge(Vertex("a"), Vertex("b")).weight == pytest.approx(1.5)

    def test_to_adjacency_matrix(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        mat = g.to_adjacency_matrix()
        verts_list = g.vertices()
        idx = {v.label: i for i, v in enumerate(verts_list)}
        assert mat[idx["a"]][idx["b"]] == 3
        assert mat[idx["b"]][idx["c"]] == 2
        assert mat[idx["a"]][idx["c"]] is None

    def test_adjacency_matrix_roundtrip(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        labels = [v.label for v in g.vertices()]
        mat = g.to_adjacency_matrix()
        g2 = WeightedGraph.from_adjacency_matrix(mat, labels)
        assert g2.num_edges == g.num_edges
        assert g2.get_edge(Vertex("a"), Vertex("b")).weight == 3

    def test_A_property(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        assert g.to_adjacency_matrix() == g.A


class TestFlowGraphIO:
    def test_from_edge_list(self, verts):
        a, b, c, _ = verts
        g = FlowGraph.from_edge_list([(a, b, 10), (b, c, 5)])
        assert g.num_edges == 2
        assert g.get_edge(a, b).capacity == 10

    def test_from_edge_list_string_labels(self):
        g = FlowGraph.from_edge_list([("s", "a", 10), ("a", "t", 5)])
        assert g.num_edges == 2

    def test_to_edge_list(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        edges = g.to_edge_list()
        assert len(edges) == 2
        assert ("a", "b", 10) in edges
        assert ("b", "c", 5) in edges

    def test_to_json_from_json_roundtrip(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        g2 = FlowGraph.from_json(g.to_json())
        assert g2.num_edges == 2
        assert g2.get_edge(a, b).capacity == 10

    def test_to_adjacency_matrix(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        mat = g.to_adjacency_matrix()
        verts_list = g.vertices()
        idx = {v.label: i for i, v in enumerate(verts_list)}
        assert mat[idx["a"]][idx["b"]] == 10
        assert mat[idx["b"]][idx["c"]] == 5
        assert mat[idx["a"]][idx["c"]] is None

    def test_adjacency_matrix_roundtrip(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        labels = [v.label for v in g.vertices()]
        mat = g.to_adjacency_matrix()
        g2 = FlowGraph.from_adjacency_matrix(mat, labels)
        assert g2.num_edges == g.num_edges

    def test_A_property(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        assert g.to_adjacency_matrix() == g.A


class TestUnweightedGraphDSL:
    def test_delete_vertex_removes_edges(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        g.delete_vertex(b)
        assert not g.has_vertex(b)
        assert g.num_vertices == 2
        assert g.num_edges == 0

    def test_delete_vertex_not_found(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        with pytest.raises(KeyError):
            g.delete_vertex(Vertex("z"))

    def test_delete_edge_undirected(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        g.delete_edge(a, b)
        assert not g.has_edge(a, b)
        assert not g.has_edge(b, a)
        assert g.num_vertices == 3
        assert g.num_edges == 1

    def test_delete_edge_not_found(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        with pytest.raises(KeyError):
            g.delete_edge(a, c)

    def test_reverse_directed(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a >> b >> c)
        r = g.reverse()
        assert r.has_edge(b, a)
        assert r.has_edge(c, b)
        assert not r.has_edge(a, b)
        assert g.has_edge(a, b)  # original unchanged

    def test_reverse_undirected_raises(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        with pytest.raises(ValueError):
            g.reverse()

    def test_neg_operator(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a >> b >> c)
        r = -g
        assert r.has_edge(b, a)
        assert not r.has_edge(a, b)

    def test_complement(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        comp = g.complement()
        assert comp.has_edge(a, c)
        assert not comp.has_edge(a, b)
        assert not comp.has_edge(b, c)

    def test_invert_operator(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        comp = ~g
        assert comp.has_edge(a, c)
        assert not comp.has_edge(a, b)

    def test_iadd_vertex(self, verts):
        a, b, c, d = verts
        g = UnweightedGraph(a - b - c)
        g += d
        assert g.has_vertex(d)
        assert g.num_vertices == 4

    def test_iadd_walk(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g += (a - b - c)
        assert g.has_edge(a, b)
        assert g.has_edge(b, c)

    def test_isub_vertex(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        g -= b
        assert not g.has_vertex(b)
        assert g.num_edges == 0

    def test_isub_walk(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        g -= (a - b)
        assert not g.has_edge(a, b)
        assert g.has_edge(b, c)

    def test_union(self, verts):
        a, b, c, d = verts
        g1 = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g1.add_edge(a, b)
        g2 = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g2.add_edge(c, d)
        g3 = g1.union(g2)
        assert g3.has_edge(a, b)
        assert g3.has_edge(c, d)
        assert g3.num_edges == 2

    def test_disjoint_union_conflict_raises(self, verts):
        a, b, c, _ = verts
        g1 = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g1.add_edge(a, b)
        g2 = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g2.add_edge(b, c)
        with pytest.raises(ValueError):
            g1.disjoint_union(g2)

    def test_add_graphs(self, verts):
        a, b, c, d = verts
        g1 = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g1.add_edge(a, b)
        g2 = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g2.add_edge(c, d)
        g3 = g1 + g2
        assert g3.num_edges == 2
        assert g1.num_edges == 1  # original unchanged

    def test_add_vertex(self, verts):
        a, b, c, d = verts
        g = UnweightedGraph(a - b - c)
        g2 = g + d
        assert g2.has_vertex(d)
        assert not g.has_vertex(d)  # original unchanged

    def test_sub_vertex(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        g2 = g - b
        assert not g2.has_vertex(b)
        assert g.has_vertex(b)  # original unchanged

    def test_sub_walk(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        g2 = g - (a - b)
        assert not g2.has_edge(a, b)
        assert g2.has_edge(b, c)
        assert g.has_edge(a, b)  # original unchanged

    def test_or_operator(self, verts):
        a, b, c, d = verts
        g1 = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g1.add_edge(a, b)
        g2 = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g2.add_edge(c, d)
        g3 = g1 | g2
        assert g3.num_vertices == 4
        assert g3.num_edges == 2

    def test_or_conflict_raises(self, verts):
        a, b, c, _ = verts
        g1 = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g1.add_edge(a, b)
        g2 = UnweightedGraph(kind=EdgeKind.UNDIRECTED)
        g2.add_edge(b, c)
        with pytest.raises(ValueError):
            g1 | g2

    def test_getitem_vertex(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        assert set(g[b]) == {a, c}  # type: ignore[arg-type]

    def test_getitem_edge(self, verts):
        a, b, c, _ = verts
        g = UnweightedGraph(a - b - c)
        e = g[a, b]
        assert e.src == a  # type: ignore[union-attr]
        assert e.dst == b  # type: ignore[union-attr]


class TestWeightedGraphDSL:
    def test_delete_vertex(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        g.delete_vertex(b)
        assert not g.has_vertex(b)
        assert g.num_edges == 0

    def test_delete_vertex_not_found(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        with pytest.raises(KeyError):
            g.delete_vertex(Vertex("z"))

    def test_delete_edge(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        g.delete_edge(a, b)
        assert not g.has_edge(a, b)
        assert g.num_edges == 1

    def test_delete_edge_not_found(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        with pytest.raises(KeyError):
            g.delete_edge(a, c)

    def test_reverse(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a >> 3 >> b >> 2 >> c)
        r = g.reverse()
        assert r.has_edge(b, a)
        assert r.get_edge(b, a).weight == 3
        assert not r.has_edge(a, b)
        assert g.has_edge(a, b)  # original unchanged

    def test_reverse_undirected_raises(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        with pytest.raises(ValueError):
            g.reverse()

    def test_set_edge_new(self, verts):
        a, b, _, _ = verts
        g = WeightedGraph[int](kind=EdgeKind.DIRECTED)
        g.set_edge(a, b, 5)
        assert g.get_edge(a, b).weight == 5

    def test_set_edge_overwrite(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        g.set_edge(a, b, 99)
        assert g.get_edge(a, b).weight == 99
        assert g.num_edges == 2

    def test_setitem(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        g[a, b] = 99
        assert g.get_edge(a, b).weight == 99
        assert g.num_edges == 2

    def test_iadd_vertex(self, verts):
        a, b, c, d = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        g += d
        assert g.has_vertex(d)
        assert g.num_vertices == 4

    def test_iadd_walk(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph[int](kind=EdgeKind.UNDIRECTED)
        g += (a - 3 - b - 2 - c)
        assert g.has_edge(a, b)
        assert g.get_edge(a, b).weight == 3

    def test_union(self, verts):
        a, b, c, d = verts
        g1 = WeightedGraph[int](kind=EdgeKind.UNDIRECTED)
        g1.add_edge(a, b, 3)
        g2 = WeightedGraph[int](kind=EdgeKind.UNDIRECTED)
        g2.add_edge(c, d, 5)
        g3 = g1 + g2
        assert g3.has_edge(a, b)
        assert g3.has_edge(c, d)
        assert g3.get_edge(c, d).weight == 5

    def test_getitem_vertex(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        assert set(g[b]) == {a, c}  # type: ignore[arg-type]

    def test_getitem_edge(self, verts):
        a, b, c, _ = verts
        g = WeightedGraph(a - 3 - b - 2 - c)
        e = g[a, b]
        assert e.weight == 3  # type: ignore[union-attr]


class TestFlowGraphDSL:
    def test_delete_edge(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        g.delete_edge(a, b)
        assert not g.has_edge(a, b)
        assert g.num_edges == 1
        g._validate()

    def test_delete_edge_not_found(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        with pytest.raises(KeyError):
            g.delete_edge(a, c)

    def test_delete_vertex(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        g.delete_vertex(b)
        assert not g.has_vertex(b)
        assert g.num_edges == 0
        g._validate()

    def test_delete_vertex_not_found(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        with pytest.raises(KeyError):
            g.delete_vertex(Vertex("z"))

    def test_reverse(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        r = g.reverse()
        assert r.has_edge(b, a)
        assert r.get_edge(b, a).capacity == 10
        assert not r.has_edge(a, b)
        assert g.has_edge(a, b)  # original unchanged

    def test_iadd_vertex(self, verts):
        a, b, c, d = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        g += d
        assert g.has_vertex(d)
        assert g.num_edges == 2

    def test_iadd_flow_edge(self, verts):
        a, b, c, _ = verts
        g = FlowGraph()
        g.add_edge(a, b, 10)
        fwd = g.get_edge(a, b)
        g2 = FlowGraph()
        g2 += fwd
        assert g2.has_edge(a, b)
        assert g2.get_edge(a, b).capacity == 10

    def test_set_capacity(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        fwd = g.get_edge(a, b)
        fwd.flow = 4
        g.set_capacity(a, b, 20)
        assert g.get_edge(a, b).capacity == 20
        assert g.get_edge(a, b).flow == 4  # flow preserved

    def test_setitem(self, verts):
        a, b, c, _ = verts
        g = FlowGraph(a >> 10 >> b >> 5 >> c)
        g[a, b] = 99
        assert g.get_edge(a, b).capacity == 99
        g._validate()


class TestGraphFactoryIO:
    def test_from_edge_list_unweighted(self):
        g = Graph.from_edge_list([("a", "b"), ("b", "c")])
        assert isinstance(g, UnweightedGraph)
        assert g.num_edges == 2

    def test_from_edge_list_weighted(self):
        g = Graph.from_edge_list([("a", "b", 3), ("b", "c", 2)])
        assert isinstance(g, WeightedGraph)
        assert g.num_edges == 2

    def test_from_dot_unweighted(self, verts):
        a, b, c, _ = verts
        dot = UnweightedGraph(a - b - c).to_dot()
        g = Graph.from_dot(dot)
        assert isinstance(g, UnweightedGraph)

    def test_from_dot_weighted(self, verts):
        a, b, c, _ = verts
        dot = WeightedGraph(a - 3 - b - 2 - c).to_dot()
        g = Graph.from_dot(dot)
        assert isinstance(g, WeightedGraph)

    def test_from_json_unweighted(self, verts):
        a, b, c, _ = verts
        js = UnweightedGraph(a - b - c).to_json()
        g = Graph.from_json(js)
        assert isinstance(g, UnweightedGraph)

    def test_from_json_weighted(self, verts):
        a, b, c, _ = verts
        js = WeightedGraph(a - 3 - b - 2 - c).to_json()
        g = Graph.from_json(js)
        assert isinstance(g, WeightedGraph)

    def test_from_json_flow(self, verts):
        a, b, c, _ = verts
        js = FlowGraph(a >> 10 >> b >> 5 >> c).to_json()
        g = Graph.from_json(js)
        assert isinstance(g, FlowGraph)

    def test_from_adjacency_matrix_unweighted(self):
        m = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        g = Graph.from_adjacency_matrix(m, ["a", "b", "c"])
        assert isinstance(g, UnweightedGraph)
        assert g.num_edges == 2

    def test_from_adjacency_matrix_weighted(self):
        m = [[None, 3, None], [3, None, 2], [None, 2, None]]
        g = Graph.from_adjacency_matrix(m, ["a", "b", "c"])
        assert isinstance(g, WeightedGraph)
        assert g.get_edge(Vertex("a"), Vertex("b")).weight == 3
