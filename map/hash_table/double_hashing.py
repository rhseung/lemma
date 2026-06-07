from map.hash_table.open_addressing import HashTableOpenAddressing


class HashTableDoubleHashing[K, V](HashTableOpenAddressing[K, V]):
    """Double hashing 방식 open addressing hash table ADT.

    probing 일반형:

        h(k, i) = (h(k) + f(i)) mod m

    double hashing에서는 보통 다음과 같이 둔다.

        f(i) = i * h2(k)

    장점:
    - primary clustering과 secondary clustering을 모두 완화한다.

    단점:
    - hash 함수가 2개 필요하다.
    - h2(k)와 table 크기가 서로소가 아니면 모든 slot을 방문하지 못할 수 있다.
    """

    def _probe(self, key: K, i: int) -> int:
        """double hashing에서 i번째 probe slot index를 반환한다."""
        raise NotImplementedError

    def _hash2(self, key: K) -> int:
        """두 번째 hash 값을 계산한다. 0이 아닌 step size여야 한다."""
        raise NotImplementedError
