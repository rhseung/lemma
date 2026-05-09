def merge_sort(A: list[int]):
    _merge_sort(A, 0, len(A) - 1)

def _merge_sort(A: list[int], s: int, e: int):
    if s < e:
        m = (s + e) // 2
        _merge_sort(A, s, m)
        _merge_sort(A, m + 1, e)
        merge(A, s, m, e)

def merge(A: list[int], s: int, m: int, e: int):
    L = A[s:m+1]
    R = A[m+1:e+1]
    l, r = 0, 0
    n_L, n_R = len(L), len(R)
    i = s

    while l < n_L and r < n_R:
        if L[l] <= R[r]:
            A[i] = L[l]
            l += 1
        else:
            A[i] = R[r]
            r += 1
        i += 1
    
    while l < n_L:
        A[i] = L[l]
        i += 1
        l += 1

    while r < n_R:
        A[i] = R[r]
        i += 1
        r += 1


if __name__ == "__main__":
    from core.sort_tester import test_sort
    print(test_sort(merge_sort, bench=True))

