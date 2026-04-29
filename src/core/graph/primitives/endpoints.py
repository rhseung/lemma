from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from core.graph.primitives.vertex import Vertex


class HasEndpoints(Protocol):
    @property
    def src(self) -> Vertex: ...
    @property
    def dst(self) -> Vertex: ...
