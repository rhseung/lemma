def quick_sort(A: list[int]):
    """
    time: avg O(n log n), worst O(n^2)
    space: always O(n) -> not-in-place
    stable
    """

    if len(A) <= 1:
        return A

    pivot = A[0]
    left = [x for x in A[1:] if x < pivot]
    mid = [x for x in A[1:] if x == pivot]
    right = [x for x in A[1:] if x > pivot]

    return [*quick_sort(left), pivot, *mid, *quick_sort(right)]


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    test_sort(quick_sort, bench=True)
