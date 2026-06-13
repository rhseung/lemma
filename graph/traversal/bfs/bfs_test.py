"""bfs_iterative 테스트 (노드를 yield 하는 제너레이터).

이 구현은 eager — push 시점에 visited 마킹(``visited.add(v)`` 후 enqueue)이라
같은 노드가 큐에 두 번 들어가지 않는다. 따라서 pop 가드(``if u in visited``)도
필요 없다.
"""

import types

from graph.traversal.bfs.bfs import bfs_iterative


def _walk(graph: list[list[int]], start: int) -> list[int]:
    return list(bfs_iterative(graph, start))


# 0 ─▶ 1 ─▶ 3
# │    └──▶ 4
# └──▶ 2 ──▶ 4
SAMPLE = [[1, 2], [3, 4], [4], [], []]


class TestBasic:
    def test_single_node(self):
        assert _walk([[]], 0) == [0]

    def test_start_is_first(self):
        assert _walk(SAMPLE, 0)[0] == 0

    def test_visits_all_reachable_nodes(self):
        assert set(_walk(SAMPLE, 0)) == {0, 1, 2, 3, 4}

    def test_each_node_visited_exactly_once(self):
        order = _walk(SAMPLE, 0)

        assert sorted(order) == [0, 1, 2, 3, 4]
        assert len(order) == len(set(order))

    def test_start_from_nonzero(self):
        assert _walk([[1], [2], []], 1) == [1, 2]

    def test_only_reachable_component(self):
        assert set(_walk([[1], [], [3], []], 0)) == {0, 1}


class TestLevelOrder:
    """BFS 의 정의: 얕은 레벨을 모두 본 뒤 다음 레벨로."""

    def test_visits_level_by_level(self):
        # 레벨0:{0}  레벨1:{1,2}  레벨2:{3,4,5}  (DFS 라면 0,1,3,4,2,5)
        graph = [[1, 2], [3, 4], [5], [], [], []]

        assert _walk(graph, 0) == [0, 1, 2, 3, 4, 5]

    def test_neighbors_within_level_in_adjacency_order(self):
        assert _walk(SAMPLE, 0) == [0, 1, 2, 3, 4]


class TestRevisitGuard:
    def test_cycle_terminates_without_revisiting(self):
        # 0→1→2→0 — 무한 루프 없이 각 노드 1회
        assert _walk([[1], [2], [0]], 0) == [0, 1, 2]

    def test_self_loop(self):
        assert _walk([[0]], 0) == [0]

    def test_diamond_visits_each_once(self):
        # 3 이 1·2 양쪽 이웃이지만 push 시점 마킹이라 큐에 한 번만 들어감
        assert _walk([[1, 2], [3], [3], []], 0) == [0, 1, 2, 3]


class TestLazy:
    def test_returns_lazy_generator(self):
        gen = bfs_iterative(SAMPLE, 0)

        assert isinstance(gen, types.GeneratorType)
        assert next(gen) == 0
