def quick_sort(A: list[int]):
    _quick_sort(A, 0, len(A) - 1)


def _quick_sort(A: list[int], s: int, e: int):
    """
    time: avg O(n log n), worst O(n^2)
    space: always O(1) -> in-place BUT RECURSIVE STACK O(log n) 그래도 여전히  in-place
    unstable
    """

    if s < e:
        p = partition(A, s, e)
        _quick_sort(A, s, p - 1)
        _quick_sort(A, p + 1, e)


def partition(A: list[int], s: int, e: int) -> int:
    """
    맨 앞을 pivot의 값으로 해서, 기준으로 L에 더 작은 것이, R에 더 큰 것이 들어가도록 나눠 이 서브 배열들이 맞닿을 때까지 스왑을 하며 반복한다.
    """

    pivot = A[s]
    l, r = s + 1, e

    while l <= r:
        while l <= r and A[l] <= pivot:
            l += 1
        while l <= r and pivot <= A[r]:
            r -= 1

        # 아래 조건문을 만족한다는 것은 A[l] <= pivot과 pivot <= A[r]이 깨졌다는 것
        if l <= r:
            A[l], A[r] = A[r], A[l]

    # r < l인 경우, 파티션 완료 -> r의 위치와 s의 위치를 바꾸기
    A[s] = A[r]
    A[r] = pivot

    return r


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    test_sort(quick_sort, bench=True)
