from map.hash_table.open_addressing.linear_probing_tombstone import HashTableLinearProbingTombstone
from map.hash_table.open_addressing.slot import TOMBSTONE, is_entry


def _show(label: str, ht) -> None:
    slots = []
    for s in ht._table:
        if s is None:
            slots.append("·")
        elif s is TOMBSTONE:
            slots.append("✗")
        elif is_entry(s):
            slots.append(f"{s[0]}:{s[1]}")
    print(f"  [{label}]")
    print("   table:   ", " | ".join(slots))
    print(f"   len={len(ht)}  capacity={ht._capacity}")


def main() -> None:
    print("=== Linear Probing + Tombstone ===")
    print("  capacity=8, h(k)=k%8  →  h(1)=h(9)=h(17)=1 (모두 충돌)")
    ht = HashTableLinearProbingTombstone[int, str](8)

    ht.insert(1, "a")
    ht.insert(9, "b")
    _show("insert 1, 9", ht)

    ht.delete(1)
    _show("delete 1  →  slot1 TOMBSTONE(✗)", ht)

    print(f"   search(9) = {ht.search(9)!r}  ← tombstone 건너뜀")

    ht.insert(17, "c")
    _show("insert 17  →  tombstone 재사용", ht)

    ht.delete(17)
    _show("delete 17  →  slot1 다시 TOMBSTONE", ht)

    result = ht.insert(9, "B")
    _show(f"insert(9,'B') → result={result} (False=갱신)", ht)
    assert result is False
    assert len(ht) == 1
    assert ht.search(9) == "B"


if __name__ == "__main__":
    main()
