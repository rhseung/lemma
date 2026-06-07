from map.hash_table.open_addressing.quadratic_probing_tombstone import HashTableQuadraticProbingTombstone
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
    print("=== Quadratic Probing + Tombstone ===")
    print("  f(i)=i*(i+1)/2  →  offsets: 0,1,3,6,10,... (triangular)")
    ht = HashTableQuadraticProbingTombstone[int, str](8)

    for k, v in [(1, "a"), (9, "b"), (17, "c")]:
        ht.insert(k, v)
    _show("insert 1, 9, 17", ht)

    ht.delete(9)
    _show("delete 9  →  TOMBSTONE", ht)

    print(f"   search(17) = {ht.search(17)!r}  ← tombstone 건너뜀")


if __name__ == "__main__":
    main()
