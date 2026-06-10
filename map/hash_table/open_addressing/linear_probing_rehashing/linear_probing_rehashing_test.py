import random

import pytest

from map.hash_table.open_addressing.linear_probing_rehashing import HashTableLinearProbingRehashing

# capacity=8, h(k)=k%8
# home 1 충돌 집합: h(1)=h(9)=h(17)=h(25)=1
# home 2 충돌 집합: h(2)=h(10)=h(18)=2
# home 7 충돌 집합(wraparound): h(7)=h(15)=h(23)=7
K1, K2, K3 = 1, 9, 17


@pytest.fixture
def ht():
    return HashTableLinearProbingRehashing[int, str](8)


def slot_keys(ht) -> list[int | None]:
    """디버깅용: 각 slot에 어떤 key가 있는지(없으면 None) 나열한다."""
    return [s[0] if s is not None else None for s in ht._table]


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

    def test_delete_missing_on_collision_path_returns_false(self, ht):
        """cluster를 끝까지 훑었는데 없으면 False여야 한다."""
        ht.insert(K1, "a")
        ht.insert(K2, "b")
        assert ht.delete(K3) is False
        assert len(ht) == 2

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
        keys = list(range(0, 48, 8))  # 6개 → load factor 0.75로 resize 유발
        for k in keys:
            ht.insert(k, str(k))
        assert len(ht) == len(keys)
        assert ht._capacity > 8  # resize가 실제로 일어났는지
        for k in keys:
            assert ht.search(k) == str(k)


class TestRehashingDelete:
    """tombstone 없이 pull-forward로 cluster를 복구하는 핵심 동작."""

    def test_delete_head_repairs_same_home_cluster(self, ht):
        """cluster 맨 앞을 지워도 뒤쪽 동일 home key가 살아있어야 한다."""
        ht.insert(K1, "a")
        ht.insert(K2, "b")
        ht.insert(K3, "c")
        assert ht.delete(K1) is True
        assert ht.search(K2) == "b"
        assert ht.search(K3) == "c"
        assert len(ht) == 2

    def test_delete_middle_repairs_cluster(self, ht):
        """cluster 중간을 지워도 앞뒤 key가 모두 살아있어야 한다."""
        ht.insert(K1, "a")
        ht.insert(K2, "b")
        ht.insert(K3, "c")
        assert ht.delete(K2) is True
        assert ht.search(K1) == "a"
        assert ht.search(K3) == "c"
        assert len(ht) == 2

    def test_delete_pulls_cluster_forward_no_gap(self, ht):
        """삭제 후 cluster가 앞으로 당겨져 중간에 빈칸(None)이 없어야 한다.

        [_,1,9,17,_,...] 에서 1을 지우면 [_,9,17,_,...] 가 되어야 한다.
        naive하게 None만 두면 [_,_,9,17,_,...] 처럼 구멍이 남는다.
        """
        ht.insert(K1, "a")  # slot 1
        ht.insert(K2, "b")  # slot 2
        ht.insert(K3, "c")  # slot 3
        ht.delete(K1)
        assert slot_keys(ht) == [None, K2, K3, None, None, None, None, None]

    def test_delete_repairs_cross_home_cluster(self, ht):
        """가장 중요한 케이스: home이 다른 key가 한 cluster에 섞여 있을 때.

        layout: [_,1,9,2,10,_,_,_]  (9는 home1, 2/10은 home2)
        9를 지우면 home2 key들이 probe 경로를 잃지 않도록 당겨져야 한다.
        naive 삭제면 search(10)이 slot2의 None을 만나 KeyError가 난다.
        """
        ht.insert(1, "a")  # slot 1 (home 1)
        ht.insert(9, "b")  # slot 2 (home 1)
        ht.insert(2, "c")  # slot 3 (home 2)
        ht.insert(10, "d")  # slot 4 (home 2)
        assert slot_keys(ht) == [None, 1, 9, 2, 10, None, None, None]

        assert ht.delete(9) is True
        assert ht.search(1) == "a"
        assert ht.search(2) == "c"
        assert ht.search(10) == "d"  # ← rehashing이 없으면 여기서 깨진다
        with pytest.raises(KeyError):
            ht.search(9)
        assert len(ht) == 3
        assert slot_keys(ht) == [None, 1, 2, 10, None, None, None, None]

    def test_search_for_deleted_key_stops_at_none(self, ht):
        """단일 key 삭제 후 같은 home의 다른 key 탐색이 None에서 끊겨야 한다."""
        ht.insert(K1, "a")
        ht.delete(K1)
        with pytest.raises(KeyError):
            ht.search(K2)

    def test_delete_then_reinsert(self, ht):
        ht.insert(K1, "a")
        ht.insert(K2, "b")
        ht.delete(K1)
        assert ht.insert(K1, "A") is True
        assert len(ht) == 2
        assert ht.search(K1) == "A"
        assert ht.search(K2) == "b"

    def test_delete_all_one_by_one(self, ht):
        for k, v in [(K1, "a"), (K2, "b"), (K3, "c")]:
            ht.insert(k, v)
        for k in [K2, K1, K3]:  # 중간/앞/뒤 순서로 지워본다
            assert ht.delete(k) is True
        assert len(ht) == 0
        assert ht.is_empty()
        for k in (K1, K2, K3):
            with pytest.raises(KeyError):
                ht.search(k)


class TestWraparoundCluster:
    """배열 끝을 넘어 0으로 감기는 cluster도 복구되는지."""

    def test_wraparound_layout(self, ht):
        ht.insert(7, "a")  # slot 7
        ht.insert(15, "b")  # slot 0 (wrap)
        ht.insert(23, "c")  # slot 1
        assert slot_keys(ht) == [15, 23, None, None, None, None, None, 7]

    def test_delete_head_of_wraparound_cluster(self, ht):
        ht.insert(7, "a")
        ht.insert(15, "b")
        ht.insert(23, "c")
        assert ht.delete(7) is True
        assert ht.search(15) == "b"
        assert ht.search(23) == "c"
        assert len(ht) == 2
        assert slot_keys(ht) == [23, None, None, None, None, None, None, 15]

    def test_delete_middle_of_wraparound_cluster(self, ht):
        ht.insert(7, "a")
        ht.insert(15, "b")
        ht.insert(23, "c")
        assert ht.delete(15) is True
        assert ht.search(7) == "a"
        assert ht.search(23) == "c"
        assert len(ht) == 2


class TestDifferentialAgainstDict:
    """무작위 연산 시퀀스를 파이썬 dict와 대조하는 종합 정합성 테스트."""

    @pytest.mark.parametrize("seed", range(10))
    def test_random_ops_match_dict(self, seed):
        rng = random.Random(seed)
        ht = HashTableLinearProbingRehashing[int, str](8)
        ref: dict[int, str] = {}
        pool = list(range(40))  # 작은 key 풀 → 충돌·cluster가 자주 생김

        for _ in range(500):
            key = rng.choice(pool)
            op = rng.random()

            if op < 0.5:  # insert / update
                val = str(rng.randint(0, 1000))
                expected_new = key not in ref
                assert ht.insert(key, val) is expected_new
                ref[key] = val
            elif op < 0.8:  # delete
                expected = key in ref
                assert ht.delete(key) is expected
                ref.pop(key, None)
            else:  # search
                if key in ref:
                    assert ht.search(key) == ref[key]
                else:
                    with pytest.raises(KeyError):
                        ht.search(key)

            # 매 연산 후 전수 정합성 검증
            assert len(ht) == len(ref)
            for k in pool:
                if k in ref:
                    assert ht.get(k) == ref[k]
                else:
                    assert ht.get(k) is None
