def insertion_sort(A: list[int]):
    n = len(A)

    for i in range(1, n):
        j = i - 1
        key = A[i]

        while j >= 0 and A[j] > key:
            A[j + 1] = A[j]
            j -= 1

        A[j + 1] = key


if __name__ == "__main__":
    from core.sort_tester import test_sort
    print(test_sort(insertion_sort, bench=True))
