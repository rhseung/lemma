"""``@trace`` / ``@mst`` 데코레이터.

각 알고리즘 파일에서 자신의 이벤트 타입을 직접 선언한다.
공용 타입은 ``TraversalEvent`` / ``TraversalFn`` 만 여기서 제공.
"""

from scaffold.trace.events import TraversalEvent, TraversalFn
from scaffold.trace.mst import _MSTTraced, mst
from scaffold.trace.traversal import _Traced, trace

__all__ = [
    "TraversalEvent",
    "TraversalFn",
    "_MSTTraced",
    "_Traced",
    "mst",
    "trace",
]
