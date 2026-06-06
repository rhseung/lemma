class DNode[T]:
    def __init__(self, value: T):
        self.value = value
        self.next: DNode[T] | None = None
        self.prev: DNode[T] | None = None

class DoublyLinkedList[T]:
    def __init__(self):
        self._head: DNode[T] | None = None
        self._tail: DNode[T] | None = None
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
                raise ValueError('len이 잘못되었습니다')

        return 'DoublyLinkedList(' + '<->'.join(ret) + ')'

    def __repr__(self) -> str:
        return f"DoublyLinkedList(len={self._len}, content={self})"

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
        new_node = DNode(value)

        if self._len == 0:
            self._head = self._tail = new_node
        else:
            assert self._head is not None
            new_node.next = self._head
            self._head.prev = new_node
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
        new_node = DNode(value)

        if self._len == 0:
            self._head = self._tail = new_node
        else:
            assert self._tail is not None
            new_node.prev = self._tail
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
        assert self._tail is not None
        r = self._head.value

        if self._len == 1:
            self._head = self._tail = None
        else:
            assert self._head.next is not None
            self._head.next.prev = None
            self._head = self._head.next

        self._len -= 1
        return r
    
    def pop_back(self) -> T:
        """맨 뒤 값을 제거해서 반환한다. 시간복잡도는 O(1).

        외우는 구조:
        1. 비어 있지 않다면 반환할 값을 미리 저장한다.
        2. len 관련 로직을 조건문으로 나눈다.
           - len == 0: IndexError를 발생시킨다.
           - len == 1: head와 tail을 둘 다 제거한다.
           - len >= 2: 뒤쪽 포인터만 신경 써서 갱신한다.
             doubly linked list는 tail.prev가 있으므로 루프 없이 바로 갱신할 수 있다.
        3. len을 1 감소시키고 저장한 값을 반환한다.
        """
        if self._len == 0:
            raise IndexError()
        
        assert self._head is not None
        assert self._tail is not None
        r = self._tail.value

        if self._len == 1:
            self._head = self._tail = None
        else:
            assert self._tail.prev is not None
            self._tail.prev.next = None
            self._tail = self._tail.prev

        self._len -= 1
        return r


if __name__ == "__main__":
    linked_list = DoublyLinkedList[int]()
    print(linked_list)

    linked_list.push_back(20)
    linked_list.push_front(10)
    linked_list.push_back(30)
    print("after pushes:", linked_list)

    print("pop_front:", linked_list.pop_front())
    print("after pop_front:", linked_list)

    print("pop_back:", linked_list.pop_back())
    print("after pop_back:", linked_list)
