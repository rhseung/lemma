class HashTableOpenAddressing[K, V]:
    """Open addressing 방식 hash table의 공통 ADT.

    모든 key-value 쌍을 table 배열 안에 직접 저장한다.
    충돌이 나면 probing 전략으로 다음 후보 slot을 찾는다.

    probing의 일반형:

        h(k, i) = (h(k) + f(i)) mod m

    여기서 k는 key, i는 probe 횟수, m은 table 크기다.
    probing 방식은 f(i)를 어떻게 정하느냐에 따라 나뉜다.

    공통 책임:
    - hash index 계산
    - probing 전략을 이용한 slot 탐색
    - insert/search/get/resize

    구체적인 probing 전략과 delete 전략은 하위 클래스에서 고른다.
    """

    def __init__(self, capacity: int = 8):
        """빈 open addressing hash table을 만든다."""
        raise NotImplementedError

    def __len__(self) -> int:
        """저장된 key-value 쌍 개수를 반환한다."""
        raise NotImplementedError

    def __contains__(self, key: K) -> bool:
        """key가 table에 있으면 True를 반환한다."""
        raise NotImplementedError

    def __getitem__(self, key: K) -> V:
        """key에 대응하는 값을 반환한다. 없으면 KeyError."""
        raise NotImplementedError

    def __setitem__(self, key: K, value: V):
        """key에 value를 저장한다. 이미 있으면 값을 갱신한다."""
        raise NotImplementedError

    def __delitem__(self, key: K):
        """key를 삭제한다. 없으면 KeyError."""
        raise NotImplementedError

    def insert(self, key: K, value: V) -> bool:
        """key-value 쌍을 삽입한다. 새 key면 True, 갱신이면 False."""
        raise NotImplementedError

    def search(self, key: K) -> V:
        """key에 대응하는 값을 반환한다. 없으면 KeyError."""
        raise NotImplementedError

    def delete(self, key: K) -> bool:
        """key를 삭제한다. 삭제 전략은 하위 클래스가 정한다."""
        raise NotImplementedError

    def get(self, key: K, default: V | None = None) -> V | None:
        """key에 대응하는 값을 반환한다. 없으면 default를 반환한다."""
        raise NotImplementedError

    def is_empty(self) -> bool:
        """table이 비어 있으면 True를 반환한다."""
        raise NotImplementedError

    def _resize(self, new_capacity: int):
        """table 크기를 바꾸고 key-value 쌍을 다시 배치한다."""
        raise NotImplementedError

    def _hash(self, key: K) -> int:
        """key의 시작 slot을 계산한다."""
        raise NotImplementedError

    def _probe(self, key: K, i: int) -> int:
        """i번째 probe에서 확인할 slot index를 반환한다."""
        raise NotImplementedError
