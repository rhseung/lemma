import random

import pytest

from graph.tree.heap import MinHeap


def _drain(heap: MinHeap[int]) -> list[int]:
    """비울 때까지 pop 한 결과 (정렬돼 있어야 정상)."""
    out = []
    while not heap.is_empty():
        out.append(heap.pop())
    return out


def _is_min_heap(data: list[int]) -> bool:
    """모든 노드가 두 자식 이하인지 (힙 불변식) 직접 검사."""
    n = len(data)
    for i in range(n):
        left, right = 2 * i + 1, 2 * i + 2
        if left < n and data[i] > data[left]:
            return False
        if right < n and data[i] > data[right]:
            return False
    return True


class TestHeapChecker:
    """힙 불변식 검사 헬퍼 자체가 위반을 잡는지 (테스트 오라클 검증)."""

    def test_accepts_valid_heap(self):
        assert _is_min_heap([1, 5, 9])

    def test_detects_left_child_violation(self):
        assert not _is_min_heap([5, 1, 9])  # 부모 5 > 왼쪽 자식 1

    def test_detects_right_child_violation(self):
        assert not _is_min_heap([5, 9, 1])  # 부모 5 > 오른쪽 자식 1


class TestBuild:
    def test_empty(self):
        heap = MinHeap[int]()

        assert len(heap) == 0
        assert heap.is_empty()

    def test_single(self):
        heap = MinHeap([42])

        assert len(heap) == 1
        assert not heap.is_empty()
        assert heap.peek() == 42

    def test_heapify_orders_min_to_root(self):
        # 역순 입력 → build 가 상향식 sift-down 으로 최솟값을 루트로 끌어올린다
        heap = MinHeap([9, 7, 5, 3, 1])

        assert heap.peek() == 1
        assert _is_min_heap(heap._data)

    def test_heapify_is_valid_heap_not_sorted(self):
        # heapify 결과는 '정렬'이 아니라 '힙 불변식'만 보장한다
        heap = MinHeap([5, 3, 8, 1, 9, 2, 7])

        assert _is_min_heap(heap._data)
        assert len(heap) == 7

    def test_accepts_any_iterable(self):
        # list 가 아닌 임의 iterable (제너레이터) 도 받는다
        heap = MinHeap(x for x in [4, 2, 6])

        assert heap.peek() == 2
        assert len(heap) == 3


class TestPeek:
    def test_returns_min_without_removing(self):
        heap = MinHeap([3, 1, 2])

        assert heap.peek() == 1
        assert len(heap) == 3  # 제거 안 함
        assert heap.peek() == 1  # 여러 번 호출해도 동일

    def test_empty_raises_index_error(self):
        heap = MinHeap[int]()

        with pytest.raises(IndexError):
            heap.peek()


class TestPush:
    def test_into_empty(self):
        heap = MinHeap[int]()

        heap.push(10)

        assert len(heap) == 1
        assert heap.peek() == 10

    def test_new_minimum_bubbles_to_root(self):
        # 더 작은 값을 넣으면 sift-up 이 루트까지 끌어올린다 (while 이 i==0 에서 종료)
        heap = MinHeap([5, 6, 7])

        heap.push(1)

        assert heap.peek() == 1
        assert _is_min_heap(heap._data)

    def test_larger_value_stays_down(self):
        # 큰 값은 부모보다 작지 않아 즉시 break (sift-up 의 else 분기)
        heap = MinHeap([1, 2, 3])

        heap.push(99)

        assert heap.peek() == 1
        assert _is_min_heap(heap._data)
        assert len(heap) == 4

    def test_keeps_heap_invariant_across_pushes(self):
        heap = MinHeap[int]()

        for value in [5, 3, 8, 1, 9, 2, 7, 0]:
            heap.push(value)
            assert _is_min_heap(heap._data)

        assert heap.peek() == 0


class TestPop:
    def test_returns_minimum_not_last(self):
        # 회귀 테스트: pop 은 루트(최솟값)를 반환해야지 마지막 잎을 반환하면 안 된다
        heap = MinHeap([5, 3, 8, 1, 9, 2])

        assert heap.pop() == 1

    def test_drains_in_sorted_order(self):
        heap = MinHeap([5, 3, 8, 1, 9, 2, 7, 4, 6, 0])

        assert _drain(heap) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_single_element_does_not_crash(self):
        # 회귀 테스트: 마지막 원소 pop 시 빈 리스트에 _data[0] 대입하면 IndexError
        heap = MinHeap([42])

        assert heap.pop() == 42
        assert heap.is_empty()
        assert len(heap) == 0

    def test_two_elements(self):
        heap = MinHeap([2, 1])

        assert heap.pop() == 1
        assert heap.pop() == 2
        assert heap.is_empty()

    def test_empty_raises_index_error(self):
        heap = MinHeap[int]()

        with pytest.raises(IndexError):
            heap.pop()

    def test_sift_down_when_only_left_child(self):
        # pop 후 루트가 sift-down: 오른쪽 자식이 범위 밖인 경로 (right >= len)
        heap = MinHeap([1, 2, 3])

        assert heap.pop() == 1  # 3 이 루트로 → 왼쪽(2)과만 비교
        assert heap.peek() == 2
        assert _is_min_heap(heap._data)

    def test_sift_down_picks_right_child(self):
        # 오른쪽 자식이 왼쪽보다 작아 right 가 smallest 가 되는 경로
        heap = MinHeap[int]()
        for value in [1, 5, 2, 6, 7]:
            heap.push(value)
        # 루트 1 제거 → 마지막 잎이 루트로 와서 오른쪽 자식 쪽으로 내려가야 함
        heap.pop()

        assert heap.peek() == 2
        assert _is_min_heap(heap._data)

    def test_interleaved_push_pop(self):
        heap = MinHeap[int]()

        heap.push(5)
        heap.push(3)
        assert heap.pop() == 3
        heap.push(1)
        heap.push(4)
        assert heap.pop() == 1
        assert heap.pop() == 4
        assert heap.pop() == 5
        assert heap.is_empty()

    def test_handles_duplicate_keys(self):
        heap = MinHeap([3, 1, 3, 1, 2, 2])

        assert _drain(heap) == [1, 1, 2, 2, 3, 3]


class TestDunder:
    def test_len_tracks_size(self):
        heap = MinHeap([1, 2, 3])

        assert len(heap) == 3
        heap.push(4)
        assert len(heap) == 4
        heap.pop()
        assert len(heap) == 3

    def test_repr_shows_backing_list(self):
        heap = MinHeap([3, 1, 2])

        assert repr(heap) == f"MinHeap({heap._data!r})"
        assert repr(heap).startswith("MinHeap([")


class TestProperty:
    def test_random_inputs_sort_correctly(self):
        # build → drain 은 항상 정렬과 같다 (heap-sort)
        for _ in range(50):
            data = [random.randint(-100, 100) for _ in range(random.randint(0, 30))]

            heap = MinHeap(data)

            assert _drain(heap) == sorted(data)

    def test_random_pushes_keep_invariant(self):
        heap = MinHeap[int]()
        pushed = []

        for _ in range(100):
            value = random.randint(-100, 100)
            heap.push(value)
            pushed.append(value)
            assert _is_min_heap(heap._data)

        assert _drain(heap) == sorted(pushed)
