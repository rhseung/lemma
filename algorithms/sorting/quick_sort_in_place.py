def quick_sort(A: list[int]):
    _quick_sort(A, 0, len(A) - 1)

def _quick_sort(A: list[int], s: int, e: int):
    if s < e:
        p = partition(A, s, e)
        _quick_sort(A, s, p - 1)
        _quick_sort(A, p + 1, e)

def partition(A: list[int], s: int, e: int):
    pivot = A[s]
    l, r = s + 1, e

    while l <= r:
        while l <= r and A[l] <= pivot:
            l += 1
        while l <= r and pivot <= A[r]:
            r -= 1

        if l < r:
            A[l], A[r] = A[r], A[l]

    A[s], A[r] = A[r], A[s]
    return r


if __name__ == "__main__":
    from core.sort_tester import test_sort
    print(test_sort(quick_sort, bench=True))
