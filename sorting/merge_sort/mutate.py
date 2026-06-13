def merge_sort(A: list[int]):
    _merge_sort(A, 0, len(A) - 1)


def _merge_sort(A: list[int], s: int, e: int):
    """
    time: always O(n log n)
    space: always O(n) -> not-in-place (메모리는 누적이 아니라 peak 값을 사용함을 기억하기!!)
    stable
    """

    if s < e:
        mid = (s + e) // 2
        _merge_sort(A, s, mid)
        _merge_sort(A, mid + 1, e)
        merge(A, s, mid, e)


def merge(A: list[int], s: int, m: int, e: int):
    L, R = A[s : m + 1], A[m + 1 : e + 1]
    i, l, r = s, 0, 0

    while l < len(L) and r < len(R):
        if L[l] <= R[r]:
            A[i] = L[l]
            l += 1
        else:
            A[i] = R[r]
            r += 1
        i += 1

    while l < len(L):
        A[i] = L[l]
        l += 1
        i += 1

    while r < len(R):
        A[i] = R[r]
        r += 1
        i += 1


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    test_sort(merge_sort, bench=True)
