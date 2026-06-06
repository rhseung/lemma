import pytest

from sequential.circular_deque import CircularDeque


class TestCircularDeque:
    def test_starts_empty(self):
        deque = CircularDeque[int](4)

        assert len(deque) == 0
        assert deque.is_empty()
        assert deque.as_list() == []
        assert str(deque) == "[]"

    def test_push_back_adds_values_to_back(self):
        deque = CircularDeque[int](4)

        deque.push_back(10)
        deque.push_back(20)
        deque.push_back(30)

        assert len(deque) == 3
        assert not deque.is_empty()
        assert deque.front() == 10
        assert deque.back() == 30
        assert deque.as_list() == [10, 20, 30]
        assert str(deque) == "[10, 20, 30]"

    def test_push_front_adds_values_to_front(self):
        deque = CircularDeque[int](4)

        deque.push_front(10)
        deque.push_front(20)
        deque.push_front(30)

        assert len(deque) == 3
        assert not deque.is_empty()
        assert deque.as_list() == [30, 20, 10]

    def test_push_front_and_push_back_can_be_mixed(self):
        deque = CircularDeque[int](6)

        deque.push_back(20)
        deque.push_front(10)
        deque.push_back(30)
        deque.push_front(0)

        assert len(deque) == 4
        assert deque.as_list() == [0, 10, 20, 30]

    def test_wraps_around_when_pushing_front(self):
        deque = CircularDeque[int](4)

        deque.push_front(30)
        deque.push_front(20)
        deque.push_front(10)

        assert deque.as_list() == [10, 20, 30]

    def test_wraps_around_when_pushing_back_after_front(self):
        deque = CircularDeque[int](4)

        deque.push_front(20)
        deque.push_back(30)
        deque.push_back(40)

        assert deque.as_list() == [20, 30, 40]

    def test_push_rejects_when_full(self):
        deque = CircularDeque[int](2)
        deque.push_back(10)
        deque.push_back(20)

        with pytest.raises(IndexError):
            deque.push_back(30)
        with pytest.raises(IndexError):
            deque.push_front(0)

        assert len(deque) == 2
        assert deque.as_list() == [10, 20]

    def test_supports_none_when_type_allows_it(self):
        deque = CircularDeque[int | None](4)

        deque.push_back(10)
        deque.push_back(None)
        deque.push_back(20)

        assert deque.as_list() == [10, None, 20]

    def test_pop_front_returns_and_removes_front_value(self):
        deque = CircularDeque[int](4)
        for value in [10, 20, 30]:
            deque.push_back(value)

        assert deque.pop_front() == 10

        assert len(deque) == 2
        assert deque.front() == 20
        assert deque.back() == 30
        assert deque.as_list() == [20, 30]

    def test_pop_back_returns_and_removes_back_value(self):
        deque = CircularDeque[int](4)
        for value in [10, 20, 30]:
            deque.push_back(value)

        assert deque.pop_back() == 30

        assert len(deque) == 2
        assert deque.front() == 10
        assert deque.back() == 20
        assert deque.as_list() == [10, 20]

    def test_pop_front_until_empty(self):
        deque = CircularDeque[int](4)
        for value in [10, 20, 30]:
            deque.push_back(value)

        assert deque.pop_front() == 10
        assert deque.pop_front() == 20
        assert deque.pop_front() == 30

        assert len(deque) == 0
        assert deque.is_empty()
        assert deque.as_list() == []

    def test_pop_back_until_empty(self):
        deque = CircularDeque[int](4)
        for value in [10, 20, 30]:
            deque.push_back(value)

        assert deque.pop_back() == 30
        assert deque.pop_back() == 20
        assert deque.pop_back() == 10

        assert len(deque) == 0
        assert deque.is_empty()
        assert deque.as_list() == []

    @pytest.mark.parametrize("method_name", ["pop_front", "pop_back"])
    def test_pop_from_empty_deque_raises_index_error(self, method_name):
        deque = CircularDeque[int](4)
        method = getattr(deque, method_name)

        with pytest.raises(IndexError):
            method()
