from map.hash_table.key import ModularKey
from map.hash_table.open_addressing.open_addressing import HashTableOpenAddressing
from map.hash_table.open_addressing.slot import TOMBSTONE, is_entry


class HashTableQuadraticProbingTombstone[K: ModularKey, V](HashTableOpenAddressing[K, V]):
    """Quadratic probing + tombstone delete.

    probing의 일반형:

        h(k, i) = (h(k) + c1*i + c2*i^2) mod m

    linear probing 대비:
    - primary clustering을 완화한다.
    - 같은 h(k)를 가진 key끼리는 같은 probe sequence를 따르므로 secondary clustering이 생긴다.
    """

    def _probe_offset(self, i: int) -> int:
        """i번째 probe의 offset을 반환한다. c1 = c2 = 1/2인 triangular probing.

        f(i) = i*(i+1)/2

        이를 선택한 이유:
        - c1 = c2 = 1/2이므로 f(i) = (i + i^2) / 2 = i*(i+1)/2, 즉 삼각수다.
        - m을 2의 거듭제곱으로 두면 i = 0, 1, ..., m-1 동안 f(i) mod m이 모두 다른 값을 가진다.
          따라서 빈 slot이 있으면 반드시 찾을 수 있다.
        - 정수 나눗셈만으로 계산되어 부동소수점 오차가 없다.
        """
        return i * (i + 1) // 2

    def _probe(self, key: K, i: int) -> int:
        return (self._hash(key) + self._probe_offset(i)) % self._capacity

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
