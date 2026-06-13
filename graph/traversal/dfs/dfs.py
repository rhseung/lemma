def dfs_recursive(graph: list[list[int]], u: int, visited: set[int]):
    visited.add(u)
    yield u

    for v in graph[u]:
        if v not in visited:
            yield from dfs_recursive(graph, v, visited)


def dfs_iterative(graph: list[list[int]], start: int):
    """
    lazy로 해야함.
    """

    stack = [start]
    visited = set[int]()  # lazy: pop 시점에 마킹하므로 start 를 미리 넣으면 안 됨

    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        yield u

        for v in reversed(graph[u]):
            if v not in visited:
                stack.append(v)
