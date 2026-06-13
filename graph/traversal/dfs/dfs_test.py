"""dfs_recursive / dfs_iterative 테스트 (둘 다 노드를 yield 하는 제너레이터).

공유 동작(도달 가능한 노드 1회씩, 사이클 종료 등)은 variant 로 묶어 두 구현에
동일하게 적용한다. iterative 는 reversed(graph[u]) 로 push 하므로 방문 '순서'까지
recursive 와 같아야 한다 — 이를 별도로 검증한다.
"""

import types

import pytest

from graph.traversal.dfs.dfs import dfs_iterative, dfs_recursive

VARIANTS = ["iterative", "recursive"]


@pytest.fixture(params=VARIANTS)
def variant(request) -> str:
    return request.param


def _walk(variant: str, graph: list[list[int]], start: int) -> list[int]:
    """variant 제너레이터를 끝까지 소비해 방문 순서를 리스트로 돌려준다."""
    if variant == "iterative":
        return list(dfs_iterative(graph, start))
    return list(dfs_recursive(graph, start, set()))


def _gen(variant: str, graph: list[list[int]], start: int):
    if variant == "iterative":
        return dfs_iterative(graph, start)
    return dfs_recursive(graph, start, set())


# 0 ─▶ 1 ─▶ 3
# │    └──▶ 4
# └──▶ 2 ──▶ 4
SAMPLE = [[1, 2], [3, 4], [4], [], []]


class TestShared:
    """두 구현이 똑같이 만족해야 하는 성질."""

    def test_single_node(self, variant: str):
        assert _walk(variant, [[]], 0) == [0]

    def test_start_is_first(self, variant: str):
        assert _walk(variant, SAMPLE, 0)[0] == 0

    def test_visits_all_reachable_nodes(self, variant: str):
        assert set(_walk(variant, SAMPLE, 0)) == {0, 1, 2, 3, 4}

    def test_each_node_visited_exactly_once(self, variant: str):
        # 다이아몬드: 3 으로 가는 경로가 둘이라도 한 번만
        order = _walk(variant, [[1, 2], [3], [3], []], 0)

        assert sorted(order) == [0, 1, 2, 3]
        assert len(order) == len(set(order))

    def test_cycle_terminates_without_revisiting(self, variant: str):
        assert _walk(variant, [[1], [2], [0]], 0) == [0, 1, 2]

    def test_self_loop(self, variant: str):
        assert _walk(variant, [[0]], 0) == [0]

    def test_only_reachable_component(self, variant: str):
        # 0→1 과 2→3 은 분리 — 0 에서 시작하면 2,3 은 안 보인다
        assert set(_walk(variant, [[1], [], [3], []], 0)) == {0, 1}

    def test_start_from_nonzero(self, variant: str):
        assert _walk(variant, [[1], [2], []], 1) == [1, 2]

    def test_neighbor_already_visited_is_skipped(self, variant: str):
        # 이웃이 이미 방문됨 → 재방문 안 함 (양쪽 visited 가드 분기)
        order = _walk(variant, [[1, 2], [], [1]], 0)

        assert sorted(order) == [0, 1, 2]

    def test_returns_lazy_generator(self, variant: str):
        gen = _gen(variant, SAMPLE, 0)

        assert isinstance(gen, types.GeneratorType)
        assert next(gen) == 0  # 첫 값만 뽑아도 동작 (지연 평가)


class TestRecursiveOrder:
    def test_visits_in_adjacency_list_order(self):
        # 재귀형은 graph[u] 순서대로 첫 이웃의 서브트리를 끝까지 판다
        assert _walk("recursive", SAMPLE, 0) == [0, 1, 3, 4, 2]


class TestIterativeOrder:
    def test_visits_in_adjacency_list_order(self):
        # reversed(graph[u]) push → stack(LIFO)이 되뒤집어 첫 이웃부터
        assert _walk("iterative", SAMPLE, 0) == [0, 1, 3, 4, 2]


class TestOrderMatchesRecursive:
    @pytest.mark.parametrize(
        "graph, start",
        [
            (SAMPLE, 0),
            ([[1, 2], [3], [3], []], 0),  # 다이아몬드
            ([[1], [2], [0]], 0),  # 사이클
            ([[2, 1], [], [1]], 0),  # 이웃이 오름차순이 아닌 경우
        ],
    )
    def test_iterative_equals_recursive(self, graph, start):
        # reversed 덕분에 방문 순서까지 두 구현이 동일
        assert _walk("iterative", graph, start) == _walk("recursive", graph, start)
