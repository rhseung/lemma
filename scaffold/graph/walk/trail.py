from __future__ import annotations

from dataclasses import dataclass

from scaffold.graph.walk.walk import Walk


@dataclass
class Trail(Walk):
    """간선 중복이 없는 워크.

    ``Walk`` 의 서브클래스로, 같은 간선을 두 번 이상 지나가지 않는다.
    정점은 중복될 수 있다. ``Path`` 의 부모 클래스다.

    예시::

        a, b, c = Vertex("a"), Vertex("b"), Vertex("c")
        Trail([a-b, b-c])          # OK
        Trail([a-b, b-a, a-c])     # OK (정점 a 중복 허용)
        Trail([a-b, b-c, b-a, a-c])  # ValueError: b-a 간선이 두 번 등장
    """

    def _validate(self) -> None:
        """간선 중복 여부를 검사한다. 중복 간선이 있으면 ``ValueError`` 를 발생시킨다."""
        seen: set[tuple] = set()
        for e in self.edges:
            key = (e.src, e.dst, e.kind)
            if key in seen:
                raise ValueError(f"Trail contains repeated edge: {e}")
            seen.add(key)
