from collections.abc import Callable, Iterator

type TraversalEvent = tuple
type TraversalFn[E: tuple] = Callable[..., Iterator[E]]

__all__ = ["TraversalEvent", "TraversalFn"]
