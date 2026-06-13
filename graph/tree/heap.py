"""배열 기반 이진 최소 힙 (암묵적 완전이진트리).

인덱스(0-인덱스): parent(i)=(i-1)//2, left(i)=2i+1, right(i)=2i+2.
한 줄 산술이라 메서드로 빼지 않고 sift에서 직접 쓴다.
"""

from collections.abc import Iterable
from typing import Protocol, Self


class _Comparable(Protocol):
    def __lt__(self, other: Self, /) -> bool: ...


class MinHeap[T: _Comparable]:
    """평탄한 리스트 기반 이진 최소 힙.

    모든 노드 <= 두 자식 → _data[0]이 항상 최소. peek O(1), push/pop
    O(log n), build(__init__) O(n).
    """

    _data: list[T]

    # --- 생성 ---
    def __init__(self, iterable: Iterable[T] = ()) -> None:
        """iterable을 O(n)에 heapify 한다 (상향식 build, 개별 push 아님)."""
        self._data = list(iterable)
        self._len = len(self._data)
        self._heapify()

    def _heapify(self) -> None:
        """마지막 내부 노드(len//2-1)부터 0까지 sift-down. in-place, O(n)."""
        for i in range(len(self) // 2 - 1, -1, -1):
            self._sift_down(i)

    # --- 던더 ---
    def __len__(self) -> int:
        return self._len

    def __repr__(self) -> str:
        return f"MinHeap({self._data!r})"

    # --- 내부 복구 ---
    def _sift_up(self, i: int) -> None:
        """i를 부모보다 작은 동안 위로 교환."""
        while i > 0:
            parent_i = (i - 1) // 2  # NOTE: i == 0이면 -1이므로 while 조건 중요
            if self._data[i] < self._data[parent_i]:
                self._data[i], self._data[parent_i] = self._data[parent_i], self._data[i]
                i = parent_i
            else:
                break

    def _sift_down(self, i: int) -> None:
        """i를 더 작은 자식(2i+1, 2i+2)과 아래로 교환. 자식 인덱스 범위 검사 필수."""
        while True:
            # 이렇게 하면 엘레강스하게 부모와 왼쪽, 오른쪽 자식 중 가장 작은 녀석을 smallest로 쉽게 찾을 수 있다. 인덱스 범위 조건까지 한 번에 고려.
            smallest, left, right = i, 2 * i + 1, 2 * i + 2
            if left < len(self) and self._data[left] < self._data[smallest]:
                smallest = left
            if right < len(self) and self._data[right] < self._data[smallest]:
                smallest = right

            if smallest == i:  # 뭐야 부모가 제일 작네 sift down 중지
                break

            self._data[smallest], self._data[i] = self._data[i], self._data[smallest]
            i = smallest

    # --- 공개 API ---
    def is_empty(self) -> bool:
        return self._len == 0

    def peek(self) -> T:
        """최소값 반환(제거 없음). 비면 IndexError."""
        if self.is_empty():
            raise IndexError()

        return self._data[0]

    def push(self, value: T) -> None:
        """끝에 추가 후 sift up. O(log n)."""
        self._data.append(value)
        self._len += 1
        self._sift_up(self._len - 1)

    def pop(self) -> T:
        """최소값 제거 후 반환: 루트↔마지막 swap → 떼어내고 sift down. 비면 IndexError."""
        if self.is_empty():
            raise IndexError()

        root = self._data[0]
        last = self._data.pop()
        self._len -= 1
        if self._len > 0:
            self._data[0] = last
            self._sift_down(0)

        return root
