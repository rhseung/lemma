import heapq


def heap_sort(A: list[int]):
    heapq.heapify(A)
    return [heapq.heappop(A) for _ in range(len(A))]
