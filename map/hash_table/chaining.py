from typing import Protocol


class Key(Protocol):
    def __mod__(self, other: int, /) -> int: ...


class HashTableChaining[K: Key, V]:
    """Separate chaining 방식의 hash table ADT.

    각 bucket이 key-value 쌍들의 작은 리스트를 가진다.
    충돌이 나면 같은 bucket 안에 함께 저장한다.

    시험 포인트:
    - 평균적으로 insert/search/delete는 O(1)이다.
    - 최악의 경우 모든 key가 한 bucket에 몰리면 O(n)이다.
    - load factor가 커지면 resize해서 bucket 수를 늘린다.
    """

    def __init__(self, capacity: int = 8):
        """빈 hash table을 만든다."""
        self._capacity = capacity
        self._len = 0
        self._buckets: list[list[tuple[K, V]]] = [[] for _ in range(capacity)]

    def _h(self, key: K) -> int:
        return key % self._capacity

    def _load_factor(self) -> float:
        return self._len / self._capacity

    def __len__(self) -> int:
        """저장된 key-value 쌍 개수를 반환한다."""
        return self._len

    def __str__(self) -> str:
        """bucket 순서대로 key-value 쌍을 문자열로 표현한다."""
        items = [(k, v) for bucket in self._buckets for k, v in bucket]
        return str(items)

    def __repr__(self) -> str:
        """디버깅용 표현을 반환한다."""
        return (
            f"HashTableChaining("
            f"len={self._len}, capacity={self._capacity}, buckets={self._buckets})"
        )

    def _getindex(self, key: K) -> tuple[int, int | None]:
        hashed_key = self._h(key)

        for i, (k, _) in enumerate(self._buckets[hashed_key]):
            if k == key:
                return hashed_key, i

        return hashed_key, None

    def __contains__(self, key: K) -> bool:
        """key가 table에 있으면 True를 반환한다."""
        return self._getindex(key)[1] is not None

    def __getitem__(self, key: K) -> V:
        """key에 대응하는 값을 반환한다. 없으면 KeyError."""
        hashed_key, idx = self._getindex(key)

        if idx is None:
            raise KeyError()

        return self._buckets[hashed_key][idx][1]

    def __setitem__(self, key: K, value: V):
        """key에 value를 저장한다. 이미 있으면 값을 갱신한다."""
        hashed_key, idx = self._getindex(key)

        if idx is None:
            self._buckets[hashed_key].append((key, value))
            self._len += 1
            if self._load_factor() >= 0.7:
                self._resize(self._capacity << 1)
        else:
            self._buckets[hashed_key][idx] = (key, value)

    def __delitem__(self, key: K):
        """key를 삭제한다. 없으면 KeyError."""
        hashed_key, idx = self._getindex(key)

        if idx is None:
            raise KeyError()

        self._buckets[hashed_key].pop(idx)
        self._len -= 1

    def insert(self, key: K, value: V) -> bool:
        """key-value 쌍을 삽입한다. 새 key면 True, 갱신이면 False."""
        hashed_key, idx = self._getindex(key)

        if idx is None:
            self._buckets[hashed_key].append((key, value))
            self._len += 1
            if self._load_factor() >= 0.7:
                self._resize(self._capacity << 1)
            return True

        self._buckets[hashed_key][idx] = (key, value)
        return False

    def search(self, key: K) -> V:
        """key에 대응하는 값을 반환한다. 없으면 KeyError."""
        hashed_key, idx = self._getindex(key)

        if idx is None:
            raise KeyError()

        return self._buckets[hashed_key][idx][1]

    def delete(self, key: K) -> bool:
        """key를 삭제한다. 삭제했으면 True, 없으면 False."""
        hashed_key, idx = self._getindex(key)

        if idx is None:
            return False

        self._buckets[hashed_key].pop(idx)
        self._len -= 1
        return True

    def get(self, key: K, default: V | None = None) -> V | None:
        """key에 대응하는 값을 반환한다. 없으면 default를 반환한다."""
        hashed_key, idx = self._getindex(key)

        if idx is None:
            return default

        return self._buckets[hashed_key][idx][1]

    def is_empty(self) -> bool:
        """table이 비어 있으면 True를 반환한다."""
        return self._len == 0

    def _resize(self, new_capacity: int):
        """bucket 수를 바꾸고 모든 key-value 쌍을 다시 배치한다."""
        new_buckets: list[list[tuple[K, V]]] = [[] for _ in range(new_capacity)]
        old_capacity = self._capacity
        self._capacity = new_capacity  # hash 함수의 모듈러 갱신됨.

        for i in range(old_capacity):
            for k, v in self._buckets[i]:
                new_buckets[self._h(k)].append((k, v))

        self._buckets = new_buckets


if __name__ == "__main__":
    table = HashTableChaining[int, str](4)

    def show(step: str):
        print(f"\n[{step}]")
        print("items:", table)
        print("raw buckets:", table._buckets)
        print("len:", len(table))
        print("capacity:", table._capacity)
        print("load factor:", table._load_factor())

    show("initial")

    table.insert(1, "one")
    show('insert(1, "one")')

    table.insert(5, "five")
    show('insert(5, "five")  # collision with key 1 when capacity is 4')

    table[9] = "nine"
    show('table[9] = "nine"')

    print("search(5):", table.search(5))
    print("get(100, 'missing'):", table.get(100, "missing"))

    table.delete(5)
    show("delete(5)")
