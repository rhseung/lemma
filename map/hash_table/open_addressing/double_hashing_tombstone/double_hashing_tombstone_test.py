import pytest

from map.hash_table.open_addressing.double_hashing_tombstone import HashTableDoubleHashingTombstone

# capacity=8 기준 충돌 key 집합: h(1) = h(9) = h(17) = 1
K1, K2, K3 = 1, 9, 17


@pytest.fixture
def ht():
    return HashTableDoubleHashingTombstone[int, str](8)


class TestBasicOperations:
    def test_starts_empty(self, ht):
        assert len(ht) == 0
        assert ht.is_empty()

    def test_insert_new_key_returns_true(self, ht):
        assert ht.insert(K1, "a") is True
        assert len(ht) == 1
        assert ht.search(K1) == "a"

    def test_insert_existing_key_returns_false_and_updates(self, ht):
        ht.insert(K1, "a")
        assert ht.insert(K1, "A") is False
        assert len(ht) == 1
        assert ht.search(K1) == "A"

    def test_setitem_updates_not_duplicates(self, ht):
        ht[K1] = "a"
        ht[K1] = "A"
        assert ht[K1] == "A"
        assert len(ht) == 1

    def test_search_missing_raises_key_error(self, ht):
        with pytest.raises(KeyError):
            ht.search(K1)

    def test_get_missing_returns_default(self, ht):
        assert ht.get(K1) is None
        assert ht.get(K1, "x") == "x"

    def test_contains(self, ht):
        assert K1 not in ht
        ht.insert(K1, "a")
        assert K1 in ht

    def test_delete_existing_returns_true(self, ht):
        ht.insert(K1, "a")
        assert ht.delete(K1) is True
        assert len(ht) == 0
        assert K1 not in ht

    def test_delete_missing_returns_false(self, ht):
        assert ht.delete(K1) is False

    def test_delitem_missing_raises_key_error(self, ht):
        with pytest.raises(KeyError):
            del ht[K1]

    def test_collision_keys_stored_independently(self, ht):
        ht.insert(K1, "a")
        ht.insert(K2, "b")
        ht.insert(K3, "c")
        assert len(ht) == 3
        assert ht.search(K1) == "a"
        assert ht.search(K2) == "b"
        assert ht.search(K3) == "c"

    def test_resize_preserves_all_values(self, ht):
        keys = [0, 8, 16, 24, 32]
        for k in keys:
            ht.insert(k, str(k))
        assert len(ht) == 5
        for k in keys:
            assert ht.search(k) == str(k)


class TestTombstoneBehavior:
    def test_search_skips_tombstone(self, ht):
        ht.insert(K1, "a")
        ht.insert(K2, "b")
        ht.delete(K1)
        assert ht.search(K2) == "b"

    def test_search_stops_at_none_not_at_tombstone(self, ht):
        ht.insert(K1, "a")
        ht.delete(K1)
        with pytest.raises(KeyError):
            ht.search(K2)

    def test_delete_skips_tombstone(self, ht):
        ht.insert(K1, "a")
        ht.insert(K2, "b")
        ht.delete(K1)
        assert ht.delete(K2) is True
        assert len(ht) == 0
        with pytest.raises(KeyError):
            ht.search(K2)

    def test_insert_reuses_tombstone_slot(self, ht):
        ht.insert(K1, "a")
        ht.insert(K2, "b")
        ht.delete(K1)
        ht.insert(K3, "c")
        assert ht.search(K2) == "b"
        assert ht.search(K3) == "c"
        assert len(ht) == 2

    def test_insert_update_past_tombstone(self, ht):
        """tombstone 뒤에 기존 key가 있으면 그 자리에서 갱신해야 한다."""
        ht.insert(K1, "a")
        ht.insert(K2, "b")
        ht.delete(K1)
        result = ht.insert(K2, "B")
        assert result is False
        assert len(ht) == 1
        assert ht.search(K2) == "B"


class TestResize:
    def test_insert_past_load_factor_triggers_resize(self, ht):
        # load factor 0.66 * 8 = 5.28 → 6번째 삽입에서 resize
        for k in range(6):
            ht.insert(k, str(k))

        assert ht._capacity > 8
        assert len(ht) == 6
        for k in range(6):
            assert ht.search(k) == str(k)

    def test_reusing_tombstone_can_trigger_resize(self, ht):
        # slot 0~4를 채우고 0을 지워 slot0을 tombstone으로 만든 뒤,
        # home이 0인 key 8을 넣으면 tombstone(slot0)을 재사용하면서
        # len이 6이 되어(0.75) resize까지 일어난다.
        for k in range(5):
            ht.insert(k, str(k))
        ht.delete(0)
        ht.insert(5, "5")
        ht.insert(8, "8")

        assert ht._capacity > 8
        assert ht.search(8) == "8"
        for k in [1, 2, 3, 4, 5]:
            assert ht.search(k) == str(k)
        with pytest.raises(KeyError):
            ht.search(0)


class TestFullTable:
    """resize가 막혀 table이 가득 찬 극단 상황의 방어 경로."""

    @staticmethod
    def _fill(ht):
        ht._table = [(k, str(k)) for k in range(ht._capacity)]
        ht._len = ht._capacity

    def test_search_missing_raises_key_error(self, ht):
        self._fill(ht)
        with pytest.raises(KeyError):
            ht.search(99)

    def test_delete_missing_returns_false(self, ht):
        self._fill(ht)
        assert ht.delete(99) is False

    def test_insert_raises_overflow_error(self, ht):
        self._fill(ht)
        with pytest.raises(OverflowError):
            ht.insert(99, "x")
