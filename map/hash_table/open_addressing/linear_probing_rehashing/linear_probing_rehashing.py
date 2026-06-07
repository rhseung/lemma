from map.hash_table.key import ModularKey
from map.hash_table.open_addressing.open_addressing import HashTableOpenAddressing


class HashTableLinearProbingRehashing[K: ModularKey, V](HashTableOpenAddressing[K, V]):
    """Linear probing + pull-forward rehashing delete.

    probing: h(k, i) = (h(k) + i) mod m

    삭제할 때 tombstone을 남기지 않는다.
    빈 slot 뒤에 이어지는 cluster를 처음부터 다시 insert해서
    search 경로의 불변식을 복구한다.

    시험 포인트:
    - 삭제 후 단순히 None으로 두면 같은 cluster 안의 뒤쪽 key가
      probe 도중 None을 만나 탐색이 조기에 끊긴다.
    - cluster 안의 각 entry를 다시 insert하면 앞쪽 빈 칸을 채워 경로가 복구된다.
    - linear probing에서만 cluster가 연속 구간이어서 이 방식이 안전하다.
    """

    # ── abstract ──────────────────────────────────────────────────────────────

    def _probe(self, key: K, i: int) -> int:
        return (self._hash(key) + i) % self._capacity

    def delete(self, key: K) -> bool:
        """key를 삭제하고 뒤따르는 cluster를 pull-forward로 복구한다."""
        idx = self._find_slot(key)
        if idx is None:
            return False

        self._table[idx] = None
        self._len -= 1
        self._rehash_cluster_after_delete(idx)
        return True

    # ── private ───────────────────────────────────────────────────────────────

    def _find_slot(self, key: K) -> int | None:
        """key가 있는 slot index를 반환한다. 없으면 None."""
        i = 0
        while i < self._capacity:
            probe_idx = self._probe(key, i)
            slot = self._table[probe_idx]
            if slot is None:
                return None
            if slot[0] == key:
                return probe_idx
            i += 1
        return None

    def _rehash_cluster_after_delete(self, empty_idx: int):
        """빈 slot 직후부터 None이 나올 때까지 각 entry를 다시 insert한다.

        각 entry를 꺼내 None으로 만든 뒤 insert를 호출하면,
        삭제로 생긴 빈 칸 포함 앞쪽 자리부터 다시 채워진다.
        """
        idx = (empty_idx + 1) % self._capacity
        while self._table[idx] is not None:
            entry = self._table[idx]
            self._table[idx] = None
            self._len -= 1
            self.insert(entry[0], entry[1])
            idx = (idx + 1) % self._capacity
