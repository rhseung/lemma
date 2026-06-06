def merge_sort(A: list[int]):
    if len(A) <= 1:
        return A

    mid = len(A) // 2
    L = merge_sort(A[:mid])
    R = merge_sort(A[mid:])
    return merge(L, R)


def merge(L: list[int], R: list[int]):
    left, right = 0, 0
    res = []

    while left < len(L) and right < len(R):
        if L[left] <= R[right]:
            res.append(L[left])
            left += 1
        else:
            res.append(R[right])
            right += 1

    while left < len(L):
        res.append(L[left])
        left += 1

    while right < len(R):
        res.append(R[right])
        right += 1

    return res


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    print(test_sort(merge_sort, bench=True))
