from __future__ import annotations

from dataclasses import dataclass

from core.graph.primitives.vertex import Vertex
from core.graph.primitives.weight import Weight
from core.graph.walk.trail import Trail
from core.graph.walk.walk import WeightedWalk


@dataclass
class Path(Trail):
    """정점 중복도 없는 워크.

    ``Trail`` 의 서브클래스로, 간선 중복이 없을 뿐만 아니라 정점도 중복되지 않는다.
    그래프 이론에서 '단순 경로(simple path)'에 해당한다.

    예시::

        a, b, c = Vertex("a"), Vertex("b"), Vertex("c")
        Path([a-b, b-c])          # OK
        Path([a-b, b-a, a-c])     # ValueError: 정점 a가 두 번 등장
    """

    def _validate(self) -> None:
        """간선 중복 및 정점 중복 여부를 검사한다. 중복이 있으면 ``ValueError`` 를 발생시킨다."""
        super()._validate()
        seen: set[Vertex] = set()
        for v in self.vertices:
            if v in seen:
                raise ValueError(f"Path contains repeated vertex: {v}")
            seen.add(v)


@dataclass
class WeightedPath[W: Weight](WeightedWalk[W]):
    """정점 중복이 없는 가중 워크 (단순 경로).

    ``WeightedWalk`` 의 서브클래스로, 정점 중복을 허용하지 않는다.
    Dijkstra, Bellman-Ford 등 최단 경로 알고리즘의 반환 타입.

    예시::

        a, b, c = Vertex("a"), Vertex("b"), Vertex("c")
        WeightedPath([a - 3 - b, b - 2 - c])    # OK
        WeightedPath([a - 1 - b, b - 2 - a])    # ValueError: 정점 a가 두 번 등장
    """

    def __post_init__(self) -> None:
        super().__post_init__()
        seen: set[Vertex] = set()
        for v in self.vertices:
            if v in seen:
                raise ValueError(f"WeightedPath contains repeated vertex: {v}")
            seen.add(v)
