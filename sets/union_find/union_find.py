"""Union-Find (Disjoint Set Union).

path compression + union by rank.
"""


class UnionFind[T]:
    """Disjoint Set Union — path compression + union by rank.

    사용:
        uf = UnionFind(["a", "b", "c"])
        uf.union("a", "b")   # True — 병합 성공
        uf.union("a", "b")   # False — 이미 같은 집합
        uf.find("a") == uf.find("b")  # True
    """

    def __init__(self, elements: list[T]) -> None:
        self._parent: dict[T, T] = {e: e for e in elements}
        self._rank: dict[T, int] = dict.fromkeys(elements, 0)

    def find(self, x: T) -> T:
        """x 의 루트 반환. path compression 으로 트리 평탄화."""
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]
            x = self._parent[x]
        return x

    def union(self, x: T, y: T) -> bool:
        """x, y 가 속한 집합 병합.

        Returns
        -------
        bool
            ``True`` — 서로 다른 집합이었음 (병합 발생).
            ``False`` — 이미 같은 집합 (사이클).
        """
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx
        self._parent[ry] = rx
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1
        return True

    def connected(self, x: T, y: T) -> bool:
        """x, y 가 같은 집합에 속하는지 확인."""
        return self.find(x) == self.find(y)

    def __len__(self) -> int:
        """집합 수 반환."""
        return sum(1 for x in self._parent if self._parent[x] == x)
