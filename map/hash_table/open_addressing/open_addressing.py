from abc import ABC, abstractmethod

from map.hash_table.key import ModularKey
from map.hash_table.open_addressing.slot import TombstoneSlot, is_entry


class HashTableOpenAddressing[K: ModularKey, V](ABC):
    """Open addressing 방식 hash table의 공통 ADT.

    모든 key-value 쌍을 table 배열 안에 직접 저장한다.
    충돌이 나면 probing 전략으로 다음 후보 slot을 찾는다.

    probing의 일반형:

        h(k, i) = (h(k) + f(i)) mod m

    여기서 k는 key, i는 probe 횟수, m은 table 크기다.
    f(i)를 어떻게 정하느냐에 따라 linear / quadratic / double hashing으로 나뉜다.

    공통 책임: insert / search / get / _resize / _hash
    구체적인 probing 전략과 delete 전략은 하위 클래스가 구현한다.
    """

    def __init__(self, capacity: int = 8):
        self._capacity = capacity
        self._len = 0
        self._table: list[TombstoneSlot[K, V]] = [None] * capacity

    # ── abstract ──────────────────────────────────────────────────────────────

    @abstractmethod
    def _probe(self, key: K, i: int) -> int:
        """i번째 probe에서 확인할 slot index를 반환한다."""
        ...

    @abstractmethod
    def delete(self, key: K) -> bool:
        """key를 삭제한다. 삭제 전략은 하위 클래스가 정한다."""
        ...

    # ── dunder ────────────────────────────────────────────────────────────────

    def __len__(self) -> int:
        return self._len

    def __contains__(self, key: K) -> bool:
        return self.get(key) is not None

    def __getitem__(self, key: K) -> V:
        return self.search(key)

    def __setitem__(self, key: K, value: V):
        self.insert(key, value)

    def __delitem__(self, key: K):
        if not self.delete(key):
            raise KeyError()

    # ── public ────────────────────────────────────────────────────────────────

    def insert(self, key: K, value: V) -> bool:
        """key-value 쌍을 삽입한다. 새 key면 True, 갱신이면 False."""
        i = 0
        while i < self._capacity:
            probe_idx = self._probe(key, i)
            kv = self._table[probe_idx]

            if kv is None:
                self._table[probe_idx] = (key, value)
                self._len += 1
                if self._load_factor() >= 0.66:
                    self._resize(self._capacity << 1)
                return True
            if is_entry(kv) and kv[0] == key:
                self._table[probe_idx] = (key, value)
                return False

            i += 1

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

    def get(self, key: K, default: V | None = None) -> V | None:
        try:
            return self.search(key)
        except KeyError:
            return default

    def is_empty(self) -> bool:
        return self._len == 0

    # ── private ───────────────────────────────────────────────────────────────

    def _hash(self, key: K) -> int:
        """key의 시작 slot index를 계산한다."""
        return key % self._capacity

    def _resize(self, new_capacity: int):
        """table 크기를 바꾸고 key-value 쌍을 다시 배치한다."""
        new_ht = self.__class__(new_capacity)
        for kv in self._table:
            if is_entry(kv):
                new_ht.insert(kv[0], kv[1])
        self._table = new_ht._table
        self._capacity = new_ht._capacity
        self._len = new_ht._len

    def _load_factor(self) -> float:
        return self._len / self._capacity
