from collections import deque


def bfs_iterative(graph: list[list[int]], start: int):
    """
    bfs는 eager, lazy 전부 가능하나 중복이 가능한 lazy보다 eager가 더 효율적이다.
    """

    queue = deque([start])
    visited = {start}

    while queue:
        u = queue.popleft()
        yield u

        for v in graph[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)
