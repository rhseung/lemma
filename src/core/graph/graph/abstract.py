from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Literal, Self

from core.graph.primitives.edge_kind import EdgeKind
from core.graph.primitives.endpoints import HasEndpoints

if TYPE_CHECKING:
    from core.graph.primitives.edge import Edge, WeightedEdge
    from core.graph.primitives.vertex import Vertex
    from core.graph.walk import Walk, WeightedWalk


class _AbstractGraph[E: HasEndpoints](ABC):
    """모든 그래프 구현체의 공통 인터페이스를 정의하는 추상 기반 클래스.

    ``UnweightedGraph`` 와 ``WeightedGraph`` 가 이 클래스를 상속받는다.
    직접 인스턴스화하지 않고, ``Graph`` 팩토리를 통해 생성한다.

    Attributes:
        kind: 그래프를 구성하는 간선들의 방향성 종류.
    """

    kind: EdgeKind

    @abstractmethod
    def add_vertex(self, v: Vertex) -> None:
        """정점을 그래프에 추가한다. 이미 존재하면 아무것도 하지 않는다."""
        ...

    @abstractmethod
    def has_vertex(self, v: Vertex) -> bool:
        """정점이 그래프에 존재하면 ``True`` 를 반환한다."""
        ...

    @abstractmethod
    def get_vertex(self, label: str) -> Vertex:
        """레이블로 정점 객체를 반환한다. 없으면 ``KeyError``."""
        ...

    @abstractmethod
    def get_edge(self, u: Vertex, v: Vertex) -> E:
        """``u``, ``v`` 를 잇는 간선 객체를 반환한다. 없으면 ``KeyError``."""
        ...

    @abstractmethod
    def has_edge(self, u: Vertex, v: Vertex) -> bool:
        """``u``, ``v`` 를 잇는 간선이 그래프에 존재하면 ``True`` 를 반환한다."""
        ...

    @abstractmethod
    def out_edges(self, v: Vertex) -> list[E]:
        """정점 ``v`` 에서 나가는 간선들을 반환한다."""
        ...

    @abstractmethod
    def in_edges(self, v: Vertex) -> list[E]:
        """정점 ``v`` 로 들어오는 간선들을 반환한다."""
        ...

    @abstractmethod
    def vertices(self) -> list[Vertex]:
        """그래프에 포함된 모든 정점을 반환한다."""
        ...

    @property
    @abstractmethod
    def num_vertices(self) -> int:
        """그래프의 정점 수."""
        ...

    @property
    @abstractmethod
    def num_edges(self) -> int:
        """그래프의 간선 수."""
        ...

    @abstractmethod
    def delete_vertex(self, v: Vertex) -> None:
        """정점과 인접 간선을 모두 제거한다. 없으면 ``KeyError``."""
        ...

    @abstractmethod
    def delete_edge(self, u: Vertex, v: Vertex) -> None:
        """``u``, ``v`` 를 잇는 간선을 제거한다. 없으면 ``KeyError``."""
        ...

    @abstractmethod
    def reverse(self) -> Self:
        """모든 간선 방향을 반전한 새 그래프를 반환한다. ``DIRECTED`` 전용."""
        ...

    @abstractmethod
    def _add_edge_from(self, edge: E) -> None:
        """간선 객체로부터 그래프에 간선을 추가한다. ``union`` 내부에서 사용."""
        ...

    @classmethod
    @abstractmethod
    def from_edge_list(cls, edges: list, *, kind: EdgeKind = EdgeKind.UNDIRECTED) -> _AbstractGraph:
        """간선 목록으로 그래프를 생성한다."""
        ...

    @abstractmethod
    def to_edge_list(self) -> list[tuple]:
        """간선을 튜플 목록으로 반환한다."""
        ...

    @classmethod
    @abstractmethod
    def from_dot(cls, s: str) -> _AbstractGraph:
        """DOT 문자열에서 그래프를 복원한다."""
        ...

    @abstractmethod
    def to_dot(self) -> str:
        """그래프를 DOT 언어 문자열로 직렬화한다."""
        ...

    @classmethod
    @abstractmethod
    def from_json(cls, s: str) -> _AbstractGraph:
        """JSON 문자열에서 그래프를 복원한다."""
        ...

    @abstractmethod
    def to_json(self) -> str:
        """그래프를 JSON 문자열로 직렬화한다."""
        ...

    @classmethod
    @abstractmethod
    def from_adjacency_matrix(
        cls, m: list[list], labels: list[str] | None = None, *, kind: EdgeKind = EdgeKind.UNDIRECTED
    ) -> _AbstractGraph:
        """인접 행렬에서 그래프를 생성한다."""
        ...

    @abstractmethod
    def to_adjacency_matrix(self) -> list[list]:
        """인접 행렬을 반환한다."""
        ...

    @abstractmethod
    def _validate(self) -> None:
        """내부 자료구조의 일관성을 검증한다. 주로 테스트에서 사용한다."""
        ...

    @abstractmethod
    def _to_graphviz(self) -> Any:
        """Graphviz 렌더링 객체를 반환한다."""
        ...

    @property
    def A(self) -> list[list]:
        """인접 행렬. ``to_adjacency_matrix()`` 와 동일."""
        return self.to_adjacency_matrix()

    def show(self, *, format: Literal["pdf", "svg", "png"] = "png") -> None:
        """그래프를 렌더링해 시스템 뷰어로 연다."""
        dot = self._to_graphviz()
        dot.format = format
        dot.view(cleanup=True)

    def _repr_svg_(self) -> str:
        """Jupyter Notebook에서 SVG로 인라인 렌더링할 때 호출된다."""
        svg = self._to_graphviz().pipe("svg").decode()
        return svg.replace("<svg ", '<svg style="background:transparent;" ', 1)

    def neighbors(self, v: Vertex) -> list[Vertex]:
        """정점 ``v`` 에서 이동 가능한 인접 정점들을 반환한다."""
        return [e.dst for e in self.out_edges(v)]

    def out_degree(self, v: Vertex) -> int:
        """정점 ``v`` 의 진출 차수(out-degree)를 반환한다."""
        return len(self.out_edges(v))

    def in_degree(self, v: Vertex) -> int:
        """정점 ``v`` 의 진입 차수(in-degree)를 반환한다."""
        return len(self.in_edges(v))

    def degree(self, v: Vertex) -> int:
        """정점 ``v`` 의 차수를 반환한다.

        무방향 그래프에서는 연결된 간선 수, 단방향 그래프에서는 진출 차수(out-degree)다.
        """
        return self.out_degree(v)

    def contains_edge(self, edge: Edge | WeightedEdge) -> bool:
        """간선의 kind와 (있다면) weight까지 엄격하게 비교해 포함 여부를 반환한다."""
        from core.graph.primitives.edge import WeightedEdge

        if not (edge.kind == self.kind and self.has_edge(edge.src, edge.dst)):
            return False
        if isinstance(edge, WeightedEdge):
            found = self.get_edge(edge.src, edge.dst)
            return isinstance(found, WeightedEdge) and found.weight == edge.weight
        return True

    def contains_walk(self, walk: Walk | WeightedWalk) -> bool:
        """워크를 구성하는 모든 간선이 그래프에 존재하면 ``True`` 를 반환한다.

        간선의 kind가 그래프와 다르거나, ``WeightedWalk`` 의 가중치가 맞지 않으면 ``False``.
        ``walk in graph`` 연산자로도 동일하게 확인할 수 있다.
        """
        from core.graph.primitives.edge import WeightedEdge
        from core.graph.walk import WeightedWalk

        if walk.kind != self.kind:
            return False
        if isinstance(walk, WeightedWalk):
            for e in walk.edges:
                if not self.has_edge(e.src, e.dst):
                    return False
                found = self.get_edge(e.src, e.dst)
                if not (isinstance(found, WeightedEdge) and found.weight == e.weight):
                    return False
            return True
        return all(self.has_edge(e.src, e.dst) for e in walk.edges)

    def __contains__(self, item: Vertex | Edge | WeightedEdge | Walk | WeightedWalk) -> bool:
        """``in`` 연산자로 정점, 간선, 워크의 포함 여부를 확인한다.

        - ``vertex in graph`` → :meth:`has_vertex` 호출
        - ``edge in graph`` → :meth:`has_edge` 호출
        - ``walk in graph`` → :meth:`contains_walk` 호출
        """
        from core.graph.primitives.edge import Edge, WeightedEdge
        from core.graph.primitives.vertex import Vertex
        from core.graph.walk import Walk, WeightedWalk

        match item:
            case Walk() | WeightedWalk():
                return self.contains_walk(item)
            case WeightedEdge() | Edge():
                return self.contains_edge(item)
            case Vertex():
                return self.has_vertex(item)
            case _:
                return NotImplemented

    def union(self, other: Self) -> Self:
        """두 그래프의 정점·간선 유니온을 반환한다. 간선이 겹치면 ``self`` 쪽을 유지한다."""
        g = copy.deepcopy(self)
        for v in other.vertices():
            g.add_vertex(v)
        for v in other.vertices():
            for e in other.out_edges(v):
                if not g.has_edge(e.src, e.dst):
                    g._add_edge_from(e)
        return g

    def disjoint_union(self, other: Self) -> Self:
        """두 그래프의 서로소 유니온을 반환한다. 정점 레이블이 겹치면 ``ValueError``."""
        conflict = {v.label for v in self.vertices()} & {v.label for v in other.vertices()}
        if conflict:
            raise ValueError(f"disjoint_union: 레이블 충돌 {conflict}")
        return self.union(other)

    def is_equal(self, other: _AbstractGraph) -> bool:
        """``self`` 와 ``other`` 가 같은 타입·방향성·정점·간선(가중치/용량 포함)이면 ``True``.

        ``g1 == g2`` 와 동일.
        """
        if type(self) is not type(other):
            return False
        if self.kind != other.kind:
            return False
        if self.num_vertices != other.num_vertices or self.num_edges != other.num_edges:
            return False
        if set(self.vertices()) != set(other.vertices()):
            return False
        for v in self.vertices():
            for e in self.out_edges(v):
                if not other.has_edge(e.src, e.dst):
                    return False
                if e != other.get_edge(e.src, e.dst):
                    return False
        return True

    def __eq__(self, other: object) -> bool:
        """``g1 == g2`` — :meth:`is_equal` 위임."""
        if not isinstance(other, _AbstractGraph):
            return NotImplemented
        return self.is_equal(other)

    __hash__ = None  # type: ignore[assignment]  # 가변 객체이므로 해시 비활성화

    def is_subgraph_of(self, other: _AbstractGraph) -> bool:
        """``self`` 의 모든 정점·간선이 ``other`` 에 포함되면 ``True``.

        간선의 가중치/용량과 ``kind`` 까지 일치해야 한다. 타입이 다르면 ``False``.
        """
        if type(self) is not type(other):
            return False
        if self.kind != other.kind:
            return False
        if not all(other.has_vertex(v) for v in self.vertices()):
            return False
        for v in self.vertices():
            for e in self.out_edges(v):
                if not other.has_edge(e.src, e.dst):
                    return False
                if e != other.get_edge(e.src, e.dst):
                    return False
        return True

    def is_isomorphic_to(self, other: _AbstractGraph) -> bool:
        """두 그래프가 동형(isomorphic)인지 확인한다.

        1-Weisfeiler-Lehman 색 정제로 비동형을 다항 시간에 걸러내고, 같은 WL
        색깔에 속하는 정점끼리만 매핑을 시도하는 backtracking으로 확정한다.
        가중치/용량은 WL 시그니처에 포함되어 동형 판정에 반영된다.

        타입이 다르거나 ``kind`` 가 다르면 ``False``. WL이 통과하더라도 정규
        그래프 등에서는 backtracking이 분기를 많이 시도할 수 있다.

        시간 복잡도:
            - 1-WL 필터: ``O(V · (V + E log V))`` — 최대 ``V`` 회 반복, 각 반복에서
              모든 정점의 이웃 멀티셋을 정렬한다. 비동형의 대부분은 여기서 거부된다.
            - 백트래킹 (worst case): ``O(∏ |C_i|! · E)`` — ``C_i`` 는 ``i`` 번째 WL
              색 그룹의 크기. 모든 정점이 같은 색이면 ``O(V! · E)`` 까지 늘어난다
              (정규 그래프, CFI 등 1-WL이 구분 못 하는 경우).
            - 실용적: 차수 분포가 다양한 그래프에서는 WL이 거의 모든 정점을 유일한
              색으로 분리해 백트래킹이 ``O(V + E)`` 수준에서 끝난다.
        """
        from core.graph.primitives.edge import WeightedEdge
        from core.graph.primitives.flow_edge import FlowEdge

        if type(self) is not type(other):
            return False
        if self.kind != other.kind:
            return False
        if self.num_vertices != other.num_vertices or self.num_edges != other.num_edges:
            return False

        def attrs_match(e1: object, e2: object) -> bool:
            if isinstance(e1, WeightedEdge) and isinstance(e2, WeightedEdge):
                return e1.weight == e2.weight
            if isinstance(e1, FlowEdge) and isinstance(e2, FlowEdge):
                return e1.capacity == e2.capacity and e1.flow == e2.flow
            return True

        refined = _wl_refine_pair(self, other)
        if refined is None:
            return False
        self_color, other_color = refined

        # 정점을 WL 색깔별로 묶음 — 백트래킹은 같은 색끼리만 시도
        other_by_color: dict[int, list[Vertex]] = {}
        for v, c in other_color.items():
            other_by_color.setdefault(c, []).append(v)

        # 색깔 그룹이 작은 정점부터 매핑 — 분기 폭을 일찍 좁힘
        order = sorted(self.vertices(), key=lambda v: len(other_by_color[self_color[v]]))
        mapping: dict[Vertex, Vertex] = {}
        used: set[Vertex] = set()

        def backtrack(i: int) -> bool:
            if i == len(order):
                return True
            u = order[i]
            for w in other_by_color[self_color[u]]:
                if w in used:
                    continue
                ok = True
                for e in self.out_edges(u):
                    if e.dst in mapping:
                        mapped = mapping[e.dst]
                        if not other.has_edge(w, mapped) or not attrs_match(
                            e, other.get_edge(w, mapped)
                        ):
                            ok = False
                            break
                if ok and self.kind == EdgeKind.DIRECTED:
                    for e in self.in_edges(u):
                        if e.src in mapping:
                            mapped = mapping[e.src]
                            if not other.has_edge(mapped, w) or not attrs_match(
                                e, other.get_edge(mapped, w)
                            ):
                                ok = False
                                break
                if not ok:
                    continue
                mapping[u] = w
                used.add(w)
                if backtrack(i + 1):
                    return True
                del mapping[u]
                used.remove(w)
            return False

        return backtrack(0)


    def __neg__(self) -> Self:
        """``-g`` — :meth:`reverse` 위임."""
        return self.reverse()

    def __add__(self, other: object) -> Self:
        """``g + v`` / ``g + edge`` / ``g + walk`` / ``g + g2`` — 새 그래프 반환."""
        if isinstance(other, _AbstractGraph):
            return self.union(other)  # type: ignore[return-value]
        g = copy.deepcopy(self)
        g += other
        return g

    def __sub__(self, other: object) -> Self:
        """``g - v`` / ``g - edge`` / ``g - walk`` — 새 그래프 반환."""
        g = copy.deepcopy(self)
        g -= other
        return g

    def __or__(self, other: Self) -> Self:
        """``g1 | g2`` — :meth:`disjoint_union` 위임."""
        return self.disjoint_union(other)

    def __isub__(self, other: object) -> Self:
        """``g -= v`` / ``g -= edge`` / ``g -= walk`` — in-place 제거."""
        from core.graph.primitives.edge import Edge, WeightedEdge
        from core.graph.primitives.vertex import Vertex
        from core.graph.walk import Walk, WeightedWalk

        match other:
            case Vertex():
                self.delete_vertex(other)
            case Edge() | WeightedEdge():
                self.delete_edge(other.src, other.dst)
            case Walk() | WeightedWalk():
                for e in other.edges:
                    self.delete_edge(e.src, e.dst)
            case _:
                return NotImplemented  # type: ignore[return-value]
        return self

    def __getitem__(self, key: object) -> object:
        """``g[v]`` → neighbors, ``g[u, v]`` → :meth:`get_edge`."""
        from core.graph.primitives.vertex import Vertex

        if isinstance(key, Vertex):
            return self.neighbors(key)
        u, v = key  # type: ignore[misc]
        return self.get_edge(u, v)

    def __len__(self) -> int:
        """``len(graph)`` 로 정점 수를 반환한다."""
        return self.num_vertices

    def __iter__(self) -> Iterator[Vertex]:
        """``for v in graph`` 로 모든 정점을 순회한다."""
        return iter(self.vertices())


def _wl_refine_pair(
    g1: _AbstractGraph,
    g2: _AbstractGraph,
) -> tuple[dict[Vertex, int], dict[Vertex, int]] | None:
    """두 그래프를 동시에 1-Weisfeiler-Lehman 정제.

    "색깔"이란?
        WL 알고리즘의 관용 표현으로, 정점에 붙이는 정수 레이블이다. 같은 색깔의
        두 정점은 "지금까지의 정제 단계에서 구조적으로 구별 불가능"하다는 의미다
        (그래프 이론의 graph coloring과 통하는 동치류 개념). 본 구현에서는 정수
        ID로 표현되며, ``sig_to_id`` 가 시그니처를 색깔 ID로 정규화한다.

    알고리즘:
        1. 초기 색깔 = 정점의 차수 (유향이면 ``(in_deg, out_deg)``).
        2. 각 라운드:  새 색깔(v) = (이전 색깔(v), 정렬된 {(이웃 색깔, 간선 속성)}).
           이웃의 색 분포가 다르면 두 정점도 다른 색으로 갈라진다.
        3. 분할이 더 이상 정제되지 않을 때까지 반복 — 정점 수만큼 반복하면 안정화.

    구현 메모:
        - 두 그래프가 ``sig_to_id`` 를 공유해 색깔 ID가 그래프 간에 비교 가능하다.
        - 매 라운드마다 히스토그램이 갈라지면 즉시 ``None`` 을 반환해 비동형 판정.
        - 가중치/용량은 이웃 멀티셋의 ``edge_attr`` 로 반영된다.

    Returns:
        안정화된 ``(color1, color2)`` 또는 색깔 히스토그램이 다르면 ``None``.
    """
    from core.graph.primitives.edge import WeightedEdge
    from core.graph.primitives.flow_edge import FlowEdge

    def edge_attr(e: object) -> object:
        if isinstance(e, WeightedEdge):
            return ("w", e.weight)
        if isinstance(e, FlowEdge):
            return ("c", e.capacity, e.flow)
        return None

    def init_sig(g: _AbstractGraph, v: Vertex) -> object:
        if g.kind == EdgeKind.DIRECTED:
            return (g.in_degree(v), g.out_degree(v))
        return g.degree(v)

    def refine_sig(g: _AbstractGraph, v: Vertex, color: dict[Vertex, int]) -> object:
        if g.kind == EdgeKind.DIRECTED:
            out_ms = tuple(sorted((color[e.dst], edge_attr(e)) for e in g.out_edges(v)))
            in_ms = tuple(sorted((color[e.src], edge_attr(e)) for e in g.in_edges(v)))
            return (color[v], out_ms, in_ms)
        ms = tuple(sorted((color[e.dst], edge_attr(e)) for e in g.out_edges(v)))
        return (color[v], ms)

    sig_to_id: dict[object, int] = {}

    def canon(sig: object) -> int:
        if sig not in sig_to_id:
            sig_to_id[sig] = len(sig_to_id)
        return sig_to_id[sig]

    color1: dict[Vertex, int] = {v: canon(init_sig(g1, v)) for v in g1.vertices()}
    color2: dict[Vertex, int] = {v: canon(init_sig(g2, v)) for v in g2.vertices()}
    if sorted(color1.values()) != sorted(color2.values()):
        return None

    # 1-WL은 정점 수만큼 반복하면 안정화된다
    for _ in range(g1.num_vertices):
        sig_to_id.clear()
        new1 = {v: canon(refine_sig(g1, v, color1)) for v in g1.vertices()}
        new2 = {v: canon(refine_sig(g2, v, color2)) for v in g2.vertices()}
        if sorted(new1.values()) != sorted(new2.values()):
            return None
        # 분할이 더 이상 정제되지 않으면 안정화 — 색깔 수가 그대로면 종료
        if len(set(new1.values())) == len(set(color1.values())):
            return new1, new2
        color1, color2 = new1, new2
    return color1, color2
