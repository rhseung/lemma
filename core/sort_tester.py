"""sorting tester — 정렬 함수 검증기.

pytest와 별개로, 구현한 정렬 함수가 잘 동작하는지 한 번 호출로 점검하는 용도.

지원 사항:
- **in-place / return 자동 감지** — 함수가 ``None`` 을 반환하든, 새 리스트를 반환하든,
  원본을 변형하면서 자기 자신을 반환하든 모두 처리한다.
- **원본 보존 여부 보고** — 호출 후 입력 리스트가 변형됐는지(`in-place`) /
  그대로인지(`return`) / 둘 다인지(`in-place+return`)를 케이스마다 표시한다.
- **안정성 검증** — 항상 실행되며, 동일 키의 상대 순서가 보존되는지 보고한다.
  안정성 실패는 정보성이라 정확성 통과 여부(반환값)에는 영향을 주지 않는다.
- **벤치** (`bench=True`) — 사이즈별 실행 시간(best/avg of 3) + peak 메모리(tracemalloc) 출력.

사용:
    from core.sort_tester import test_sort
    from algorithms.sorting.bubble_sort import bubble_sort

    test_sort(bubble_sort, bench=True)
"""

from __future__ import annotations

import random
import time
import tracemalloc
from collections.abc import Callable
from typing import Any

# 반환값이 None이면 in-place, 그 외엔 정렬된 리스트로 본다.
SortFn = Callable[[list[Any]], list[Any] | None]


# ─── helpers ────────────────────────────────────────────────────────────────


class _Tagged:
    """안정성 검증용 — ``key`` 는 비교 대상, ``tag`` 는 원래 인덱스."""

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


def _classify(returned: bool, mutated: bool) -> str:
    """누적된 반환/변형 여부로 함수의 호출 스타일을 분류."""
    if returned and mutated:
        return "in-place + return"
    if returned:
        return "return"
    if mutated:
        return "in-place"
    return "unknown"  # 단 한 번도 변형/반환을 안 함 — 모든 입력이 이미 정렬돼 있었거나 버그


def _is_stably_sorted(actual: list[_Tagged], expected_keys: list[int]) -> bool:
    """동일 키 그룹 내에서 ``tag`` 가 단조 증가하는지 확인."""
    if [x.key for x in actual] != expected_keys:
        return False
    i = 0
    while i < len(actual):
        j = i
        while j < len(actual) and actual[j].key == actual[i].key:
            j += 1
        tags = [actual[t].tag for t in range(i, j)]
        if tags != sorted(tags):
            return False
        i = j
    return True


# ─── public API ─────────────────────────────────────────────────────────────


def test_sort(
    sort_fn: SortFn,
    *,
    name: str | None = None,
    bench: bool = False,
    sizes: tuple[int, ...] = (10, 100, 1000),
    seed: int = 42,
) -> bool:
    """정렬 함수를 다양한 입력으로 실행하고 결과를 ``sorted()`` 와 비교한다.

    안정성 검증은 항상 실행되지만, 결과는 정보성으로만 출력된다 (반환값에 영향 없음).

    Returns
    -------
    bool
        모든 정확성 케이스 통과 시 ``True``.
    """
    name = name or getattr(sort_fn, "__name__", "sort")
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

    pad = max(len(label) for label, _ in cases)
    fails: list[str] = []
    seen_returned = False  # 한 번이라도 None 아닌 값을 반환한 적 있는가
    seen_mutated = False  # 한 번이라도 입력을 변형한 적 있는가

    print(f"=== {name} ===")
    for label, original in cases:
        expected = sorted(original)
        buf = list(original)
        try:
            out = sort_fn(buf)
        except Exception as e:
            print(f"  ✗ {label.ljust(pad)}  raised {type(e).__name__}: {e}")
            fails.append(label)
            continue

        returned = out is not None
        mutated = buf != original
        actual = out if returned else buf
        seen_returned |= returned
        seen_mutated |= mutated

        if actual != expected:
            extra = "  (no-op — 변형도 반환도 없음)" if not returned and not mutated else ""
            print(f"  ✗ {label.ljust(pad)}{extra}")
            print(f"      input    {_preview(original)}")
            print(f"      expected {_preview(expected)}")
            print(f"      got      {_preview(actual)}")
            fails.append(label)
            continue

        print(f"  ✓ {label.ljust(pad)}  n={len(original)}")

    # ─── 안정성 검증 (정보성 — fails에 누적하지 않음) ────────────────────
    print("\n  -- stability --")
    stab_cases: list[tuple[str, list[tuple[int, int]]]] = [
        ("dup 4 keys", [(rng.randrange(4), i) for i in range(20)]),
        ("dup 2 keys", [(rng.randrange(2), i) for i in range(50)]),
        ("all equal", [(0, i) for i in range(15)]),
    ]
    stable_results: list[bool] = []
    for label, raw in stab_cases:
        tagged = [_Tagged(k, t) for k, t in raw]
        buf = list(tagged)
        try:
            out = sort_fn(buf)
        except Exception as e:
            print(f"  ! {label.ljust(pad)}  raised {type(e).__name__}: {e}")
            stable_results.append(False)
            continue
        actual = buf if out is None else out
        seen_returned |= out is not None
        seen_mutated |= buf != tagged
        expected_keys = sorted(x.key for x in tagged)
        if _is_stably_sorted(actual, expected_keys):
            print(f"  ✓ {label.ljust(pad)}  stable")
            stable_results.append(True)
        else:
            print(f"  ✗ {label.ljust(pad)}  not stable")
            print(f"      got      {_preview(actual)}")
            stable_results.append(False)
    is_stable = all(stable_results)

    # ─── 벤치마크 ──────────────────────────────────────────────────────────
    if bench:
        print("\n  -- bench (time: best/avg of 3, mem: peak) --")
        for n in sizes:
            data = [rng.randint(-10_000, 10_000) for _ in range(n)]
            # 시간 측정 — tracemalloc 오버헤드 분리를 위해 메모리 측정과 별도 실행.
            times: list[float] = []
            for _ in range(3):
                # in-place 함수도 공정하게: 매 반복 새 사본을 정렬한다.
                buf = list(data)
                t0 = time.perf_counter()
                sort_fn(buf)
                times.append(time.perf_counter() - t0)
            best = min(times) * 1000
            avg = sum(times) / len(times) * 1000
            # 메모리 측정 — 결정적이라 1회로 충분.
            buf = list(data)
            tracemalloc.start()
            sort_fn(buf)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            print(
                f"  N={n:<5}  best={best:7.2f} ms   avg={avg:7.2f} ms   peak={_fmt_bytes(peak):>10}"
            )

    total = len(cases)
    passed = total - len(fails)
    style = _classify(seen_returned, seen_mutated)
    print()
    print(f"  style:  {style}")
    print(f"  stable: {'yes' if is_stable else 'no'}")
    if fails:
        print(f"  → {passed}/{total} passed, {len(fails)} failed: {', '.join(fails)}")
    else:
        print(f"  → all {total} passed")
    return not fails


# ─── self-check ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 빌트인 정렬은 모든 테스트(+ 안정성)를 통과해야 한다.
    # `sorted()` — 새 리스트 반환 (return 모드)
    def _sorted_return(a: list[Any]) -> list[Any]:
        return sorted(a)

    test_sort(_sorted_return, name="builtin sorted", bench=True)
    print()

    # `list.sort()` — None 반환 (in-place 모드)
    def _list_sort(a: list[Any]) -> None:
        a.sort()

    test_sort(_list_sort, name="builtin list.sort")
