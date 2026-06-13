from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from scaffold.graph.primitives.vertex import Vertex


def _as_accessor(spec: str | Callable[[Any], Any]) -> Callable[[Any], Any]:
    """속성 이름(문자열) 또는 callable 을 노드 접근 함수로 정규화한다.

    문자열이면 ``getattr`` 로, callable 이면 그대로 호출한다::

        _as_accessor("value")(node)  # node.value
        _as_accessor(lambda n: n.key)(node)  # node.key
    """
    if callable(spec):
        return spec
    return lambda node: getattr(node, spec)


class Tree:
    """루트가 있는 순서 트리(rooted ordered tree).

    각 노드는 ``label`` 로 식별되는 :class:`Vertex` 이고, 자식은 **순서 있는 list**
    로 보관된다. 자식 list 의 ``None`` 항목은 *빈 슬롯* 으로, 렌더링 시 투명
    placeholder 가 되어 형제의 좌/우 위치를 보존한다.

    이 ``None`` 슬롯 컨벤션 덕분에 별도의 이진 트리 클래스 없이도, 이진 트리에서
    한쪽 자식만 있는 경우(왼쪽만/오른쪽만)를 정확히 렌더할 수 있다. 일반 n-ary
    트리(trie 등)는 ``None`` 없이 자식을 순서대로 나열하면 된다.

    ``scaffold`` 를 전혀 모르는 순수 자료구조를 :meth:`from_root` 로 읽어들이므로,
    BST·AVL·heap·trie 어떤 노드 타입이든 같은 방식으로 시각화할 수 있다::

        from scaffold.tree import Tree

        Tree.from_root(bst._root, left="left", right="right", label="value").show()

    렌더링 API(:meth:`show`, ``_repr_svg_``, :meth:`to_dot`)와 ``highlight`` 동작은
    그래프(:class:`~scaffold.graph.graph.abstract._AbstractGraph`)와 동일하게 맞춰져
    있어, 탐색 경로를 ``Walk``/``Path`` 로 강조하는 방식까지 일관된다.

    Note:
        ``label`` 은 트리 안에서 고유해야 한다 (graphviz 노드 id 로 쓰인다). BST 는
        키가 유일하므로 ``label="value"`` 로 충분하다. 표시값이 겹치는 일반 트리는
        고유 식별자를 돌려주는 ``label`` accessor 를 직접 지정해야 한다.
    """

    def __init__(self) -> None:
        """빈 트리를 생성한다. 보통 :meth:`from_root` 로 만든다."""
        self._vertices: dict[str, Vertex] = {}
        self._children: dict[str, list[Vertex | None]] = {}
        self._root: Vertex | None = None

    # --- 구성 ---

    def _add_vertex(self, v: Vertex) -> None:
        """정점을 등록한다. 이미 있으면 아무것도 하지 않는다."""
        if v.label not in self._vertices:
            self._vertices[v.label] = v
            self._children[v.label] = []

    def set_root(self, v: Vertex) -> None:
        """루트 정점을 지정한다. 그래프에 없으면 추가한다."""
        self._add_vertex(v)
        self._root = v

    def add_child(self, parent: Vertex, child: Vertex | None) -> None:
        """``parent`` 의 자식 슬롯에 ``child`` 를 순서대로 추가한다.

        ``child`` 가 ``None`` 이면 빈 슬롯으로, 렌더링 시 투명 placeholder 가 되어
        형제의 좌/우 위치를 보존한다. 이진 트리에서 한쪽 자식만 있을 때 핵심이다::

            tree.add_child(p, left)  # 왼쪽 (실제)
            tree.add_child(p, None)  # 오른쪽 비었음 → 자리만 유지
        """
        self._add_vertex(parent)
        if child is not None:
            self._add_vertex(child)
        self._children[parent.label].append(child)

    @classmethod
    def from_root(
        cls,
        root: Any,
        *,
        children: str | Callable[[Any], Any] | None = None,
        left: str | Callable[[Any], Any] | None = None,
        right: str | Callable[[Any], Any] | None = None,
        label: str | Callable[[Any], Any] = "value",
    ) -> Tree:
        """임의의 노드 객체 트리를 순회해 ``Tree`` 를 만든다.

        노드 타입에 의존하지 않고 accessor(속성명 또는 callable)로만 읽으므로,
        ``scaffold`` 를 모르는 순수 자료구조를 그대로 시각화할 수 있다::

            Tree.from_root(bst._root, left="left", right="right", label="value")
            Tree.from_root(trie.root, children="children", label="char")

        Args:
            root: 트리의 루트 노드 객체. ``None`` 이면 빈 트리를 반환한다.
            children: 자식 list 를 돌려주는 accessor. list 안의 ``None`` 은 빈 슬롯이
                된다. 잎 노드는 ``None`` 이나 빈 list 둘 다 허용한다.
                ``left``/``right`` 와 함께 줄 수 없다.
            left: 이진 트리 편의용 왼쪽 자식 accessor. ``right`` 와 함께 쓴다.
            right: 이진 트리 편의용 오른쪽 자식 accessor. ``left`` 와 함께 쓴다.
                ``left``/``right`` 중 한쪽만 줘도 되며, 빠진 쪽은 빈 슬롯이 된다.
            label: 노드의 라벨(고유 식별자 겸 표시 텍스트) accessor. 기본 ``"value"``.

        Raises:
            ValueError: ``children`` 과 ``left``/``right`` 를 함께 주거나, 셋 다 주지
                않은 경우.
        """
        tree = cls()
        if root is None:
            return tree

        label_fn = _as_accessor(label)
        if children is not None:
            if left is not None or right is not None:
                raise ValueError("children 와 left/right 는 함께 쓸 수 없다")
            children_fn = _as_accessor(children)
        elif left is not None or right is not None:
            left_fn = _as_accessor(left) if left is not None else (lambda _n: None)
            right_fn = _as_accessor(right) if right is not None else (lambda _n: None)
            children_fn = lambda node: [left_fn(node), right_fn(node)]  # noqa: E731
        else:
            raise ValueError("children 또는 left/right 중 하나는 지정해야 한다")

        def build(node: Any) -> Vertex:
            v = Vertex(str(label_fn(node)))
            tree._add_vertex(v)
            kids = list(children_fn(node) or [])  # 잎의 children 이 None 이어도 허용
            if all(c is None for c in kids):  # 순수 잎: placeholder 불필요
                return v
            for child in kids:
                tree.add_child(v, build(child) if child is not None else None)
            return v

        tree._root = build(root)
        return tree

    # --- 조회 ---

    @property
    def root(self) -> Vertex | None:
        """루트 정점. 빈 트리면 ``None``."""
        return self._root

    def children_of(self, v: Vertex) -> list[Vertex | None]:
        """정점 ``v`` 의 자식 슬롯 list. ``None`` 은 빈 슬롯을 뜻한다."""
        return self._children[v.label]

    def vertices(self) -> list[Vertex]:
        """트리에 포함된 모든 정점을 등록 순서(루트부터 전위 순회)대로 반환한다."""
        return list(self._vertices.values())

    @property
    def num_vertices(self) -> int:
        """트리의 정점 수 (빈 슬롯 placeholder 는 제외)."""
        return len(self._vertices)

    # --- 렌더링 ---

    def _to_graphviz(self, *, highlight: object = None) -> Any:
        """Graphviz 렌더링 객체를 생성한다.

        ``ordering="out"`` 으로 자식의 좌→우 순서를 보존하고, 빈 슬롯(``None``)은
        투명 placeholder 노드 + invisible 간선으로 그려 자리를 유지한다. 그래서
        자식이 하나뿐인 노드도 그 자식이 왼쪽인지 오른쪽인지 정확히 드러난다.

        ``highlight`` 와 노드/간선 강조 동작은 그래프와 동일한 헬퍼를 재사용한다.
        간선은 부모→자식 방향이라, ``highlight`` 의 ``Walk``/``Path`` 도 같은
        방향으로 구성해야 매칭된다.
        """
        import graphviz

        from scaffold.graph.graph.abstract import (
            _edge_highlight_attrs,
            _node_highlight_attrs,
            _normalize_highlight,
            _patch_jupyter_transparent,
        )

        groups = _normalize_highlight(highlight)
        dot = graphviz.Digraph()
        dot.attr(bgcolor="transparent", ordering="out")
        dot.attr("node", shape="circle")
        dot.attr("edge", arrowhead="none")

        for label, v in self._vertices.items():
            dot.node(label, **_node_highlight_attrs(v, groups))

        ph = 0
        for label, kids in self._children.items():
            for child in kids:
                if child is None:
                    pid = f"__ph{ph}"
                    ph += 1
                    dot.node(pid, style="invis")
                    dot.edge(label, pid, style="invis")
                else:
                    attrs = _edge_highlight_attrs(label, child.label, False, groups)
                    dot.edge(label, child.label, **attrs)
        return _patch_jupyter_transparent(dot)

    def show(
        self,
        *,
        highlight: object = None,
        format: Literal["pdf", "svg", "png"] = "png",
    ) -> None:
        """트리를 렌더링해 시스템 뷰어로 연다.

        Args:
            highlight: 강조할 ``Walk``/``Path`` 또는 그 list (탐색 경로 등).
                list 로 여러 개 주면 색이 자동 배분된다. 간선은 부모→자식 방향으로
                구성해야 한다.
            format: 출력 포맷.
        """
        dot = self._to_graphviz(highlight=highlight)
        dot.format = format
        dot.view(cleanup=True)

    def _repr_svg_(self) -> str | None:
        """Jupyter Notebook 에서 SVG 로 인라인 렌더링할 때 호출된다.

        graphviz 시스템 바이너리(``dot``)가 없으면 ``None`` 을 돌려줘, Jupyter 가
        ``__repr__`` 의 ASCII 트리로 폴백하게 한다.
        """
        import graphviz

        try:
            svg = self._to_graphviz().pipe("svg").decode()
        except graphviz.ExecutableNotFound:
            return None
        return svg.replace("<svg ", '<svg style="background:transparent;" ', 1)

    def to_dot(self) -> str:
        """트리를 DOT 언어 문자열로 직렬화한다."""
        return self._to_graphviz().source

    # --- 텍스트 렌더링 (graphviz 불필요) ---

    _EMPTY_SLOT = "·"

    def to_text(self) -> str:
        """트리를 들여쓰기 ASCII 아트로 그린다.

        graphviz 없이도 구조를 바로 확인할 수 있다. n-ary 를 위→아래로 들여쓰며,
        빈 슬롯(``None``)은 ``·`` 로 표시해 이진 트리에서 한쪽 자식만 있을 때
        좌/우를 텍스트로도 구분한다::

            50
            ├─ 30
            │  ├─ ·
            │  └─ 40
            └─ 70
               ├─ ·
               └─ 80
        """
        if self._root is None:
            return "(empty tree)"
        lines = [self._root.label]
        self._text_children(self._root, "", lines)
        return "\n".join(lines)

    def _text_children(self, v: Vertex, prefix: str, lines: list[str]) -> None:
        """``v`` 의 자식들을 박스 드로잉 가지로 ``lines`` 에 덧붙인다."""
        kids = self._children[v.label]
        for i, child in enumerate(kids):
            last = i == len(kids) - 1
            branch = "└─ " if last else "├─ "
            lines.append(prefix + branch + (child.label if child is not None else self._EMPTY_SLOT))
            if child is not None:
                self._text_children(child, prefix + ("   " if last else "│  "), lines)

    def __len__(self) -> int:
        """``len(tree)`` 로 정점 수를 반환한다."""
        return self.num_vertices

    def __str__(self) -> str:
        """``print(tree)`` / ``str(tree)`` 로 ASCII 트리를 그린다."""
        return self.to_text()

    # 시각화 객체이므로 repr 도 같은 ASCII 트리 — REPL 에서 `tree` 만 쳐도 보인다.
    __repr__ = __str__
