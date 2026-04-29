from __future__ import annotations

import re

from core.graph.primitives.edge_kind import EdgeKind


def _parse_dot(s: str) -> tuple[EdgeKind, list[str], list[tuple[str, str, str | None]]]:
    """DOT 문자열을 파싱해 ``(kind, 정점 레이블 목록, 간선 목록)``을 반환한다.

    간선 목록의 각 항목은 ``(u_label, v_label, weight_str | None)``이다.
    정점 목록은 등장 순서대로 정렬된다 (standalone 선언 우선, 그 다음 간선 엔드포인트).
    """
    s = s.strip()
    is_digraph = bool(re.search(r"\bdigraph\b", s))

    m = re.search(r"\{(.*)\}", s, re.DOTALL)
    if not m:
        raise ValueError("invalid DOT format: no braces found")
    content = m.group(1)

    op = "->" if is_digraph else "--"
    ident = r'"?([\w.]+)"?'
    edge_re = re.compile(rf"{ident}\s*{re.escape(op)}\s*{ident}(?:\s*\[([^\]]*)\])?")
    label_re = re.compile(r"\blabel\s*=\s*\"?([^\"\s,\]]+)\"?")
    node_re = re.compile(r"^\s*\"?([\w.]+)\"?\s*;?\s*$")

    reserved = frozenset({"graph", "digraph", "subgraph", "node", "edge", "strict"})
    seen: set[str] = set()
    vertices: list[str] = []
    edges: list[tuple[str, str, str | None]] = []
    has_dir_both = False

    def _add(label: str) -> None:
        if label not in reserved and label not in seen:
            seen.add(label)
            vertices.append(label)

    for line in content.splitlines():
        line = line.strip()
        em = edge_re.search(line)
        if em:
            u, v, attrs = em.group(1), em.group(2), em.group(3) or ""
            _add(u)
            _add(v)
            lm = label_re.search(attrs)
            edges.append((u, v, lm.group(1) if lm else None))
            if re.search(r"\bdir\s*=\s*both\b", attrs):
                has_dir_both = True
        else:
            nm = node_re.match(line)
            if nm:
                _add(nm.group(1))

    if is_digraph and has_dir_both:
        kind = EdgeKind.BIDIRECTED
    elif is_digraph:
        kind = EdgeKind.DIRECTED
    else:
        kind = EdgeKind.UNDIRECTED

    return kind, vertices, edges
