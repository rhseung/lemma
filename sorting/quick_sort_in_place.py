def quick_sort(A: list[int]):
    _quick_sort(A, 0, len(A) - 1)


def _quick_sort(A: list[int], s: int, e: int):
    if s < e:
        p = partition(A, s, e)
        _quick_sort(A, s, p - 1)
        _quick_sort(A, p + 1, e)


def partition(A: list[int], s: int, e: int):
    pivot = A[s]
    left, right = s + 1, e

    while left <= right:
        while left <= right and A[left] <= pivot:
            left += 1
        while left <= right and pivot <= A[right]:
            right -= 1

        if left < right:
            A[left], A[right] = A[right], A[left]

    A[s], A[right] = A[right], A[s]
    return right


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    print(test_sort(quick_sort, bench=True))
