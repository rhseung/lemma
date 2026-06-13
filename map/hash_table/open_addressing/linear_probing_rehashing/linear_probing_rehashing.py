from map.hash_table.open_addressing.slot import is_entry
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

    def _probe(self, key: K, i: int) -> int:
        return (self._hash(key) + i) % self._capacity

    def delete(self, key: K) -> bool:
        """key를 삭제하고 뒤따르는 cluster를 pull-forward로 복구한다."""
        probe_idx = self._find_slot(key)
        if probe_idx is None:
            return False

        self._table[probe_idx] = None
        self._len -= 1

        idx = (probe_idx + 1) % self._capacity
        while (kv := self._table[idx]) is not None:
            # rehashing은 tombstone을 안 남기므로 kv는 항상 entry (else 분기 도달 불가)
            if is_entry(kv):  # pragma: no branch
                self._table[idx] = None
                self._len -= 1
                self.insert(kv[0], kv[1])
            idx = (idx + 1) % self._capacity

        return True

    def _find_slot(self, key: K) -> int | None:
        """key가 있는 slot index를 반환한다. 없으면 None."""
        i = 0
        while i < self._capacity:
            probe_idx = self._probe(key, i)
            kv = self._table[probe_idx]

            if kv is None:
                return None
            if is_entry(kv) and kv[0] == key:
                return probe_idx
            i += 1
        return None


if __name__ == "__main__":

    def _show(label: str, ht) -> None:
        slots = []
        for s in ht._table:
            if s is None:
                slots.append("·")
            else:
                slots.append(f"{s[0]}:{s[1]}")
        print(f"  [{label}]")
        print("   table:   ", " | ".join(slots))
        print(f"   len={len(ht)}  capacity={ht._capacity}")

    print("=== Linear Probing + Rehashing Delete ===")
    print("  capacity=8, h(k)=k%8  →  h(1)=h(9)=h(17)=1 (모두 충돌)")
    ht = HashTableLinearProbingRehashing[int, str](8)

    ht.insert(1, "a")
    ht.insert(9, "b")
    ht.insert(17, "c")
    _show("insert 1, 9, 17", ht)

    ht.delete(1)
    _show("delete 1  →  pull-forward 복구", ht)

    print(f"   search(9)  = {ht.search(9)!r}")
    print(f"   search(17) = {ht.search(17)!r}")
