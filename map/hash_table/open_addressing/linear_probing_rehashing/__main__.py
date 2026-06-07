from map.hash_table.open_addressing.linear_probing_rehashing import HashTableLinearProbingRehashing


def _show(label: str, ht) -> None:
    slots = []
    for s in ht._table:
        if s is None:
            slots.append("·")
        else:
            slots.append(f"{s[0]}:{s[1]}")
    print(f"  [{label}]")
    print("   table:   ", " | ".join(slots))
    print(f"   len={len(ht)}  capacity={ht._capacity}")


def main() -> None:
    print("=== Linear Probing + Rehashing Delete ===")
    print("  capacity=8, h(k)=k%8  →  h(1)=h(9)=h(17)=1 (모두 충돌)")
    ht = HashTableLinearProbingRehashing[int, str](8)

    ht.insert(1, "a")
    ht.insert(9, "b")
    ht.insert(17, "c")
    _show("insert 1, 9, 17", ht)

    ht.delete(1)
    _show("delete 1  →  pull-forward 복구", ht)

    print(f"   search(9)  = {ht.search(9)!r}")
    print(f"   search(17) = {ht.search(17)!r}")


if __name__ == "__main__":
    main()
