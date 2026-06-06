import pytest

from sequential.dynamic_array import DynamicArray


def values[T](array: DynamicArray[T]) -> list[T]:
    return [array[i] for i in range(len(array))]


class TestDynamicArray:
    def test_starts_empty(self):
        array = DynamicArray[int](4)

        assert len(array) == 0
        assert array.is_empty()

    def test_append_adds_values_in_order(self):
        array = DynamicArray[int](2)

        assert array.append(10)
        assert array.append(20)

        assert len(array) == 2
        assert not array.is_empty()
        assert array.front() == 10
        assert array.back() == 20
        assert values(array) == [10, 20]

    def test_front_and_back_raise_index_error_when_empty(self):
        array = DynamicArray[int](2)

        with pytest.raises(IndexError):
            array.front()
        with pytest.raises(IndexError):
            array.back()

    def test_clear_removes_all_values(self):
        array = DynamicArray[int](4)
        for value in [10, 20, 30]:
            array.append(value)

        array.clear()

        assert len(array) == 0
        assert array.is_empty()
        assert values(array) == []
        with pytest.raises(IndexError):
            array.front()

    def test_append_extends_capacity_when_full(self):
        array = DynamicArray[int](2)

        assert array.append(10)
        assert array.append(20)
        assert array.append(30)

        assert len(array) == 3
        assert values(array) == [10, 20, 30]

    def test_append_many_values_across_multiple_extensions(self):
        array = DynamicArray[int](1)

        for value in range(20):
            assert array.append(value)

        assert len(array) == 20
        assert values(array) == list(range(20))

    def test_append_accepts_none_as_value_when_type_allows_it(self):
        array = DynamicArray[int | None](2)

        assert array.append(10)
        assert array.append(None)
        assert array.append(20)

        assert values(array) == [10, None, 20]

    def test_insert_at_front_middle_and_end(self):
        array = DynamicArray[str](2)

        assert array.append("b")
        assert array.insert(0, "a")
        assert array.insert(2, "d")
        assert array.insert(2, "c")

        assert len(array) == 4
        assert [array[i] for i in range(len(array))] == ["a", "b", "c", "d"]

    def test_insert_at_len_behaves_like_append(self):
        array = DynamicArray[int](2)
        array.append(10)

        assert array.insert(len(array), 20)

        assert values(array) == [10, 20]

    def test_insert_into_full_array_extends_and_shifts_values(self):
        array = DynamicArray[int](2)
        array.append(10)
        array.append(30)

        assert array.insert(1, 20)

        assert len(array) == 3
        assert values(array) == [10, 20, 30]

    def test_insert_rejects_out_of_range_index(self):
        array = DynamicArray[int](2)

        assert not array.insert(-1, 10)
        assert not array.insert(1, 10)
        assert len(array) == 0

    def test_insert_rejects_index_greater_than_len_without_changing_array(self):
        array = DynamicArray[int](4)
        array.append(10)
        array.append(20)

        assert not array.insert(3, 30)

        assert len(array) == 2
        assert values(array) == [10, 20]

    def test_getitem_returns_value_by_index(self):
        array = DynamicArray[int](2)
        array.append(10)
        array.append(20)

        assert array[0] == 10
        assert array[1] == 20

    def test_getitem_reflects_insert_and_pop_mutations(self):
        array = DynamicArray[int](6)
        for value in [10, 30, 40]:
            array.append(value)
        array.insert(1, 20)
        array.pop(2)

        assert array[0] == 10
        assert array[1] == 20
        assert array[2] == 40

    @pytest.mark.parametrize("idx", [-1, 0, 1])
    def test_getitem_raises_index_error_for_out_of_range_index(self, idx):
        array = DynamicArray[int](2)

        with pytest.raises(IndexError):
            array[idx]

    @pytest.mark.parametrize(
        ("idx", "expected"),
        [
            (0, [20, 30, 40]),
            (1, [10, 30, 40]),
            (3, [10, 20, 30]),
        ],
    )
    def test_pop_removes_value_at_index(self, idx, expected):
        array = DynamicArray[int](4)
        for value in [10, 20, 30, 40]:
            array.append(value)

        assert array.pop(idx)

        assert len(array) == 3
        assert values(array) == expected

    def test_pop_until_empty(self):
        array = DynamicArray[int](8)
        for value in [10, 20, 30]:
            array.append(value)

        assert array.pop(2)
        assert array.pop(1)
        assert array.pop(0)

        assert len(array) == 0
        assert values(array) == []

    def test_pop_rejects_out_of_range_index(self):
        array = DynamicArray[int](2)
        array.append(10)

        assert not array.pop(-1)
        assert not array.pop(1)
        assert values(array) == [10]

    def test_remove_deletes_first_matching_value(self):
        array = DynamicArray[int](4)
        for value in [10, 20, 10, 30]:
            array.append(value)

        assert array.remove(10)

        assert len(array) == 3
        assert values(array) == [20, 10, 30]

    def test_remove_deletes_middle_matching_value(self):
        array = DynamicArray[int](8)
        for value in [10, 20, 30, 40]:
            array.append(value)

        assert array.remove(30)

        assert len(array) == 3
        assert values(array) == [10, 20, 40]

    def test_remove_deletes_last_matching_value(self):
        array = DynamicArray[int](8)
        for value in [10, 20, 30]:
            array.append(value)

        assert array.remove(30)

        assert len(array) == 2
        assert values(array) == [10, 20]

    def test_remove_returns_false_when_value_is_missing(self):
        array = DynamicArray[int](2)
        array.append(10)

        assert not array.remove(20)
        assert values(array) == [10]

    def test_sequence_of_operations_matches_python_list(self):
        array = DynamicArray[int](2)
        expected: list[int] = []

        for value in [10, 20, 30, 40]:
            assert array.append(value)
            expected.append(value)

        assert array.insert(2, 25)
        expected.insert(2, 25)
        assert array.pop(0)
        expected.pop(0)
        assert array.remove(30)
        expected.remove(30)
        assert array.insert(len(array), 50)
        expected.insert(len(expected), 50)

        assert len(array) == len(expected)
        assert values(array) == expected

    def test_str_and_repr_include_state(self):
        array = DynamicArray[int](2)
        array.append(10)

        text = str(array)
        debug_text = repr(array)

        assert "10" in text
        assert "DynamicArray" in debug_text
        assert "len=1" in debug_text
        assert "capacity=2" in debug_text
        assert "10" in debug_text

    def test_str_empty_array_includes_len_and_content(self):
        array = DynamicArray[int](2)

        text = str(array)
        debug_text = repr(array)

        assert text == "[None, None]"
        assert "DynamicArray" in debug_text
        assert "len=0" in debug_text
        assert "capacity=2" in debug_text
        assert "content=" in debug_text
