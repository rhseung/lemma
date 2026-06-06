from typing import cast


class CircularDeque[T]:
    """Ring buffer 기반 deque ADT.

    Deque는 양쪽 끝에서 삽입과 삭제를 지원하는 선형 자료구조다.
    Queue는 이 ADT에서 push_back과 pop_front만 사용하는 제한판으로 볼 수 있다.

    이 구현의 핵심 불변식:
    - front는 첫 원소가 들어 있는 칸을 가리킨다.
    - rear는 마지막 원소 다음 빈 칸, 즉 다음 push_back 위치를 가리킨다.
    - i번째 원소의 실제 위치는 (front + i) % capacity 이다.
    """

    def __init__(self, capacity: int):
        """초기 용량을 가진 빈 deque를 만든다."""
        self._capacity = capacity
        self._content: list[T | None] = [None] * capacity
        self._front = 0
        self._rear = 0
        self._len = 0

    def __len__(self) -> int:
        """저장된 원소 개수를 반환한다. 시간복잡도는 O(1)."""
        return self._len

    def as_list(self) -> list[T]:
        """앞에서 뒤 순서로 원소를 list로 반환한다. 시간복잡도는 O(n)."""
        if self.is_empty():
            return []
        elif self._front < self._rear:
            return cast(list[T], self._content[self._front : self._rear])
        else:
            return cast(list[T], self._content[self._front :] + self._content[: self._rear])

    def __str__(self) -> str:
        """앞에서 뒤 순서로 원소를 문자열로 표현한다. 시간복잡도는 O(n)."""
        return str(self.as_list())

    def is_empty(self) -> bool:
        """deque가 비어 있으면 True를 반환한다. 시간복잡도는 O(1)."""
        return self._front == self._rear and self._len == 0

    def push_front(self, value: T):
        """맨 앞에 값을 추가한다. 시간복잡도는 O(1).

        외우는 구조:
        1. 가득 찼으면 IndexError를 발생시킨다.
        2. front를 한 칸 왼쪽으로 순환 이동한다.
        3. front 위치에 값을 넣고 len을 1 증가시킨다.
        """
        if self._len == self._capacity:
            raise IndexError()

        self._front = (self._front - 1 + self._capacity) % self._capacity
        self._content[self._front] = value
        self._len += 1

    def push_back(self, value: T):
        """맨 뒤에 값을 추가한다. 시간복잡도는 O(1).

        외우는 구조:
        1. 가득 찼으면 IndexError를 발생시킨다.
        2. rear 위치에 값을 넣는다.
        3. rear를 한 칸 오른쪽으로 순환 이동하고 len을 1 증가시킨다.
        """
        if self._len == self._capacity:
            raise IndexError()

        self._content[self._rear] = value
        self._rear = (self._rear + 1) % self._capacity
        self._len += 1

    def pop_front(self) -> T:
        """맨 앞 값을 제거해서 반환한다. 시간복잡도는 O(1).

        외우는 구조:
        1. 비어 있으면 IndexError를 발생시킨다.
        2. front 위치의 값을 저장하고 그 칸을 비운다.
        3. front를 한 칸 오른쪽으로 순환 이동한다.
        4. len을 1 감소시키고 저장한 값을 반환한다.
        """
        if self._len == 0:
            raise IndexError()

        r = self._content[self._front]
        assert r is not None
        self._content[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._len -= 1
        return r

    def pop_back(self) -> T:
        """맨 뒤 값을 제거해서 반환한다. 시간복잡도는 O(1).

        외우는 구조:
        1. 비어 있으면 IndexError를 발생시킨다.
        2. rear는 마지막 원소 다음 빈 칸이므로, 먼저 rear를 한 칸 왼쪽으로 순환 이동한다.
        3. rear 위치의 값을 저장하고 그 칸을 비운다.
        4. len을 1 감소시키고 저장한 값을 반환한다.
        """
        if self._len == 0:
            raise IndexError()

        self._rear = (self._rear - 1 + self._capacity) % self._capacity
        r = self._content[self._rear]
        assert r is not None
        self._content[self._rear] = None
        self._len -= 1
        return r

    def front(self) -> T:
        """맨 앞 값을 제거하지 않고 반환한다. 시간복잡도는 O(1)."""
        return cast(T, self._content[self._front])

    def back(self) -> T:
        """맨 뒤 값을 제거하지 않고 반환한다. 시간복잡도는 O(1)."""
        return cast(T, self._content[(self._rear - 1 + self._capacity) % self._capacity])


if __name__ == "__main__":
    deque = CircularDeque[int](5)

    def show(step: str):
        print(f"\n[{step}]")
        print("logical:", deque)
        print("raw:", deque._content)
        print("front index:", deque._front)
        print("rear index:", deque._rear)
        print("len:", len(deque))
        print("is_empty:", deque.is_empty())

    show("initial")

    deque.push_back(20)
    show("push_back(20)")

    deque.push_front(10)
    show("push_front(10)")

    deque.push_back(30)
    show("push_back(30)")

    deque.push_front(0)
    show("push_front(0)")
