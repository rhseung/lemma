from __future__ import annotations


class Node[T]:
    def __init__(self, value: T):
        self.value = value
        self.next: Node[T] | None = None

class SinglyLinkedList[T]:
    def __init__(self):
        self._head: Node[T] | None = None
        self._tail: Node[T] | None = None
        self._len = 0

    def __len__(self) -> int:
        return self._len

    def __str__(self) -> str:
        ret = []

        cur = self._head
        for _ in range(self._len):
            if cur is not None:
                ret.append(str(cur.value))
                cur = cur.next
            else:
                raise ValueError('len이 잘못 되었습니다.')

        return 'SinglyLinkedList(' + '->'.join(ret) + ')'

    def __repr__(self) -> str:
        return f"SinglyLinkedList(len={self._len}, content={self})"

    def is_empty(self) -> bool:
        return self._len == 0

    def front(self) -> T:
        if self._head is None:
            raise IndexError()

        return self._head.value

    def back(self) -> T:
        if self._tail is None:
            raise IndexError()

        return self._tail.value

    def clear(self):
        self._head = self._tail = None
        self._len = 0

    def push_front(self, value: T):
        """맨 앞에 값을 추가한다. 시간복잡도는 O(1).

        외우는 구조:
        1. new_node를 만든다.
        2. len 관련 로직을 조건문으로 나눈다.
           - len == 0: head와 tail을 둘 다 조정한다.
           - len >= 1: 앞쪽 포인터만 신경 써서 갱신한다.
        3. len을 1 증가시킨다.
        """
        new_node = Node(value)

        if self._len == 0:
            self._head = self._tail = new_node
        else:
            new_node.next = self._head
            self._head = new_node

        self._len += 1

    def push_back(self, value: T):
        """맨 뒤에 값을 추가한다. 시간복잡도는 O(1).

        외우는 구조:
        1. new_node를 만든다.
        2. len 관련 로직을 조건문으로 나눈다.
           - len == 0: head와 tail을 둘 다 조정한다.
           - len >= 1: 뒤쪽 포인터만 신경 써서 갱신한다.
        3. len을 1 증가시킨다.
        """
        new_node = Node(value)

        if self._len == 0:
            self._head = self._tail = new_node
        else:
            assert self._tail is not None
            self._tail.next = new_node
            self._tail = new_node

        self._len += 1

    def pop_front(self) -> T:
        """맨 앞 값을 제거해서 반환한다. 시간복잡도는 O(1).

        외우는 구조:
        1. 비어 있지 않다면 반환할 값을 미리 저장한다.
        2. len 관련 로직을 조건문으로 나눈다.
           - len == 0: IndexError를 발생시킨다.
           - len == 1: head와 tail을 둘 다 제거한다.
           - len >= 2: 앞쪽 포인터만 신경 써서 갱신한다.
        3. len을 1 감소시키고 저장한 값을 반환한다.
        """
        if self._len == 0:
            raise IndexError()

        assert self._head is not None
        r = self._head.value

        if self._len == 1:
            self._head = self._tail = None
        else:
            self._head = self._head.next

        self._len -= 1
        return r

    def pop_back(self) -> T:
        """맨 뒤 값을 제거해서 반환한다. 시간복잡도는 O(n).

        외우는 구조:
        1. 비어 있지 않다면 반환할 값을 미리 저장한다.
        2. len 관련 로직을 조건문으로 나눈다.
           - len == 0: IndexError를 발생시킨다.
           - len == 1: head와 tail을 둘 다 제거한다.
           - len >= 2: 뒤쪽 포인터만 신경 써서 갱신한다.
             singly linked list라 pop_back은 루프로 tail 직전 노드를 찾아야 한다.
        3. len을 1 감소시키고 저장한 값을 반환한다.
        """
        if self._len == 0:
            raise IndexError()

        assert self._tail is not None
        assert self._head is not None
        r = self._tail.value

        if self._len == 1:
            self._head = self._tail = None
        else:
            prev_tail = self._head
            while prev_tail.next != self._tail:
                prev_tail = prev_tail.next
                assert prev_tail is not None

            prev_tail.next = None
            self._tail = prev_tail

        self._len -= 1
        return r


if __name__ == "__main__":
    linked_list = SinglyLinkedList[int]()
    print(linked_list)

    linked_list.push_back(20)
    linked_list.push_front(10)
    linked_list.push_back(30)
    print("after pushes:", linked_list)

    print("pop_front:", linked_list.pop_front())
    print("after pop_front:", linked_list)

    print("pop_back:", linked_list.pop_back())
    print("after pop_back:", linked_list)

    linked_list = SinglyLinkedList[int]()
    for value in [10, 20, 30]:
        linked_list.push_back(value)

    print(linked_list.pop_back(), linked_list)
    print(linked_list.pop_back(), linked_list)
    print(linked_list.pop_back(), linked_list)
