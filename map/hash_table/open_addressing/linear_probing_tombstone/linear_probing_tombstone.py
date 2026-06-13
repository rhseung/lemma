from map.hash_table.key import ModularKey
from map.hash_table.open_addressing.open_addressing import HashTableOpenAddressing
from map.hash_table.open_addressing.slot import TOMBSTONE, is_entry


class HashTableLinearProbingTombstone[K: ModularKey, V](HashTableOpenAddressing[K, V]):
    """Linear probing + tombstone delete.

    probing: h(k, i) = (h(k) + i) mod m

    삭제할 때 None 대신 TOMBSTONE sentinel을 남긴다.
    - search: TOMBSTONE을 만나도 멈추지 않고 probe를 계속한다.
    - insert: 첫 번째 TOMBSTONE 자리를 재사용한다.
    - tombstone이 많아지면 resize 시 자동으로 정리된다.
    """

    def _probe(self, key: K, i: int) -> int:
        return (self._hash(key) + i) % self._capacity

    def delete(self, key: K) -> bool:
        i = 0
        while i < self._capacity:
            probe_idx = self._probe(key, i)
            kv = self._table[probe_idx]

            if kv is None:
                return False
            if is_entry(kv) and kv[0] == key:
                self._table[probe_idx] = TOMBSTONE
                self._len -= 1
                return True

            i += 1

        return False

    # FIXME: 주의! TOMBSTONE 뒤에 같은 key의 기존 entry가 있을 때 duplicate가 생긴다. 따라서, 첫 if 문에서 TOMBSTONE을 만나도, 바로 삽입하지 말고 2번째 key 동일 조건문을 만족하는지 기다린 후 없을 때 TOMBSTONE을 대체해야한다.
    # def insert(self, key: K, value: V) -> bool:
    #     """key-value 쌍을 삽입한다. 새 key면 True, 갱신이면 False."""
    #     i = 0
    #     while i < self._capacity:
    #         probe_idx = self._probe(key, i)
    #         kv = self._table[probe_idx]

    #         if kv is None or kv is TOMBSTONE:
    #             self._table[probe_idx] = (key, value)
    #             self._len += 1
    #             if self._load_factor() >= 0.66:
    #                 self._resize(self._capacity << 1)
    #             return True
    #         if is_entry(kv) and kv[0] == key:
    #             self._table[probe_idx] = (key, value)
    #             return False

    #         i += 1

    #     raise OverflowError("hash table에 삽입할 수 있는 slot이 없습니다.")

    def insert(self, key: K, value: V) -> bool:
        """key-value 쌍을 삽입한다. 새 key면 True, 갱신이면 False."""
        i = 0
        first_tombstone_idx = None
        while i < self._capacity:
            probe_idx = self._probe(key, i)
            kv = self._table[probe_idx]

            if kv is None and first_tombstone_idx is None:
                self._table[probe_idx] = (key, value)
                self._len += 1
                if self._load_factor() >= 0.66:
                    self._resize(self._capacity << 1)
                return True

            if kv is TOMBSTONE and first_tombstone_idx is None:
                first_tombstone_idx = probe_idx

            if is_entry(kv) and kv[0] == key:
                self._table[probe_idx] = (key, value)
                return False

            i += 1

        if first_tombstone_idx is not None:
            self._table[first_tombstone_idx] = (key, value)
            self._len += 1
            if self._load_factor() >= 0.66:
                self._resize(self._capacity << 1)
            return True

        raise OverflowError("hash table에 삽입할 수 있는 slot이 없습니다.")

    def search(self, key: K) -> V:
        """key에 대응하는 값을 반환한다. 없으면 KeyError."""
        i = 0
        while i < self._capacity:
            kv = self._table[self._probe(key, i)]

            if kv is None:
                raise KeyError()
            if is_entry(kv) and kv[0] == key:
                return kv[1]

            i += 1

        raise KeyError()


if __name__ == "__main__":

    def _show(label: str, ht) -> None:
        slots = []
        for s in ht._table:
            if s is None:
                slots.append("·")
            elif s is TOMBSTONE:
                slots.append("✗")
            elif is_entry(s):
                slots.append(f"{s[0]}:{s[1]}")
        print(f"  [{label}]")
        print("   table:   ", " | ".join(slots))
        print(f"   len={len(ht)}  capacity={ht._capacity}")

    print("=== Linear Probing + Tombstone ===")
    print("  capacity=8, h(k)=k%8  →  h(1)=h(9)=h(17)=1 (모두 충돌)")
    ht = HashTableLinearProbingTombstone[int, str](8)

    ht.insert(1, "a")
    ht.insert(9, "b")
    _show("insert 1, 9", ht)

    ht.delete(1)
    _show("delete 1  →  slot1 TOMBSTONE(✗)", ht)

    print(f"   search(9) = {ht.search(9)!r}  ← tombstone 건너뜀")

    ht.insert(17, "c")
    _show("insert 17  →  tombstone 재사용", ht)

    ht.delete(17)
    _show("delete 17  →  slot1 다시 TOMBSTONE", ht)

    result = ht.insert(9, "B")
    _show(f"insert(9,'B') → result={result} (False=갱신)", ht)
    assert result is False
    assert len(ht) == 1
    assert ht.search(9) == "B"
