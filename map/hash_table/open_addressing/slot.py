from typing import Final, TypeGuard


class Tombstone:
    """삭제된 slot을 표시하는 sentinel 타입."""


TOMBSTONE: Final = Tombstone()

type Entry[K, V] = tuple[K, V]
type Slot[K, V] = Entry[K, V] | None
type TombstoneSlot[K, V] = Entry[K, V] | None | Tombstone


def is_entry[K, V](slot: TombstoneSlot[K, V]) -> TypeGuard[Entry[K, V]]:
    return isinstance(slot, tuple)
