# Graph DSL

`core/graph`는 연산자 오버로딩 기반의 간결한 DSL을 갖춘 경량 그래프 라이브러리입니다.  
내부 구조는 [graaf](https://github.com/bobluppes/graaf)(C++) 에서, DSL 표면은 [galoisenne](https://github.com/breandan/galoisenne)(Kotlin) 에서 영감을 받았습니다.

세부 설계 문서 → [`design.md`](design.md)  
대화형 데모 → [`notebooks/graph_demo.ipynb`](../../../notebooks/graph_demo.ipynb)

---

## 빠른 시작

```python
import core.graph as g

a, b, c, d = g.vertices("a", "b", "c", "d")

# 무가중 그래프
ug = g.UnweightedGraph(a - b - c - d)

# 가중 그래프
wg = g.WeightedGraph(a - 3 - b - 7 - c)
wg[c, d] = 2          # 간선 추가/수정

# 유량 그래프
s, t = g.vertices("s", "t")
fg = g.FlowGraph(s >> 10 >> a >> 5 >> t)
```

---

## 간선 표현식

`Vertex` 연산자로 간선과 워크를 직접 표현합니다.

| 표현식 | 결과 | 방향성 |
|--------|------|--------|
| `u - v` | `Edge` | 무방향 |
| `u >> v` | `Edge` | 단방향 (u → v) |
| `u << v` | `Edge` | 단방향 (v → u) |
| `u & v` | `Edge` | 양방향 |
| `u - 3 - v` | `WeightedEdge[int]` | 무방향, 가중치 3 |
| `u >> 5 >> v` | `WeightedEdge[int]` | 단방향, 가중치 5 |

연결하면 Walk가 됩니다:

```python
a - b - c - d          # Walk (무가중, 무방향)
a >> b >> c            # Walk (단방향)
a - 3 - b - 2 - c      # WeightedWalk[int]
```

---

## 다중 간선 단축 표기

```python
# 스타 — A에서 여러 정점으로
a - [b, c, d]          # UnweightedGraph: a-b, a-c, a-d

# VertexList
g.vs(a, b) - g.vs(c, d)    # K_{2,2}: a-c, a-d, b-c, b-d
[a, b] - g.vs(c, d)        # 동일 (plain list 왼쪽 피연산자)
g.vs(a, b) - c             # a-c, b-c
```

반환값은 `UnweightedGraph`이므로 `+`, `+=`, `union` 등 그래프 연산자와 바로 결합할 수 있습니다.

---

## 패턴 생성자

```python
Graph.path(a, b, c, d)                               # 경로 (n-1개 간선)
Graph.cycle(a, b, c, d)                              # 순환 (n개 간선)
Graph.complete(a, b, c, d)                           # K_n
Graph.bipartite([a, b], [c, d])                      # K_{m,n}
Graph.star(center, a, b, c)                          # 별 (첫 인자 = center)
Graph.wheel(center, a, b, c, d)                      # 바퀴
Graph.grid(rows=3, cols=3)                           # 격자 (정점 자동 생성)
Graph.petersen()                                     # 페테르센 그래프
```

---

## 그래프 뮤테이션 연산자

| 표현식 | 동작 | 반환 |
|--------|------|------|
| `g + v` | 정점 추가 | 새 그래프 |
| `g + edge/walk` | 간선 추가 | 새 그래프 |
| `g + g2` | `union(g2)` | 새 그래프 |
| `g += v/edge/walk/g2` | in-place 버전 | `self` |
| `g - v` | 정점 제거 (인접 간선 포함) | 새 그래프 |
| `g - edge/walk` | 간선 제거 | 새 그래프 |
| `g -= v/edge/walk` | in-place 버전 | `self` |
| `g1 \| g2` | `disjoint_union(g2)` (레이블 충돌 시 ValueError) | 새 그래프 |

```python
ug = UnweightedGraph(a - b - c)

ug2 = ug + d              # 정점 d 추가된 새 그래프
ug3 = ug + (c - d)        # 간선 c-d 추가된 새 그래프
ug4 = ug - b              # 정점 b와 인접 간선 제거
ug5 = ug - (a - b)        # 간선 a-b 제거

ug += d                   # in-place: 정점 d 추가
ug -= b                   # in-place: 정점 b 제거
```

---

## 단항 연산자

```python
~g    # 여그래프 (UnweightedGraph 전용): 없는 간선↔있는 간선 교환
-g    # 역방향 그래프 (DIRECTED 전용): 모든 간선 방향 반전
```

---

## 인덱싱

```python
g[v]        # neighbors(v) 단축 → list[Vertex]
g[u, v]     # get_edge(u, v) 단축 → Edge / WeightedEdge / FlowEdge

# WeightedGraph 전용
wg[u, v] = 5          # set_edge: 간선 추가 또는 가중치 수정

# FlowGraph 전용
fg[u, v] = 10         # set_capacity: 용량 설정
```

---

## Walk 계층

```
Walk            정점·간선 중복 허용
 └── Trail      간선 중복 없음
      └── Path  정점·간선 중복 없음
WeightedWalk    가중 버전
```

알고리즘 반환 타입이 의미를 가집니다:

```python
dijkstra(g, src, dst)    # → Path
euler_circuit(g)         # → Trail
dfs_walk(g, src)         # → Walk
```

---

## 그래프 타입

| 타입 | 간선 | 특징 |
|------|------|------|
| `UnweightedGraph` | `Edge` | 기본 그래프, `complement()` / `~g` 지원 |
| `WeightedGraph[W]` | `WeightedEdge[W]` | `dijkstra`, `kruskal` 등에 사용 |
| `FlowGraph[W]` | `FlowEdge[W]` | 항상 `DIRECTED`, 역방향 간선 자동 관리 |

`Graph` 팩토리가 워크 타입으로 구현체를 자동 추론합니다:

```python
Graph(a - b - c)                   # → UnweightedGraph
Graph(a - 3 - b - 2 - c)          # → WeightedGraph[int]
Graph(a >> 10 >> b, flow=True)     # → FlowGraph[int]
```

---

## I/O

모든 그래프 타입에서 공통으로 지원합니다:

```python
g.to_edge_list()   / Graph.from_edge_list(edges)
g.to_dot()         / Graph.from_dot(dot_str)
g.to_json()        / Graph.from_json(json_str)
g.to_adjacency_matrix()  / Graph.from_adjacency_matrix(m, labels)
g.A                # to_adjacency_matrix() 단축
```

---

## 렌더링

```python
g.show()                     # Graphviz PDF/SVG/PNG 뷰어
g._repr_svg_()               # Jupyter 인라인 SVG 자동 호출
```
