from map.hash_table.open_addressing import HashTableOpenAddressing


class HashTableLinearProbing[K, V](HashTableOpenAddressing[K, V]):
    """Linear probing 방식 open addressing hash table의 공통 ADT.

    probing 일반형:

        h(k, i) = (h(k) + f(i)) mod m

    linear probing에서는 다음과 같이 둔다.

        f(i) = i

    충돌이 나면 한 칸씩 이동하며 다음 후보 slot을 찾는다.
    이 방식은 연속된 occupied slot들의 linear cluster를 만든다.

    장점:
    - 캐시 친화적이다. 연속 메모리를 순서대로 확인한다.

    단점:
    - primary clustering이 생긴다.

    delete 전략은 하위 클래스에서 고른다.
    Tombstone 방식과 pull-forward rehashing 방식은 같은 table에서 섞어 쓰지 않는다.
    """

    def _probe(self, key: K, i: int) -> int:
        """linear probing에서 i번째 probe slot index를 반환한다."""
        raise NotImplementedError
