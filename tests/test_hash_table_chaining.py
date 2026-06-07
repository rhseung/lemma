import pytest

from map.hash_table.chaining import HashTableChaining


class TestHashTableChaining:
    def test_starts_empty(self):
        table = HashTableChaining[int, str](4)

        assert len(table) == 0
        assert table.is_empty()
        assert str(table) == "[]"

    def test_insert_adds_new_key_value_pair(self):
        table = HashTableChaining[int, str](4)

        assert table.insert(1, "one")

        assert len(table) == 1
        assert not table.is_empty()
        assert table.search(1) == "one"
        assert table[1] == "one"
        assert 1 in table

    def test_insert_updates_existing_key(self):
        table = HashTableChaining[int, str](4)

        assert table.insert(1, "one")
        assert not table.insert(1, "ONE")

        assert len(table) == 1
        assert table.search(1) == "ONE"

    def test_setitem_adds_and_updates_value(self):
        table = HashTableChaining[int, str](4)

        table[1] = "one"
        table[1] = "ONE"

        assert len(table) == 1
        assert table[1] == "ONE"

    def test_collision_keys_are_kept_separate(self):
        table = HashTableChaining[int, str](4)

        table.insert(1, "one")
        table.insert(5, "five")
        table.insert(9, "nine")

        assert len(table) == 3
        assert table.search(1) == "one"
        assert table.search(5) == "five"
        assert table.search(9) == "nine"

    def test_delete_removes_existing_key(self):
        table = HashTableChaining[int, str](4)
        table.insert(1, "one")
        table.insert(5, "five")

        assert table.delete(1)

        assert len(table) == 1
        assert 1 not in table
        assert table.search(5) == "five"
        with pytest.raises(KeyError):
            table.search(1)

    def test_delete_returns_false_for_missing_key(self):
        table = HashTableChaining[int, str](4)

        assert not table.delete(1)
        assert len(table) == 0

    def test_delitem_removes_key_or_raises_key_error(self):
        table = HashTableChaining[int, str](4)
        table[1] = "one"

        del table[1]

        assert len(table) == 0
        with pytest.raises(KeyError):
            del table[1]

    def test_search_and_getitem_raise_key_error_for_missing_key(self):
        table = HashTableChaining[int, str](4)

        with pytest.raises(KeyError):
            table.search(1)
        with pytest.raises(KeyError):
            table[1]

    def test_get_returns_default_for_missing_key(self):
        table = HashTableChaining[int, str](4)

        assert table.get(1) is None
        assert table.get(1, "missing") == "missing"

    def test_resize_preserves_values(self):
        table = HashTableChaining[int, str](2)

        for key in range(10):
            table.insert(key, str(key))

        assert len(table) == 10
        for key in range(10):
            assert table.search(key) == str(key)

    def test_str_and_repr_include_state(self):
        table = HashTableChaining[int, str](4)
        table.insert(1, "one")

        text = str(table)
        debug_text = repr(table)

        assert "(1, 'one')" in text
        assert "HashTableChaining" in debug_text
        assert "len=1" in debug_text
        assert "capacity=" in debug_text
