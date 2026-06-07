from map.hash_table.open_addressing.double_hashing_tombstone import HashTableDoubleHashingTombstone
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
    print("=== Double Hashing + Tombstone ===")
    print("  h2(k)=1+(k%(m-1))  →  key마다 다른 step size")
    ht = HashTableDoubleHashingTombstone[int, str](8)

    ht.insert(1, "a")
    ht.insert(9, "b")
    _show("insert 1, 9", ht)

    ht.delete(1)
    _show("delete 1  →  TOMBSTONE", ht)

    print(f"   search(9) = {ht.search(9)!r}  ← tombstone 건너뜀")

    ht.insert(1, "A")
    _show("insert 1 (재삽입)  →  tombstone 자리", ht)


if __name__ == "__main__":
    main()
