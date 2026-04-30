# 그래프 라이브러리 설계

algoforge의 그래프 서브시스템에 대한 세부 설계 문서입니다.

> **범례**: ✅ 구현 완료 · 🔲 구현 예정

---

## 목표와 영감

- **[graaf](https://github.com/bobluppes/graaf)** (C++) — 기능 커버리지와 내부 구조. 알고리즘을 Graph 메서드가 아닌 독립 함수로 두는 철학.
- **[galoisenne](https://github.com/breandan/galoisenne)** (Kotlin) — 연산자 오버로딩 기반의 간결한 DSL.

내부는 graaf처럼 탄탄하게, 외부 표면은 galoisenne처럼 간결하게.

---

## 아키텍처

### 레이어 분리

```
core/graph/              ← 자료구조 계층
  primitives/            ← 기본 타입
  walk/                  ← 중간 표현 (IR)
  graph/                 ← 그래프 자료구조

graph/                   ← 알고리즘 계층
```

**의존 방향**: `graph/`는 `core/graph/`를 import할 수 있지만 역방향은 금지.

### 타입 계층

```
_AbstractGraph[E] (ABC)
├── UnweightedGraph          (_AbstractGraph[Edge])
├── WeightedGraph[W: Weight] (_AbstractGraph[WeightedEdge[W]])
└── FlowGraph[W: Weight]     (_AbstractGraph[FlowEdge[W]])
```

가중치 유무와 유량 여부를 타입으로 구분한다. 런타임 플래그가 아니다.
`dijkstra(g: WeightedGraph[W], ...)`에 무가중 그래프를 넘기면 정적으로 거부된다.

### Walk: 중간 표현 (IR)

연산자는 구문(syntax)만 기록하는 AST를 만들고, Graph 생성자가 의미(semantics)를 해석한다.
SQLAlchemy의 `BinaryExpression`, TensorFlow 1.x의 `tf.Graph`와 같은 패턴.

```
Walk            정점·간선 중복 허용
 └── Trail      간선 중복 없음
      └── Path  정점 중복도 없음
```

알고리즘 반환 타입이 정확해진다:

```python
def dijkstra(...) -> Path: ...          # 단순 경로 보장
def euler_circuit(...) -> Trail: ...    # 모든 간선 정확히 한 번
def dfs_walk(...) -> Walk: ...          # 일반 traversal 기록
```

### DSL 설계 원칙

- **`@overload` + `match`**: `@overload`로 정적 타입 선언, `match`로 런타임 분기
- **`@runtime_checkable` Protocol**: `Weight`가 `case Weight()`로 매칭 가능
- **Positional-only `/`**: 오버로드 시그니처 불일치 방지
- **`__r*__` 없음**: 진입점이 항상 `Vertex`·`Walk`이라 역방향 연산자 불필요
- **헬퍼 함수 추출 없음**: 클래스별 케이스 집합이 달라 합치면 분기가 되살아남
- **연산자 ↔ 메서드 대응**: 모든 연산자 오버로딩은 동일한 동작의 named method를 함께 제공한다. 연산자는 syntactic sugar, 메서드는 명시적 대안.

| 연산자 | 대응 메서드 |
|--------|------------|
| `u - v`, `u >> v`, `u & v` | `Edge(u, v, kind=...)` 직접 생성 |
| `g + v` | `g.add_vertex(v)` |
| `g + edge` / `g + walk` | `g.add_edge(...)` |
| `g - v` | `g.delete_vertex(v)` |
| `g - edge` / `g - walk` | `g.delete_edge(...)` |
| `~g` | `g.complement()` |
| `-g` | `g.reverse()` |
| `g1 + g2` | `g1.union(g2)` |
| `g1 \| g2` | `g1.disjoint_union(g2)` |

---

## ✅ 구현 완료

### 기본 타입 (`core/graph/primitives/`)

| 항목 | 설명 |
|------|------|
| `Vertex` | `label: str`로 식별되는 불변 정점. 연산자 오버로딩으로 간선·워크 생성 |
| `Edge` | 무가중 간선. `(src, dst, kind)` |
| `WeightedEdge[W]` | 가중 간선. `(src, dst, kind, weight)` |
| `FlowEdge[W]` | 유량 간선. `(src, dst, capacity, flow)`. 생성 시 역방향 간선 자동 쌍 생성 |
| `EdgeKind` | `UNDIRECTED / DIRECTED / BIDIRECTED` |
| `Weight` | `__hash__`, `__eq__`, `__lt__`, `__add__`, `__sub__`를 가지는 `@total_ordering` + `@runtime_checkable` Protocol. `__lt__` 하나만 구현하면 나머지 비교 연산자 자동 생성 |
| `_WeightedEdgeBuilder[W]` | `Vertex - weight` 중간 빌더 |
| `_WeightedWalkBuilder[W]` | `WeightedEdge - weight` 중간 빌더 |

**연산자 의미**

| 표현식 | 결과 | kind |
|--------|------|------|
| `u - v` | `Edge` | `UNDIRECTED` |
| `u - 3 - v` | `WeightedEdge[int]` | `UNDIRECTED` |
| `u >> v` | `Edge` | `DIRECTED` |
| `u << v` | `Edge` (src↔dst 교환) | `DIRECTED` |
| `u & v` | `Edge` | `BIDIRECTED` |

### Walk 계층 (`core/graph/walk/`)

| 항목 | 제약 |
|------|------|
| `Walk` | 없음 (정점·간선 중복 허용) |
| `WeightedWalk[W]` | 없음 (가중 버전) |
| `Trail` | 간선 중복 없음 |
| `Path` | 정점·간선 중복 없음 |

모든 Walk 타입은 연산자로 이어 붙여 확장 가능하며, `__post_init__`에서 방향성·가중치 혼합을 즉시 검증한다.

### 그래프 자료구조 (`core/graph/graph/`)

**`_AbstractGraph[E]` 공통 인터페이스**

| 메서드 / 연산자 | 설명 |
|----------------|------|
| `add_vertex(v)` | 정점 추가 |
| `has_vertex(v)` | 정점 존재 여부 |
| `get_vertex(label)` | 레이블로 정점 조회. 없으면 `KeyError` |
| `has_edge(u, v)` | 간선 존재 여부 (정점 쌍) |
| `get_edge(u, v)` | 간선 객체 조회. 없으면 `KeyError` |
| `contains_edge(edge)` | kind·weight까지 엄격하게 비교한 간선 포함 여부 |
| `contains_walk(walk)` | Walk의 모든 간선 존재 여부 (kind·weight 포함) |
| `neighbors(v)` | 인접 정점 |
| `vertices()` | 전체 정점 |
| `degree(v)` | 차수 |
| `show(format=)` | Graphviz 뷰어 (`"pdf"` · `"svg"` · `"png"`) |
| `_repr_svg_()` | Jupyter 인라인 SVG 렌더링 |
| `v in g` | 정점 포함 여부 |
| `edge in g` | `contains_edge` 위임 |
| `walk in g` | `contains_walk` 위임 |
| `len(g)` | 정점 수 |
| `for v in g` | 정점 순회 |
| `.A` | 인접 행렬 (`to_adjacency_matrix()` 단축) |
| `from_edge_list` / `to_edge_list` | 간선 목록 직렬화·역직렬화 |
| `from_dot` / `to_dot` | DOT 언어 직렬화·역직렬화 |
| `from_json` / `to_json` | JSON 직렬화·역직렬화 |
| `from_adjacency_matrix` / `to_adjacency_matrix` | 인접 행렬 직렬화·역직렬화 |
| `delete_vertex(v)` | 정점과 인접 간선 제거. 없으면 `KeyError` |
| `delete_edge(u, v)` | 간선 제거. 없으면 `KeyError` |
| `reverse()` | 모든 간선 방향 반전한 새 그래프. `DIRECTED` 전용 |
| `union(g2)` | 정점·간선 유니온. 겹치는 간선은 `self` 유지 |
| `disjoint_union(g2)` | 서로소 유니온. 레이블 충돌 시 `ValueError` |
| `g + v/edge/walk` | `add_vertex`/`add_edge` → 새 그래프 반환 |
| `g + g2` | `union(g2)` → 새 그래프 반환 |
| `g += v/edge/walk` | in-place `add_vertex`/`add_edge` |
| `g - v/edge/walk`, `g -= v/edge/walk` | `delete_vertex`/`delete_edge`. `-`는 새 그래프, `-=`는 in-place |
| `-g` | `reverse()` 단축 |
| `g1 \| g2` | `disjoint_union(g2)` 단축 |
| `g[v]` | `neighbors(v)` 단축 |
| `g[u, v]` | `get_edge(u, v)` 단축 → 간선 객체(`Edge`/`WeightedEdge`/`FlowEdge`) 반환 |

**`UnweightedGraph`**: `add_edge(u, v)`, `complement()`, `~g` 추가

**`WeightedGraph[W]`**: `add_edge(u, v, weight)`, `set_edge(u, v, weight)`, `weighted_neighbors(v)`, `g[u,v]=w` 추가

**`FlowGraph[W]`**: `add_edge(u, v, capacity)`, `set_capacity(u, v, capacity)`, `fg[u,v]=cap`, `edges(v)` 추가. 항상 `DIRECTED`. 역방향 간선 자동 관리

**`Graph` 팩토리**: 워크 타입과 `flow` 플래그로 구현체를 자동 추론

```python
Graph(a - b - c)                   # → UnweightedGraph
Graph(a - 3 - b - 2 - c)          # → WeightedGraph[int]
Graph(a >> 10 >> b, flow=True)     # → FlowGraph[int]
Graph(flow=True)                   # → FlowGraph (빈 그래프)
```

### 패턴 생성자 (`Graph` 팩토리)

```python
Graph.path(A, B, C, D, kind=EdgeKind.UNDIRECTED)           # 경로
Graph.cycle(A, B, C, kind=EdgeKind.UNDIRECTED)              # 순환
Graph.complete(A, B, C, D, kind=EdgeKind.UNDIRECTED)        # K_n
Graph.bipartite([A, B], [C, D], kind=EdgeKind.UNDIRECTED)   # K_{m,n}
Graph.grid(rows=3, cols=3, kind=EdgeKind.UNDIRECTED)        # 격자 (정점 자동 생성)
Graph.star(center, A, B, C, kind=EdgeKind.UNDIRECTED)       # 별 (첫 인자가 center)
Graph.wheel(center, A, B, C, D, kind=EdgeKind.UNDIRECTED)   # 바퀴 (첫 인자가 center)
Graph.petersen()                                            # 페테르센 그래프 (고정)
```

---

## 🔲 구현 예정

---

### 그래프 변환

```python
g.subgraph([A, B, C])
g.transitive_closure()
g.line_graph()
g.contract(A, B)
```

---

### 그래프 비교

```python
g1 == g2
g1.is_isomorphic_to(g2)
g1.is_subgraph_of(g2)
```

---

### 매트릭스 인터페이스

`g.A` / `to_adjacency_matrix()` / `from_adjacency_matrix()`는 `dict[Vertex, dict[Vertex, E]]` 기반.
값이 `E` (그래프의 간선 타입) 이므로 모든 그래프 타입에 일관되게 적용된다.
인덱스가 아닌 정점 레이블로 직접 접근하므로 `labels` 파라미터 불필요.

```python
# UnweightedGraph (E = Edge)
g.A[A][B]   # Edge(src=A, dst=B, kind=UNDIRECTED)

# WeightedGraph[W] (E = WeightedEdge[W])
g.A[A][B]   # WeightedEdge(src=A, dst=B, kind=UNDIRECTED, weight=5)

# FlowGraph[W] (E = FlowEdge[W])
g.A[A][B]   # FlowEdge(src=A, dst=B, capacity=10, flow=3)

# 키 없음 = 간선 없음 (KeyError)
B in g.A[A]   # 연결 여부

g.D    # 차수 행렬: dict[Vertex, int]
g.L    # 라플라시안: dict[Vertex, dict[Vertex, int]]  (WeightedGraph 전용)
```

---

### 타입 정제

```python
SimpleGraph    # 다중 간선·자기 루프 없음
DAG            # 유향 + 비순환 보장
Tree           # 연결 + 비순환
BipartiteGraph # 두 정점 집합 구분
```

---

### 간선 메타데이터

```python
A - (3, label="x") - B
A - {"weight": 3, "color": "red"} - B
```

---

### 알고리즘 (`graph/`)

| 파일 | 알고리즘 |
|------|---------|
| `traversal.py` | BFS, DFS |
| `shortest_path.py` | Dijkstra, Bellman-Ford, Floyd-Warshall, SPFA |
| `mst.py` | Kruskal, Prim |
| `scc.py` | Tarjan, Kosaraju |
| `toposort.py` | 위상 정렬 |
| `bridges.py` | 다리·단절점 |
| `flow.py` | Dinic, MCMF |
| `matching.py` | 이분 매칭, 일반 매칭 |
| `coloring.py` | 그래프 채색 |
| `euler.py` | Euler 경로·회로 |
| `hamilton.py` | Hamilton 경로·회로 |
| `tree_algorithms.py` | LCA, HLD, centroid decomposition |

---

### 렌더링·시각화 (`graph/render.py`, `graph/animate.py`)

알고리즘은 결과값(`Path`, `Trail`, `Walk`, `WeightedGraph` 등)만 반환한다.
시각화는 유저가 원본 그래프에 결과를 직접 하이라이팅하는 방식으로 제어한다.

#### 하이라이팅 shortcut

```python
path = dijkstra(g, A, B)
g.show(highlight=path)             # path 포함 간선·정점 자동 강조

mst = kruskal(g)
g.show(highlight=mst)              # MST 간선 강조

g.show(highlight=[path1, path2])   # 여러 결과, 색 자동 배분
```

`highlight`는 `Walk`, `Path`, `Trail`, `_AbstractGraph` 를 모두 받는다.
포함된 간선·정점을 자동으로 감지해 강조한다.

#### 세밀한 커스텀 스타일

`highlight`로 부족할 때 람다로 직접 제어한다.

```python
from graph.render import VertexStyle, EdgeStyle

g.show(
    layout="dot",
    vertex_style=lambda v: VertexStyle(color="red" if v == src else "white"),
    edge_style=lambda e: EdgeStyle(width=3 if e in path else 1),
)
g.render("out.svg")
```

#### 단계별 애니메이션

```python
from graph.animate import animate_to_gif

animate_to_gif(dijkstra_steps(g, src=u), output="dijkstra.gif", fps=2)
```

---

### 컬렉션 인터페이스

```python
g.vertices.filter(lambda v: g.degree(v) > 3)
g.edges.where(lambda e: e.weight < 0).map(lambda e: e.src)
g.edges.sorted_by(lambda e: e.weight)
```

---

## 테스트 전략

| 방식 | 내용 |
|------|------|
| 불변식 검증 | `_validate()` — 인접 리스트 대칭성, 엔드포인트 존재 확인 |
| Brute-force 교차 | Dijkstra vs Bellman-Ford, Kruskal vs Prim, Tarjan vs Kosaraju |
| 제네릭 가중치 | `@pytest.mark.parametrize("W", [int, float, Fraction])` |
| 정적 타입 | pyrefly로 `dijkstra(UnweightedGraph, ...)` 에러 유도 |

---

## 열린 질문

- **인접 행렬**: `dict[Vertex, dict[Vertex, E]]`로 통일. `E`는 그래프의 간선 타입 파라미터. numpy 미사용. 스펙트럴 알고리즘은 범위 밖.
- **멀티그래프**: 현재 같은 정점 쌍에 간선 여러 개 허용. 단순 그래프 가정 알고리즘은 케이스별 처리.
- **Semiring 추상화**: `Weight` 프로토콜로 시작. tropical semiring 등 필요 시 확장.
- **하이퍼그래프**: 범위 밖.

---

## 참고 자료

- [graaf](https://github.com/bobluppes/graaf) — 구조적 영감
- [galoisenne](https://github.com/breandan/galoisenne) — DSL·대수적 영감
- [Boost Graph Library](https://www.boost.org/doc/libs/1_82_0/libs/graph/doc/index.html)
- [NetworkX](https://networkx.org/) — 레퍼런스 API
- [Python graphviz](https://graphviz.readthedocs.io/) — 렌더링 백엔드
