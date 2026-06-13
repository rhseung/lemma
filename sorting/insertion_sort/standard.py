def insertion_sort(A: list[int]):
    """
    time: best O(n), avg O(n^2)
    space: always O(1) -> in-place
    stable
    """

    n = len(A)
    for i in range(1, n):
        key = A[i]
        j = i - 1
        while j >= 0 and A[j] > key:
            A[j + 1] = A[j]
            j -= 1
        A[j + 1] = key


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    test_sort(insertion_sort, bench=True)
