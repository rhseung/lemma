def merge_sort(A: list[int]) -> list[int]:
    """
    time: always O(n log n)
    space: always O(n) -> not-in-place (메모리는 누적이 아니라 peak 값을 사용함을 기억하기!!)
    stable
    """

    if len(A) <= 1:
        return A

    mid = len(A) // 2
    L = merge_sort(A[:mid])
    R = merge_sort(A[mid:])
    return merge(L, R)


def merge(L: list[int], R: list[int]) -> list[int]:
    res, l, r = [], 0, 0

    while l < len(L) and r < len(R):
        if L[l] <= R[r]:
            res.append(L[l])
            l += 1
        else:
            res.append(R[r])
            r += 1

    return res + L[l:] + R[r:]


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    test_sort(merge_sort, bench=True)
