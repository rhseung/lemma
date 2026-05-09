def selection_sort(A: list[int]):
    n = len(A)

    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if A[min_idx] > A[j]:
                min_idx = j
        A[i], A[min_idx] = A[min_idx], A[i]


if __name__ == "__main__":
    from core.sort_tester import test_sort

    print(test_sort(selection_sort, bench=True))
