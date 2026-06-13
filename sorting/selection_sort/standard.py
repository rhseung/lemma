def selection_sort(A: list[int]):
    """
    time: always O(n^2)
    space: always O(1) -> in-place
    unstable
    """

    n = len(A)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if A[min_idx] > A[j]:
                min_idx = j

        A[min_idx], A[i] = A[i], A[min_idx]


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    test_sort(selection_sort, bench=True)
