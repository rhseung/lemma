from map.hash_table.linear_probing import HashTableLinearProbing


class HashTableRehashing[K, V](HashTableLinearProbing[K, V]):
    """Pull-forward rehashing delete를 쓰는 linear probing hash table ADT.

    삭제할 때 tombstone을 남기지 않고, 뒤쪽 cluster를 다시 배치해서 search 경로를 복구한다.

    시험 포인트:
    - delete가 핵심이다.
    - 단순히 한 칸을 None으로 비우면 뒤쪽 key의 search 경로가 끊긴다.
    - 삭제 후 cluster를 재삽입하거나 앞으로 당겨 search 불변식을 복구해야 한다.
    """

    def delete(self, key: K) -> bool:
        """key를 삭제하고 뒤쪽 cluster를 복구한다. 삭제했으면 True, 없으면 False."""
        raise NotImplementedError

    def _find_slot(self, key: K) -> int:
        """key가 있거나 들어갈 수 있는 slot을 linear probing으로 찾는다."""
        raise NotImplementedError

    def _rehash_cluster_after_delete(self, empty_idx: int):
        """삭제로 생긴 빈 칸 뒤 cluster를 다시 배치한다.

        Linear probing에서 pull-forward delete의 핵심 로직이다.
        """
        raise NotImplementedError
