# 그래프 라이브러리 설계

algoforge의 그래프 서브시스템에 대한 세부 설계 문서입니다.

## 목표와 영감

- **[graaf](https://github.com/bobluppes/graaf)** (C++) — 기능 커버리지와 내부 구조. 제네릭 vertex/edge 타입, directed/undirected 구분, 알고리즘을 Graph 메서드가 아닌 독립 함수로 두는 철학.
- **[galoisenne](https://github.com/breandan/galoisenne)** (Kotlin) — 프론트엔드 API. 연산자 오버로딩 기반의 간결한 DSL.

내부는 graaf처럼 탄탄하게, 외부 표면은 galoisenne처럼 간결하게.

## 레이어 분리

```
algoforge/core/graph/        ← 자료구조 계층
  base.py                    ← Graph[V] ABC, Vertex
  chain.py                   ← Chain (중간 표현), ChainEdge
  unweighted.py              ← UnweightedGraph
  weighted.py                ← WeightedGraph[W], Weight 프로토콜
  flow_graph.py              ← FlowGraph (역방향 간선 관리)
  io.py                      ← edge list, adjacency matrix, DOT 입출력

algoforge/graph/             ← 알고리즘 계층
  traversal.py               ← BFS, DFS
  shortest_path.py           ← Dijkstra, Bellman-Ford, Floyd-Warshall, SPFA
  mst.py                     ← Kruskal, Prim
  scc.py                     ← Tarjan, Kosaraju
  bridges.py
  toposort.py
  flow.py                    ← Dinic, MCMF
  matching.py
  coloring.py
  euler.py
  hamilton.py
  tree_algorithms.py         ← LCA, HLD, centroid decomposition
  layout.py
  render.py                  ← graphviz 기반 렌더링
  animate.py                 ← 단계별 애니메이션
```

**의존 방향**: `algoforge/graph/`는 `algoforge/core/graph/`를 import할 수 있지만, 역방향은 금지.

## 타입 계층

가중치 유무는 **타입으로 구분**합니다. 런타임 플래그가 아닙니다.

```
Graph[V] (abstract, factory)
├── UnweightedGraph[V]
└── WeightedGraph[V, W: Weight]
```

- `dijkstra(g: WeightedGraph[V, W], ...)`에 무가중 그래프를 넘기면 정적으로 거부됨.
- BFS, DFS처럼 가중치 무관한 알고리즘은 `Graph[V]`를 받아 둘 다 지원.
- 잘못된 상태가 표현 자체로 불가능해짐.

### Weight 프로토콜

```python
class Weight(Protocol):
    def __add__(self, other: Self) -> Self: ...
    def __lt__(self, other: Self) -> bool: ...
    def __le__(self, other: Self) -> bool: ...
```

### 무한대 처리

Dijkstra 결과는 **도달 가능한 정점만** 포함하는 dict. `float('inf')` sentinel 안 씀 → int 가중치와도 호환. 사용자는 `dist.get(v)`로 접근하면 도달 불가능 시 `None`.

## 두 가지 API 스타일

그래프는 **DSL 방식**과 **객체형 방식** 둘 다로 구성할 수 있습니다. 두 스타일은 first-class이고 자유롭게 섞어 쓸 수 있습니다.

### 1. DSL 방식 — Chain을 거친 명시적 평가

```python
from algoforge.core.graph import Vertex, Graph, UnweightedGraph, WeightedGraph

u, v, w = Vertex("u"), Vertex("v"), Vertex("w")

# 연산자는 Chain을 만들기만 함
chain = u - 3 - v - 2 - w        # Chain 인스턴스

# Graph 생성자가 평가
g = WeightedGraph(chain)         # 타입 명시
g = Graph(chain)                 # 자동 추론 (→ WeightedGraph[V, int])
```

### 2. 객체형 방식 — Chain 없이 직접

```python
g = UnweightedGraph[str](directed=False)
g.add_vertex(u)
g.add_vertex(v)
g.add_edge(u, v)
```

### 3. 혼합

```python
g = WeightedGraph(u - 3 - v)     # DSL로 시작
g.add_edge(v, w, weight=5)       # 객체형으로 추가
```

## 연산자 오버로딩의 구조적 문제

연산자가 많은 DSL은 전통적으로 다음 문제들을 겪습니다.

- **코드 중복**: `__add__`와 `__radd__`가 거의 동일한 로직
- **순환 참조**: `A + B = C`를 구현하려면 A가 B·C를, B가 A·C를 알아야 함. 서로 import
- **분기 폭발**: `__sub__` 내부에서 상대 타입마다 `isinstance`/`match` 분기
- **확장 어려움**: 새 타입 추가 시 기존 타입들의 `__r*__` 수정 필요

근본 원인은 **연산자가 주체의 메서드로 디스패치된다**는 것. `a + b`는 항상 `a.__add__(b)`로 먼저 가서, A에게 "B와 어떻게 더할지"를 아는 책임이 간다. 그런데 이건 둘 사이의 관계지 A 단독의 속성이 아니다.

### 해결 전략: 중간 표현(IR)

연산자와 결과를 분리한다. 연산자는 **구문(syntax)** 만 기록하는 AST를 만들고, 별도 해석기가 **의미(semantics)** 를 담당한다.

- 연산자 메서드들은 전부 한 줄짜리 AST 노드 생성
- 모든 해석 로직은 한 곳에 집중
- 각 클래스는 서로를 import할 필요 없음 (공통 AST 타입만 알면 됨)

이 패턴은 컴파일러의 파싱·평가 분리와 동일. SQLAlchemy의 `User.name == "foo"`가 불리언이 아닌 `BinaryExpression` 반환, NumPy/Dask의 lazy expression, TensorFlow 1.x의 `tf.Graph` 전부 같은 원리.

algoforge에서는 이 AST를 **Chain**이라 부른다.

## Chain: 중간 표현

Vertex의 연산자들은 즉시 Graph를 만들지 않고 Chain을 반환한다. Graph 생성자가 Chain을 받아 해석·평가한다.

### 역할 분리

- **Vertex / Chain의 연산자**: 구문만. 각 메서드가 한 줄씩.
- **Graph 생성자**: 의미. 검증·평가 로직이 한 곳에 집중.

### Chain 구조

```python
@dataclass(frozen=True)
class ChainEdge:
    src: Vertex
    dst: Vertex
    kind: Literal["undirected", "directed_fwd", "bidirectional"]
    weight: Weight | None = None

@dataclass
class Chain:
    edges: list[ChainEdge]
    _last: Vertex
    _pending_weight: Weight | None = None
```

Chain은 **순수 데이터**. 평가 로직은 없음. 연산자 (`__sub__`, `__rshift__`, `__lshift__`, `__and__`, `__add__`)는 전부 새 Chain을 반환하는 한 줄짜리 메서드. `validate()`는 방향 일관성과 가중치 유무 일관성만 검사.

### 연산자 의미

| 연산자 | 의미 | kind |
|---|---|---|
| `u - v` | 무방향 간선 | `undirected` |
| `u - 3 - v` | 무방향, 가중치 3 | `undirected` |
| `u >> v` | 유향 u→v | `directed_fwd` |
| `u << v` | 유향 v→u | `directed_fwd` (src, dst swap) |
| `u & v` | 양방향 유향 | `bidirectional` |
| `chain1 + chain2` | 유니온 | — |

### 일관성 규칙

한 Chain 안에서 다음을 섞으면 `validate()`가 `ValueError`를 발생시킵니다.

- **방향성**: `undirected`와 `directed_fwd` 혼합 금지
- **가중치**: 가중치 있는 간선과 없는 간선 혼합 금지

`bidirectional`은 `directed_fwd`와 호환 (둘 다 유향 그래프로 평가됨).

## 클래스 스펙

### Vertex

```python
@dataclass(frozen=True)
class Vertex[V]:
    label: str
    payload: V | None = None
```

연산자 (`__sub__`, `__rshift__`, `__lshift__`, `__and__`)는 모두 `Chain`을 반환.

### Graph (ABC)

모든 그래프가 제공하는 공통 인터페이스.

| 메서드 | 반환 | 설명 |
|---|---|---|
| `add_vertex(v)` | `None` | 정점 추가 |
| `neighbors(v)` | `Iterable[Vertex[V]]` | 이웃 정점 (가중치 무관) |
| `degree(v)` | `int` | 차수 |
| `_validate()` | `None` | 불변식 검증 (테스트용) |
| `show(**kwargs)` | `None` | graphviz 렌더링 |
| `render(path, **kwargs)` | `None` | 파일로 저장 |
| `to_dot()` | `str` | DOT 소스 |

속성: `directed: bool`, `vertices: list[Vertex[V]]`

### UnweightedGraph

추가 속성: `adj: dict[int, list[int]]` (vertex id → 이웃 id 리스트)

추가 메서드: `add_edge(u, v)`

### WeightedGraph

추가 속성: `adj: dict[int, list[WeightedEdge[W]]]`

추가 메서드:

- `add_edge(u, v, weight)`
- `weighted_neighbors(v) -> Iterable[tuple[Vertex[V], W]]`

```python
@dataclass(frozen=True)
class WeightedEdge[W: Weight]:
    src_id: int
    dst_id: int
    weight: W
```

## Graph 생성자 패턴

Graph 클래스는 여러 형태의 입력을 받습니다.

```python
# 빈 그래프
g = UnweightedGraph(directed=False)

# Chain에서 평가
g = UnweightedGraph(u - v - w)

# edge list에서
g = UnweightedGraph([(u, v), (v, w)])
g = WeightedGraph([(u, v, 3), (v, w, 2)])
```

### 자동 타입 추론: `Graph(chain)` 팩토리

`Graph` 베이스 클래스가 `__new__`에서 Chain 내용을 분석해 적절한 서브클래스 반환. 가중치 있으면 `WeightedGraph`, 없으면 `UnweightedGraph`. `directed`는 간선 중 하나라도 `directed_fwd`/`bidirectional`이면 `True`.

### 서브클래스 생성자

`UnweightedGraph(chain)`, `WeightedGraph(chain)`은 Chain이 자기 타입과 맞지 않으면 `TypeError`:

```python
UnweightedGraph(u - 3 - v)    # TypeError: Chain contains weighted edges
WeightedGraph(u - v)          # TypeError: Chain contains unweighted edges
```

## 렌더링: graphviz

`graphviz` PyPI 패키지로 PNG/SVG/PDF 직접 생성. 시스템에 Graphviz 실행 파일(`dot`) 필요.

```python
g.show()                      # Jupyter inline 또는 기본 viewer
g.render("out.png")
g.render("out.svg")
dot_source = g.to_dot()       # DOT 문자열만
```

### 커스터마이징

```python
g.show(
    layout="dot",             # dot, neato, fdp, sfdp, twopi, circo
    node_attrs={"shape": "circle"},
    edge_attrs={"color": "gray"},
    graph_attrs={"rankdir": "LR"},
)
```

정점·간선별 스타일:

```python
from algoforge.graph.render import VertexStyle, EdgeStyle

g.show(
    vertex_style=lambda v: VertexStyle(color="red" if v == src else "white"),
    edge_style=lambda e: EdgeStyle(width=3 if e in mst_edges else 1),
)
```

### 알고리즘 결과 시각화

각 알고리즘 결과는 `.render()`를 가짐:

```python
result = dijkstra(g, src=u)
result.render("dijkstra.svg")     # 최단 경로 트리 강조 렌더링
```

### 단계별 애니메이션

```python
from algoforge.graph.animate import animate_to_gif

animate_to_gif(dijkstra_steps(g, src=u), output="dijkstra.gif", fps=2)
```

각 프레임은 graphviz 렌더링, imageio로 합성. `imageio`는 선택 의존성.

## 구현 순서

1. `core/graph/base.py` — `Vertex`, `Graph[V]` ABC (팩토리 포함)
2. `core/graph/chain.py` — `ChainEdge`, `Chain`, 연산자 메서드
3. `core/graph/unweighted.py` — `UnweightedGraph`
4. `core/graph/weighted.py` — `Weight` 프로토콜, `WeightedGraph[V, W]`
5. `core/graph/io.py` — edge list, DOT 입출력
6. `graph/render.py` — graphviz 렌더링
7. `graph/traversal.py` — BFS, DFS
8. `graph/shortest_path.py` — Dijkstra (heap 선행)
9. `graph/mst.py` — Kruskal (union-find 선행)
10. `graph/animate.py` — 애니메이션
11. 이후 SCC, flow, matching, LCA 등

## 테스트 전략

### 불변식 검증

`Graph._validate()`:

- `directed` 플래그와 간선 구조 일치
- 모든 간선 엔드포인트가 `vertices`에 존재
- 무방향 그래프에서 `u→v`와 `v→u`가 쌍으로 존재

`Chain.validate()`:

- 방향성 혼합 없음
- 가중치 유무 혼합 없음

### Brute-force 교차검증

- Dijkstra vs Bellman-Ford
- Kruskal vs Prim (총 가중치)
- Tarjan vs Kosaraju (SCC 파티션 동등성)

### 제네릭 가중치 테스트

```python
@pytest.mark.parametrize("weight_type", [int, float, Fraction])
def test_dijkstra_generic_weights(weight_type):
    ...
```

### 타입 체크 테스트

pyrefly로 정적 오류 유도:

```python
# tests/type_errors/test_unweighted_dijkstra.py
g: UnweightedGraph = ...
dijkstra(g, src=v)            # pyrefly error: expected WeightedGraph
```

## 열린 질문

- **MatrixGraph 도입 시점**: 스펙트럴 알고리즘 필요할 때. 그전엔 `to_adjacency_matrix()` 변환 함수로 충분.
- **멀티그래프**: 현재 설계는 같은 정점 쌍에 간선 여러 개 허용. 단순 그래프 가정하는 알고리즘은 케이스별 처리.
- **하이퍼그래프**: 범위 밖.
- **Semiring 추상화**: `Weight` 프로토콜로 시작. tropical semiring 등 다루게 되면 확장 고려.

## 참고 자료

- [graaf](https://github.com/bobluppes/graaf) — 구조적 영감
- [galoisenne](https://github.com/breandan/galoisenne) — DSL·대수적 영감
- [Boost Graph Library](https://www.boost.org/doc/libs/1_82_0/libs/graph/doc/index.html) — 제네릭 그래프 라이브러리의 고전
- [NetworkX](https://networkx.org/) — 레퍼런스 API 참고
- [Python graphviz](https://graphviz.readthedocs.io/) — 렌더링 백엔드
