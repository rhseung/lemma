from map.hash_table.linear_probing import HashTableLinearProbing


class HashTableTombstone[K, V](HashTableLinearProbing[K, V]):
    """Tombstone delete를 쓰는 linear probing hash table ADT.

    삭제된 칸은 None으로 비우지 않고 tombstone 표시를 남긴다.

    시험 포인트:
    - search는 tombstone을 만나도 멈추면 안 된다.
    - insert는 tombstone 자리를 재사용할 수 있다.
    - tombstone이 많아지면 probe 길이가 길어져 resize/rehash가 필요하다.
    """

    def delete(self, key: K) -> bool:
        """key를 tombstone으로 표시한다. 삭제했으면 True, 없으면 False."""
        raise NotImplementedError

    def _resize(self, new_capacity: int):
        """table 크기를 바꾸고 tombstone 없이 살아 있는 key-value 쌍만 다시 배치한다."""
        raise NotImplementedError

    def _find_slot_for_search(self, key: K) -> int:
        """search/delete용 slot을 찾는다. tombstone을 만나도 계속 probe한다."""
        raise NotImplementedError

    def _find_slot_for_insert(self, key: K) -> int:
        """insert용 slot을 찾는다. 첫 tombstone 위치를 재사용 후보로 기억한다."""
        raise NotImplementedError
