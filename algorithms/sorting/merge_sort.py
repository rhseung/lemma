def merge_sort(A: list[int]):
    if len(A) <= 1:
        return A

    mid = len(A) // 2
    L = merge_sort(A[:mid])
    R = merge_sort(A[mid:])
    return merge(L, R)

def merge(L: list[int], R: list[int]):
    l, r = 0, 0
    res = []

    while l < len(L) and r < len(R):
        if L[l] <= R[r]:
            res.append(L[l])
            l += 1
        else:
            res.append(R[r])
            r += 1

    while l < len(L):
        res.append(L[l])
        l += 1

    while r < len(R):
        res.append(R[r])
        r += 1

    return res

if __name__ == "__main__":
    from core.sort_tester import test_sort
    print(test_sort(merge_sort, bench=True))
    
