def merge_sort(A: list[int]):
    _merge_sort(A, 0, len(A) - 1)


def _merge_sort(A: list[int], s: int, e: int):
    if s < e:
        m = (s + e) // 2
        _merge_sort(A, s, m)
        _merge_sort(A, m + 1, e)
        merge(A, s, m, e)


def merge(A: list[int], s: int, m: int, e: int):
    L = A[s : m + 1]
    R = A[m + 1 : e + 1]
    left, right = 0, 0
    n_L, n_R = len(L), len(R)
    i = s

    while left < n_L and right < n_R:
        if L[left] <= R[right]:
            A[i] = L[left]
            left += 1
        else:
            A[i] = R[right]
            right += 1
        i += 1

    while left < n_L:
        A[i] = L[left]
        i += 1
        left += 1

    while right < n_R:
        A[i] = R[right]
        i += 1
        right += 1


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    print(test_sort(merge_sort, bench=True))
