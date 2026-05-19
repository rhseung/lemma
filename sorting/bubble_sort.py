def bubble_sort(A: list[int]):
    n = len(A)

    for i in range(n):
        for j in range(n - i - 1):
            if A[j] > A[j + 1]:
                A[j], A[j + 1] = A[j + 1], A[j]


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    test_sort(bubble_sort, bench=True)
