import pytest

from sequential.doubly_linked_list import DoublyLinkedList


def pop_front_n[T](linked_list: DoublyLinkedList[T], count: int) -> list[T]:
    return [linked_list.pop_front() for _ in range(count)]


class TestDoublyLinkedList:
    def test_starts_empty(self):
        linked_list = DoublyLinkedList[int]()

        assert len(linked_list) == 0
        assert linked_list.is_empty()
        assert str(linked_list) == "DoublyLinkedList()"

    def test_push_front_adds_values_to_front(self):
        linked_list = DoublyLinkedList[int]()

        linked_list.push_front(10)
        linked_list.push_front(20)
        linked_list.push_front(30)

        assert len(linked_list) == 3
        assert str(linked_list) == "DoublyLinkedList(30<->20<->10)"
        assert pop_front_n(linked_list, 3) == [30, 20, 10]

    def test_push_back_adds_values_to_back(self):
        linked_list = DoublyLinkedList[int]()

        linked_list.push_back(10)
        linked_list.push_back(20)
        linked_list.push_back(30)

        assert len(linked_list) == 3
        assert not linked_list.is_empty()
        assert linked_list.front() == 10
        assert linked_list.back() == 30
        assert str(linked_list) == "DoublyLinkedList(10<->20<->30)"
        assert pop_front_n(linked_list, 3) == [10, 20, 30]

    def test_front_and_back_raise_index_error_when_empty(self):
        linked_list = DoublyLinkedList[int]()

        with pytest.raises(IndexError):
            linked_list.front()
        with pytest.raises(IndexError):
            linked_list.back()

    def test_clear_removes_all_values(self):
        linked_list = DoublyLinkedList[int]()
        for value in [10, 20, 30]:
            linked_list.push_back(value)

        linked_list.clear()

        assert len(linked_list) == 0
        assert linked_list.is_empty()
        assert str(linked_list) == "DoublyLinkedList()"
        with pytest.raises(IndexError):
            linked_list.pop_front()

    def test_repr_includes_state(self):
        linked_list = DoublyLinkedList[int]()
        linked_list.push_back(10)

        text = repr(linked_list)

        assert "DoublyLinkedList" in text
        assert "len=1" in text
        assert "10" in text

    def test_push_front_and_push_back_can_be_mixed(self):
        linked_list = DoublyLinkedList[int]()

        linked_list.push_back(20)
        linked_list.push_front(10)
        linked_list.push_back(30)
        linked_list.push_front(0)

        assert len(linked_list) == 4
        assert str(linked_list) == "DoublyLinkedList(0<->10<->20<->30)"
        assert pop_front_n(linked_list, 4) == [0, 10, 20, 30]

    def test_pop_front_returns_and_removes_head(self):
        linked_list = DoublyLinkedList[str]()
        for value in ["a", "b", "c"]:
            linked_list.push_back(value)

        assert linked_list.pop_front() == "a"
        assert len(linked_list) == 2
        assert str(linked_list) == "DoublyLinkedList(b<->c)"

    def test_pop_back_returns_and_removes_tail(self):
        linked_list = DoublyLinkedList[str]()
        for value in ["a", "b", "c"]:
            linked_list.push_back(value)

        assert linked_list.pop_back() == "c"
        assert len(linked_list) == 2
        assert str(linked_list) == "DoublyLinkedList(a<->b)"

    def test_pop_front_until_empty(self):
        linked_list = DoublyLinkedList[int]()
        for value in [10, 20, 30]:
            linked_list.push_back(value)

        assert linked_list.pop_front() == 10
        assert linked_list.pop_front() == 20
        assert linked_list.pop_front() == 30

        assert len(linked_list) == 0
        assert str(linked_list) == "DoublyLinkedList()"

    def test_pop_back_until_empty(self):
        linked_list = DoublyLinkedList[int]()
        for value in [10, 20, 30]:
            linked_list.push_back(value)

        assert linked_list.pop_back() == 30
        assert linked_list.pop_back() == 20
        assert linked_list.pop_back() == 10

        assert len(linked_list) == 0
        assert str(linked_list) == "DoublyLinkedList()"

    def test_single_value_can_be_popped_from_front_then_reused(self):
        linked_list = DoublyLinkedList[int]()
        linked_list.push_back(10)

        assert linked_list.pop_front() == 10
        linked_list.push_back(20)

        assert len(linked_list) == 1
        assert str(linked_list) == "DoublyLinkedList(20)"
        assert linked_list.pop_front() == 20

    def test_single_value_can_be_popped_from_back_then_reused(self):
        linked_list = DoublyLinkedList[int]()
        linked_list.push_back(10)

        assert linked_list.pop_back() == 10
        linked_list.push_back(20)

        assert len(linked_list) == 1
        assert str(linked_list) == "DoublyLinkedList(20)"
        assert linked_list.pop_back() == 20

    @pytest.mark.parametrize("pop_method_name", ["pop_front", "pop_back"])
    def test_pop_from_empty_list_raises_index_error(self, pop_method_name):
        linked_list = DoublyLinkedList[int]()
        pop_method = getattr(linked_list, pop_method_name)

        with pytest.raises(IndexError):
            pop_method()

    def test_supports_none_when_type_allows_it(self):
        linked_list = DoublyLinkedList[int | None]()

        linked_list.push_back(10)
        linked_list.push_back(None)
        linked_list.push_back(20)

        assert len(linked_list) == 3
        assert pop_front_n(linked_list, 3) == [10, None, 20]

    def test_sequence_of_operations_matches_expected_order(self):
        linked_list = DoublyLinkedList[int]()

        linked_list.push_back(20)
        linked_list.push_front(10)
        linked_list.push_back(30)
        assert linked_list.pop_front() == 10
        linked_list.push_front(5)
        assert linked_list.pop_back() == 30
        linked_list.push_back(40)

        assert len(linked_list) == 3
        assert str(linked_list) == "DoublyLinkedList(5<->20<->40)"
        assert pop_front_n(linked_list, 3) == [5, 20, 40]

    def test_str_raises_when_len_is_corrupted(self):
        # __str__는 _len과 실제 노드 수가 어긋나면 방어적으로 ValueError를 낸다
        linked_list = DoublyLinkedList[int]()
        linked_list.push_back(10)
        linked_list._len = 5  # 노드는 1개뿐인데 len을 5로 손상시킴

        with pytest.raises(ValueError):
            str(linked_list)
