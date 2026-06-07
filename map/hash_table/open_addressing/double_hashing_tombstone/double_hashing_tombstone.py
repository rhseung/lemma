from map.hash_table.key import ModularKey
from map.hash_table.open_addressing.open_addressing import HashTableOpenAddressing
from map.hash_table.open_addressing.slot import TOMBSTONE, is_entry


class HashTableDoubleHashingTombstone[K: ModularKey, V](HashTableOpenAddressing[K, V]):
    """Double hashing + tombstone delete.

    probing: h(k, i) = (h(k) + i * h2(k)) mod m

        h(k)  = k mod m           (첫 번째 hash, 시작 slot)
        h2(k) = 1 + (k mod (m-1)) (두 번째 hash, step size)

    h2(k)는 항상 1 이상이므로 step이 0이 되지 않는다.
    m과 m-1이 서로소이면 모든 slot을 방문할 수 있다 (m을 소수로 두는 것이 일반적).

    linear / quadratic probing 대비:
    - 같은 h(k)를 가진 key도 h2(k)가 다르면 서로 다른 probe sequence를 따른다.
    - primary clustering과 secondary clustering을 모두 완화한다.
    """

    def _hash2(self, key: K) -> int:
        return 1 + key % (self._capacity - 1)

    def _probe(self, key: K, i: int) -> int:
        return (self._hash(key) + i * self._hash2(key)) % self._capacity

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
