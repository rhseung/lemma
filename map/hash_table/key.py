from typing import Protocol


class ModularKey(Protocol):
    """key % capacity 연산을 지원하는 hash table key."""

    def __mod__(self, other: int, /) -> int: ...
