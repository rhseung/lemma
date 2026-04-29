from __future__ import annotations

from dataclasses import dataclass, field

from core.graph.primitives.vertex import Vertex
from core.graph.primitives.weight import Weight


@dataclass
class FlowEdge[W: Weight]:
    """유량 그래프의 간선.

    각 간선은 생성 시 대응하는 역방향(residual) 간선과 쌍을 이룬다.
    알고리즘이 흐름을 보낼 때 ``flow`` 를 직접 수정하며,
    역방향 간선의 ``flow`` 는 반대 방향으로 자동 반영된다.

    Attributes:
        src: 출발 정점.
        dst: 도착 정점.
        capacity: 최대 허용 유량.
        flow: 현재 흐르는 유량 (초기값 0, ``__post_init__`` 에서 설정).
        reverse_edge: 역방향 간선 참조 (``__post_init__`` 에서 자동 설정).
        forward: 사용자가 추가한 정방향 간선이면 ``True`` (읽기 전용).
    """

    src: Vertex
    dst: Vertex
    capacity: W
    flow: W = field(init=False)
    reverse_edge: FlowEdge[W] | None = field(default=None, compare=False, repr=False)
    _forward: bool = field(default=True, compare=False, repr=False)

    def __post_init__(self) -> None:
        self.flow = type(self.capacity)(0)
        if self._forward:
            zero = type(self.capacity)(0)
            rev = FlowEdge(self.dst, self.src, zero, _forward=False)
            self.reverse_edge = rev
            rev.reverse_edge = self

    @property
    def forward(self) -> bool:
        """사용자가 추가한 정방향 간선이면 ``True``."""
        return self._forward

    @property
    def residual(self) -> W:
        """보낼 수 있는 잔여 용량. ``capacity - flow``."""
        return self.capacity - self.flow

    def __repr__(self) -> str:
        return f"FlowEdge({self.src} [{self.flow}/{self.capacity}] {self.dst})"

    def __str__(self) -> str:
        return f"{self.src} [{self.flow}/{self.capacity}] {self.dst}"
