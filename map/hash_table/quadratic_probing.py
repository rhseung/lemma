from map.hash_table.open_addressing import HashTableOpenAddressing


class HashTableQuadraticProbing[K, V](HashTableOpenAddressing[K, V]):
    """Quadratic probing 방식 open addressing hash table ADT.

    probing 일반형:

        h(k, i) = (h(k) + f(i)) mod m

    quadratic probing에서는 보통 다음과 같이 둔다.

        f(i) = c1 * i + c2 * i^2

    장점:
    - linear probing의 primary clustering을 완화한다.

    단점:
    - 같은 시작 hash를 가진 key들은 같은 probe sequence를 따라가므로 secondary clustering이 생긴다.
    - table 크기와 c1, c2 선택에 따라 모든 slot을 방문하지 못할 수 있다.
    """

    def _probe(self, key: K, i: int) -> int:
        """quadratic probing에서 i번째 probe slot index를 반환한다."""
        raise NotImplementedError

    def _probe_offset(self, i: int) -> int:
        """f(i) = c1 * i + c2 * i^2 값을 반환한다."""
        raise NotImplementedError
