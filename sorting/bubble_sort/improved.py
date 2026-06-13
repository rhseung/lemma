def bubble_sort_improved(A: list[int]):
    """
    time: best O(n), avg O(n^2)
    space: always O(1) -> in-place
    stable
    """

    n = len(A)
    for i in range(n):
        is_already_sorted = True
        for j in range(n - i - 1):
            if A[j] > A[j + 1]:
                A[j], A[j + 1] = A[j + 1], A[j]
                is_already_sorted = False
        if is_already_sorted:
            break


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    test_sort(bubble_sort_improved, bench=True)
