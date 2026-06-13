"""sorting tester — 정렬 함수 비교 검증기.

pytest와 별개로, 구현한 정렬 함수가 잘 동작하는지 한 번 호출로 점검하는 용도.
여러 함수를 동시에 넘기면 나란히 비교한다 (Python 내장 포함).

지원 사항:
- **정확성 검증** — 엣지 케이스·랜덤 입력에서 최종 결과가 ``sorted()`` 와 일치하는지 본다.
- **interface 자동 감지** — 함수가 ``None`` 을 반환하든, 새 리스트를 반환하든,
  원본을 변형하면서 자기 자신을 반환하든 모두 처리한다 (mutate / return / mutate+return).
- **안정성 검증** — 동일 키의 상대 순서가 보존되는지 보고한다.
- **in-place 판정** — 입력을 제외한 peak 보조 메모리(tracemalloc)가 입력 크기에
  비례해 커지면 out-of-place, (거의) 일정하면 in-place 로 본다. 즉 *공간 복잡도*
  기준이며, 인터페이스상 원본을 바꾸더라도 O(n) 보조 메모리를 쓰면 out-of-place 다
  (예: timsort 의 ``list.sort``).
- **벤치** (``bench=True``) — 사이즈별 실행 시간(best/avg of 3) + peak 메모리(tracemalloc).

사용:
    from scaffold.sort_tester import compare_sort
    from sorting.bubble_sort import bubble_sort

    compare_sort(bubble_sort, sorted, bench=True)
"""

from __future__ import annotations

import gc
import random
import time
import tracemalloc
from collections.abc import Callable
from typing import Any

SortFn = Callable[[list[Any]], list[Any] | None]


# ─── helpers ────────────────────────────────────────────────────────────────


class _Tagged:
    __slots__ = ("key", "tag")

    def __init__(self, key: int, tag: int) -> None:
        self.key, self.tag = key, tag

    def __lt__(self, other: _Tagged) -> bool:
        return self.key < other.key

    def __le__(self, other: _Tagged) -> bool:
        return self.key <= other.key

    def __gt__(self, other: _Tagged) -> bool:
        return self.key > other.key

    def __ge__(self, other: _Tagged) -> bool:
        return self.key >= other.key

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _Tagged) and self.key == other.key

    def __hash__(self) -> int:
        return hash(self.key)

    def __repr__(self) -> str:
        return f"({self.key}#{self.tag})"


def _preview(xs: list[Any], k: int = 12) -> str:
    if len(xs) <= k:
        return repr(xs)
    head = ", ".join(repr(x) for x in xs[:k])
    return f"[{head}, …+{len(xs) - k}]"


def _fmt_bytes(b: int) -> str:
    if b < 1024:
        return f"{b} B"
    if b < 1024**2:
        return f"{b / 1024:.1f} KB"
    if b < 1024**3:
        return f"{b / 1024**2:.2f} MB"
    return f"{b / 1024**3:.2f} GB"


def _fmt_ms(ms: float) -> str:
    return f"{ms:.3f}ms"


def _classify(returned: bool, mutated: bool) -> str:
    """인터페이스 계약 (공간 복잡도와 무관 — in-place 판정은 ``_space_class`` 가 한다)."""
    if returned and mutated:
        return "mutate+return"
    if returned:
        return "return"
    if mutated:
        return "mutate"
    return "noop"


def _is_stably_sorted(actual: list[_Tagged], expected_keys: list[int]) -> bool:
    if [x.key for x in actual] != expected_keys:
        return False
    i = 0
    while i < len(actual):
        j = i
        while j < len(actual) and actual[j].key == actual[i].key:
            j += 1
        if [actual[t].tag for t in range(i, j)] != sorted(actual[t].tag for t in range(i, j)):
            return False
        i = j
    return True


def _run_one(fn: SortFn, data: list[Any]) -> tuple[list[Any] | None, bool, bool]:
    """(result_list, returned, mutated)"""
    buf = list(data)
    out = fn(buf)
    returned = out is not None
    mutated = buf != data
    actual = out if returned else buf
    return actual, returned, mutated


def _measure_peak(fn: SortFn, data: list[Any]) -> int:
    """입력을 제외하고 ``fn`` 이 추가로 점유하는 peak 보조 메모리(bytes).

    입력 복사본은 측정 시작 *전* 에 할당해 추적에서 제외하므로, 측정값은 정렬
    과정에서 새로 잡은 보조 메모리(임시 리스트·반환 리스트·재귀 프레임 등)만 담는다.
    """
    buf = list(data)  # 입력 — tracemalloc 시작 전에 할당해 측정에서 뺀다
    gc.collect()
    tracemalloc.start()
    out = fn(buf)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del out, buf
    return peak


def _space_class(peaks: list[tuple[int, int]]) -> tuple[str, bool]:
    """``(N, peak)`` 측정값으로 보조 공간이 입력에 비례하는지 판정한다.

    입력이 ``size_ratio`` 배 커질 때 보조 메모리도 그만큼(절반 이상) 커지면 O(n)
    → out-of-place. 일정하거나 로그 수준으로만 늘면 in-place. 원소당 보조 메모리
    하한(``per_elem``)은 측정 노이즈가 큰 미세 할당을 선형으로 오판하지 않게 거른다
    (제자리 정렬은 N=4000 에서 1B/elem 미만, O(n) 은 timsort 도 ≈4B/elem 이상).

    Returns
    -------
    (label, is_in_place)
    """
    (n_lo, p_lo), (n_hi, p_hi) = peaks[0], peaks[-1]
    per_elem = p_hi / n_hi
    size_ratio = n_hi / n_lo
    mem_ratio = p_hi / p_lo if p_lo > 0 else float("inf")
    if per_elem >= 2 and mem_ratio >= size_ratio * 0.5:
        return "O(n)", False
    return "O(1)~O(log n)", True


# ─── public API ─────────────────────────────────────────────────────────────


def compare_sort(
    *sort_fns: SortFn,
    bench: bool = False,
    sizes: tuple[int, ...] = (10, 100, 1000),
    space_sizes: tuple[int, ...] = (1000, 4000),
    seed: int = 42,
) -> bool:
    """여러 정렬 함수를 동시에 검증하고 비교한다.

    단일 함수도 허용 (``test_sort`` 와 동일 동작).

    Returns
    -------
    bool
        모든 함수의 모든 정확성 케이스 통과 시 ``True``.
    """
    if not sort_fns:
        raise ValueError("sort_fn 최소 1개 필요")

    names = [getattr(fn, "__name__", f"fn{i}") for i, fn in enumerate(sort_fns)]
    rng = random.Random(seed)

    cases: list[tuple[str, list[Any]]] = [
        ("empty", []),
        ("single", [42]),
        ("two — sorted", [1, 2]),
        ("two — reversed", [2, 1]),
        ("already sorted", list(range(10))),
        ("reverse sorted", list(range(10, 0, -1))),
        ("all equal", [7] * 8),
        ("with negatives", [-3, 5, -1, 0, 2, -8, 4]),
        ("with duplicates", [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]),
        ("floats", [3.14, 2.71, 1.41, 1.73, 0.0, -1.0]),
        ("strings", ["banana", "apple", "cherry", "apple", "date"]),
    ]
    cases.extend((f"random N={n}", [rng.randint(-10_000, 10_000) for _ in range(n)]) for n in sizes)

    col = 20
    label_w = max(len(label) for label, _ in cases) + 2
    name_w = max(len(n) for n in names) + 2

    title = " vs ".join(names)
    print(f"=== {title} ===\n")

    # ─── correctness ────────────────────────────────────────────────────────
    print("correctness:")
    header = "  " + "case".ljust(label_w) + "".join(n.ljust(col) for n in names)
    print(header)

    # track per-function state
    seen_returned = [False] * len(sort_fns)
    seen_mutated = [False] * len(sort_fns)
    fails: list[list[str]] = [[] for _ in sort_fns]

    for label, original in cases:
        expected = sorted(original)
        marks: list[str] = []
        for i, fn in enumerate(sort_fns):
            try:
                actual, returned, mutated = _run_one(fn, original)
            except Exception as e:
                marks.append(f"✗ {type(e).__name__}")
                fails[i].append(label)
                continue
            seen_returned[i] |= returned
            seen_mutated[i] |= mutated
            if actual != expected:
                marks.append("✗")
                fails[i].append(label)
            else:
                marks.append("✓")
        row = "  " + label.ljust(label_w) + "".join(m.ljust(col) for m in marks)
        print(row)

    # ─── stability ──────────────────────────────────────────────────────────
    print("\nstability:")
    stab_cases: list[tuple[str, list[tuple[int, int]]]] = [
        ("dup 4 keys", [(rng.randrange(4), i) for i in range(20)]),
        ("dup 2 keys", [(rng.randrange(2), i) for i in range(50)]),
        ("all equal", [(0, i) for i in range(15)]),
    ]
    print("  " + "case".ljust(label_w) + "".join(n.ljust(col) for n in names))
    for label, raw in stab_cases:
        tagged = [_Tagged(k, t) for k, t in raw]
        marks = []
        for i, fn in enumerate(sort_fns):
            try:
                actual, returned, mutated = _run_one(fn, tagged)
            except Exception as e:
                marks.append(f"✗ {type(e).__name__}")
                continue
            seen_returned[i] |= returned
            seen_mutated[i] |= mutated
            expected_keys = sorted(x.key for x in tagged)
            actual_tagged: list[_Tagged] = actual  # type: ignore[assignment]
            marks.append("stable" if _is_stably_sorted(actual_tagged, expected_keys) else "unstable")
        print("  " + label.ljust(label_w) + "".join(m.ljust(col) for m in marks))

    # ─── space (in-place via 공간 복잡도) ─────────────────────────────────────
    # 입력을 제외한 peak 보조 메모리를 N, 4N 두 크기에서 재 증가율로 in-place 판정.
    space_col = 13
    print("\nspace — auxiliary peak (in-place 판정):")
    print("  " + "fn".ljust(name_w) + "".join(f"N={n}".ljust(space_col) for n in space_sizes) + "verdict")
    space_labels: list[str] = []
    space_inplace: list[bool] = []
    for name, fn in zip(names, sort_fns, strict=True):
        peaks: list[tuple[int, int]] = []
        cells: list[str] = []
        err: str | None = None
        for n in space_sizes:
            data = [rng.randint(-10_000, 10_000) for _ in range(n)]
            try:
                peak = _measure_peak(fn, data)
            except Exception as e:
                err = type(e).__name__
                break
            peaks.append((n, peak))
            cells.append(_fmt_bytes(peak))
        if err is not None:
            space_labels.append("error")
            space_inplace.append(False)
            print("  " + name.ljust(name_w) + "".join(c.ljust(space_col) for c in cells) + f"✗ {err}")
            continue
        label, inplace = _space_class(peaks)
        space_labels.append(label)
        space_inplace.append(inplace)
        verdict = ("in-place" if inplace else "out-of-place") + f" ({label})"
        print("  " + name.ljust(name_w) + "".join(c.ljust(space_col) for c in cells) + verdict)

    # ─── bench ──────────────────────────────────────────────────────────────
    if bench:
        for n in sizes:
            print(f"\nbench N={n}:")
            print("  " + "fn".ljust(name_w) + "best       avg        mem")
            data = [rng.randint(-10_000, 10_000) for _ in range(n)]
            for name, fn in zip(names, sort_fns, strict=True):
                times: list[float] = []
                for _ in range(3):
                    buf = list(data)
                    t0 = time.perf_counter()
                    fn(buf)
                    times.append(time.perf_counter() - t0)
                best = min(times) * 1000
                avg = sum(times) / len(times) * 1000
                buf = list(data)
                tracemalloc.start()
                fn(buf)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                print(
                    "  "
                    + name.ljust(name_w)
                    + _fmt_ms(best).ljust(11)
                    + _fmt_ms(avg).ljust(11)
                    + _fmt_bytes(peak)
                )

    # ─── summary ────────────────────────────────────────────────────────────
    print()
    total = len(cases)
    styles = [_classify(seen_returned[i], seen_mutated[i]) for i in range(len(sort_fns))]
    all_passed = all(not f for f in fails)

    print("  interface: " + "   ".join(f"{n}={s}" for n, s in zip(names, styles, strict=True)))
    print(
        "  in-place:  "
        + "   ".join(
            f"{n}={'yes' if ip else 'no'} ({lbl})"
            for n, ip, lbl in zip(names, space_inplace, space_labels, strict=True)
        )
    )
    for name, fn_fails in zip(names, fails, strict=True):
        passed = total - len(fn_fails)
        status = f"{passed}/{total} ✓" if not fn_fails else f"{passed}/{total} ✗ failed: {', '.join(fn_fails)}"
        print(f"  {name}: {status}")

    return all_passed


def test_sort(
    sort_fn: SortFn,
    *,
    name: str | None = None,
    bench: bool = False,
    sizes: tuple[int, ...] = (10, 100, 1000),
    space_sizes: tuple[int, ...] = (1000, 4000),
    seed: int = 42,
) -> bool:
    """단일 함수 검증. ``compare_sort`` 의 단일 함수 편의 래퍼."""
    if name is not None:
        sort_fn = type(sort_fn)(sort_fn.__code__, sort_fn.__globals__, name)  # type: ignore[call-arg]
    return compare_sort(sort_fn, bench=bench, sizes=sizes, space_sizes=space_sizes, seed=seed)


# ─── self-check ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    def _sorted_return(a: list[Any]) -> list[Any]:
        return sorted(a)

    def _list_sort(a: list[Any]) -> None:
        a.sort()

    compare_sort(_sorted_return, _list_sort, bench=True)
