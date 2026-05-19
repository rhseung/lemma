import functools
from collections.abc import Callable, Iterator
from typing import Any

from scaffold import WeightedGraph


class _MSTTraced[E: tuple]:
    """``@mst`` 로 wrap 된 MST 함수.

    - ``kruskal(g)``        — MST ``WeightedGraph`` 직접 반환
    - ``kruskal.events(g)`` — raw 이벤트 stream (``"add_edge"`` / ``"skip_edge"``)
    """

    def __init__(self, fn: Callable[..., Iterator[E]]) -> None:
        self._fn = fn
        functools.update_wrapper(self, fn)

    def __call__[W: (int, float)](self, *args: Any, **kwargs: Any) -> WeightedGraph[W]:
        result: WeightedGraph[W] = WeightedGraph()
        for type_, *ev_args in self._fn(*args, **kwargs):
            if type_ == "add_edge":
                u, v, w = ev_args[0], ev_args[1], ev_args[2]
                result.add_edge(u, v, w)
        return result

    def events(self, *args: Any, **kwargs: Any) -> Iterator[E]:
        """raw 이벤트 stream — 시각화·디버깅용."""
        return self._fn(*args, **kwargs)


def mst[E: tuple](fn: Callable[..., Iterator[E]]) -> _MSTTraced[E]:
    """MST generator 에 직접 반환 의미론 부여.

    호출 시 MST ``WeightedGraph`` 직접 반환, ``.events()`` 로 raw stream 접근.
    """
    return _MSTTraced(fn)


__all__ = ["_MSTTraced", "mst"]
