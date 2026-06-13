import heapq


def heap_sort(A: list[int]):
    """
    time: always O(n log n)
    space: always O(n) -> not-in-place
    unstable
    """

    heapq.heapify(A)
    return [heapq.heappop(A) for _ in range(len(A))]


if __name__ == "__main__":
    from scaffold.sort_tester import test_sort

    test_sort(heap_sort, bench=True)
