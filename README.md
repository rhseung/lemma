# lemma

## 소개

lemma는 자료구조와 알고리즘을 밑바닥부터 직접 구현하는 개인 학습 프로젝트입니다. C++ STL에 대응하는 컨테이너들을 Python으로 짜고, 그 위에 그래프·문자열·기하·정수론 등의 알고리즘을 쌓아 올립니다. `collections.deque`, `heapq`, `networkx` 같은 표준 라이브러리는 쓰지 않습니다. 목표는 이 구조들이 _왜_ 이렇게 생겼는지 이해하는 것입니다.

## 구현 우선순위 (AI2000 수업 기준)

AI2000 자료구조 및 알고리즘 강의(Prof. Mansu Kim) 커리큘럼에 맞춰 구현 순서를 정한다.
수업 전체 범위를 먼저, 그 외 심화 내용을 이후에 구현한다.

### 🔴 Priority 1 — 수업 전체 범위

강의·과제·Reading 자료를 포함한 수업 범위 전체다.

| 주차 | 구현 대상 | 파일 경로 | 상태 |
|------|-----------|-----------|------|
| W2 | **Dynamic Array** — append, insert, remove, resize | `core/containers/dynamic_array.py` | 🔲 |
| W3 | **Stack** — push, pop, peek (배열 기반) | `core/containers/stack.py` | 🔲 |
| W3 | **Queue** — enqueue, dequeue, peek (배열/연결 리스트 기반) | `core/containers/queue.py` | 🔲 |
| W3 | **Deque** — push/pop front & back | `core/containers/deque.py` | 🔲 |
| W4 | **Singly Linked List** — insert, delete, search, traversal | `core/containers/linked_list.py` | 🔲 |
| W4 | **Doubly Linked List** — 양방향 insert/delete/traversal | `core/containers/linked_list.py` | 🔲 |
| W4 | **Circular Doubly Linked List** | `core/containers/linked_list.py` | 🔲 |
| W6 | **Hash Table** — chaining + open addressing (probing), insert/delete/search | `core/containers/hash_map.py` | 🔲 |
| W7 | **Binary Search Tree (BST)** — insert, delete, search, min/max | `core/trees/bst.py` | 🔲 |
| W7 | **BST Traversal (반복 버전)** — 재귀 버전과 비교 | `core/trees/bst.py` | 🔲 |
| W7 | **Min-Heap** — insert (sift-up), extract-min (sift-down), heapify | `core/heaps/binary_heap.py` | 🔲 |
| W7 | **Priority Queue (Heap 기반)** | `core/heaps/binary_heap.py` | 🔲 |
| W9 | **Selection Sort** | `algorithms/sorting/sorts.py` | 🔲 |
| W9 | **Insertion Sort** | `algorithms/sorting/sorts.py` | 🔲 |
| W9 | **Bubble Sort** | `algorithms/sorting/sorts.py` | 🔲 |
| W9 | **Quick Sort** | `algorithms/sorting/sorts.py` | 🔲 |
| W9 | **Merge Sort** | `algorithms/sorting/sorts.py` | 🔲 |
| W9 | **Binary Search** | `algorithms/sorting/binary_search.py` | 🔲 |
| W10 | **Graph** — adjacency list/matrix, add/remove vertex & edge | `core/graph/` | ✅ |
| W10 | **DFS** — 재귀 / 스택 기반 | `algorithms/graph/dfs.py` | ✅ |
| W10 | **BFS** — 큐 기반 | `algorithms/graph/bfs.py` | ✅ |

### 🟢 Priority 2 — lemma 자체 목표 (방학/여유 시간)

수업 범위 밖의 심화 구현. 경쟁 프로그래밍 및 CS 이론 학습 목적이다.

- **균형 트리**: RB 트리, AVL 트리, 트립, 스플레이 트리, 스킵 리스트
- **고급 힙**: 페어링 힙, 좌편향 힙, 피보나치 힙
- **기타 자료구조**: Union-Find, Fenwick 트리, 세그먼트 트리, 트라이
- **그래프 알고리즘**: Dijkstra, Bellman-Ford, Floyd-Warshall, Kruskal, Prim, SCC, 최대 유량
- **문자열**: KMP, Z-알고리즘, Aho-Corasick, 접미사 배열, Manacher
- **계산 기하**: 볼록 껍질, 최근접 점쌍, 선분 교차, CCW
- **정수론**: 소수 체, 모듈러 산술, 빠른 거듭제곱, 확장 유클리드
- **동적 계획법**: LIS, 배낭, 편집 거리, CHT, 분할 정복 DP, 비트마스크 DP
- **선형대수**: 행렬 거듭제곱, 가우스 소거
- **조합론**: 이항 계수, 순열, 포함-배제 원리

## 범위

- **자료구조**
  - STL 스타일 컨테이너: 동적 배열, 덱, 연결 리스트, 해시 맵
  - 균형 트리: RB 트리, AVL 트리, 트립, 스플레이 트리, 스킵 리스트
  - 힙: 이진 힙, 페어링 힙, 좌편향 힙, 피보나치 힙
  - 기타: 유니온 파인드, 펜윅 트리, 세그먼트 트리, 트라이
  - 그래프: 간결한 DSL을 갖춘 경량 그래프 추상화 (Walk, Graph, FlowGraph). DSL 문법은 [`core/graph/README.md`](core/graph/README.md), 세부 설계는 [`core/graph/design.md`](core/graph/design.md) 참고.
- **알고리즘**
  - 그래프: BFS/DFS, 최단 경로(Dijkstra, Bellman-Ford, Floyd-Warshall), MST(Kruskal, Prim), SCC, 최대 유량, 이분 매칭
  - 문자열: KMP, Z-알고리즘, Aho-Corasick, 접미사 배열, Manacher
  - 계산 기하: 볼록 껍질, 최근접 점쌍, 선분 교차, CCW
  - 정수론: 소수 체, 모듈러 산술, 빠른 거듭제곱, 확장 유클리드
  - 동적 계획법: LIS, 배낭, 편집 거리, CHT, 분할 정복 DP, 비트마스크 DP
  - 정렬 / 탐색: 비교 기반 정렬, 비비교 기반 정렬, 이분 탐색 변형
  - 조합론: 이항 계수, 순열, 포함-배제 원리
  - 선형대수: 행렬 거듭제곱, 가우스 소거

## 프로젝트 구조

```
lemma/
├── core/                               # 자료구조 (알고리즘 의존 없음)
│   ├── graph/                          # Walk, Graph, FlowGraph, DSL
│   ├── containers/                     # STL 스타일 컨테이너 (동적 배열, 덱, 연결 리스트, 해시 맵)
│   ├── trees/                          # 균형 BST (RB, AVL, 트립, 스플레이, 스킵 리스트)
│   ├── heaps/                          # 힙 (이진, 페어링, 좌편향, 피보나치)
│   ├── union_find.py
│   ├── fenwick.py
│   ├── segment_tree.py
│   └── trie.py
├── algorithms/                         # 알고리즘 (core를 import할 수 있음)
│   ├── graph/                          # 그래프 알고리즘
│   │   ├── traversal.py                # BFS, DFS
│   │   ├── shortest_path.py            # Dijkstra, Bellman-Ford, Floyd-Warshall
│   │   ├── mst.py                      # Kruskal, Prim
│   │   ├── scc.py                      # Tarjan, Kosaraju
│   │   ├── flow.py                     # Ford-Fulkerson, Dinic
│   │   └── matching.py                 # 이분 매칭, 헝가리안
│   ├── string/                         # 문자열 알고리즘
│   │   ├── kmp.py
│   │   ├── z.py
│   │   ├── aho_corasick.py
│   │   ├── suffix_array.py
│   │   └── manacher.py
│   ├── geometry/                       # 계산 기하
│   │   ├── convex_hull.py
│   │   ├── closest_pair.py
│   │   └── segment.py                  # 선분 교차, CCW
│   ├── number_theory/                  # 정수론
│   │   ├── sieve.py
│   │   ├── modular.py                  # 모듈러 산술, 확장 유클리드
│   │   └── fast_pow.py
│   ├── dp/                             # 동적 계획법 패턴
│   │   ├── lis.py
│   │   ├── knapsack.py
│   │   ├── edit_distance.py
│   │   └── cht.py                      # Convex Hull Trick, 분할 정복 DP
│   ├── sorting/                        # 정렬 / 이분 탐색
│   │   ├── sorts.py                    # 비교·비비교 기반 정렬
│   │   └── binary_search.py
│   ├── combinatorics/                  # 조합론
│   │   └── combinatorics.py            # 이항 계수, 순열, 포함-배제
│   └── linalg/                         # 선형대수
│       └── matrix.py                   # 행렬 거듭제곱, 가우스 소거
├── tests/                              # pytest, brute-force 교차검증 포함
├── notebooks/                          # 데모 노트북
└── benchmarks/                         # CPython vs 표준 라이브러리
```

설계 원칙:

- `core/`에는 알고리즘을 모르는 순수 자료구조만 둡니다.
- 알고리즘 레이어(`algorithms/graph`, `algorithms/string` 등)는 `core/`를 import할 수 있지만, 알고리즘 레이어끼리는 서로 참조하지 않습니다.
- 알고리즘은 메서드가 아닌 함수로 구현합니다. `g.dijkstra(src)`가 아니라 `dijkstra(g, src)`. 편의를 위해 `Graph`에 얇은 메서드 래퍼를 제공합니다.
- 렌더링과 애니메이션은 알고리즘 로직과 분리됩니다. 단계별 시각화가 필요한 알고리즘은 제너레이터 버전(예: `dijkstra_steps`)을 따로 제공합니다.

## 도구 체계

이 프로젝트는 Rust 기반의 최신 파이썬 툴체인을 사용합니다.

- [**uv**](https://github.com/astral-sh/uv) — 의존성 및 가상환경 관리
- [**ruff**](https://github.com/astral-sh/ruff) — 린터 및 포매터 (flake8, black, isort, pyupgrade 대체)
- [**pyrefly**](https://pyrefly.org/) — 정적 타입 체커 (Meta)
- [**pytest**](https://docs.pytest.org/) — 테스트

런타임 타입 분기는 Python 3.10+의 `match` 문으로 처리합니다. `isinstance` 사슬 대신 구조적 패턴 매칭을 사용해 DSL 코드의 가독성을 유지합니다.

## 설치

```bash
# uv 설치 (없으면)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 클론 및 환경 구성
git clone <repo-url>
cd lemma
uv sync
```

## 개발

```bash
uv run ruff check .              # 린트
uv run ruff check --fix .        # 자동 수정 가능한 부분 수정
uv run ruff format .             # 포맷
uv run pyrefly check             # 타입 체크
uv run pytest                    # 테스트 실행
uv run pytest --cov=core --cov=algorithms  # 커버리지 포함
```

## 테스트 철학

모든 사소하지 않은 구조는 두 종류의 테스트와 함께 제공됩니다.

1. **불변식 검증자(invariant validator).** RB 트리 같은 구조는 내부 불변식(black height 동일, red-red 간선 없음, BST 속성 등)을 검사하는 `_validate()` 메서드를 노출합니다. 모든 테스트 끝에 호출합니다.
2. **Brute-force 교차검증.** 알고리즘 출력을 랜덤 입력에 대해 나이브 참조 구현과 비교합니다. Dijkstra를 Bellman-Ford와, 세그먼트 트리를 일반 배열과, 해시 맵을 `dict`와 비교하는 식입니다. 수백 번의 랜덤 시행이면 대부분의 버그가 잡힙니다.

## 성능에 관하여

이 라이브러리는 가독성을 위해 CPython으로 작성되었습니다. 기본 컨테이너(예: `DynamicArray`)의 순수 파이썬 구현은 C로 구현된 CPython 내장 `list`보다 항상 느립니다. 이는 예상된 결과이며 괜찮습니다.

`benchmarks/`의 벤치마크는 참고를 위해 CPython과 PyPy 수행 시간을 표준 라이브러리와 함께 보고합니다. 보통 PyPy는 코드 수정 없이도 대부분의 성능 격차를 메웁니다.

## 참고 문헌

이 라이브러리를 만들면서 참조한 자료들입니다.

- Cormen, Leiserson, Rivest, Stein. _Introduction to Algorithms_ (CLRS).
- Sedgewick, Wayne. _Algorithms_.
- [cp-algorithms](https://cp-algorithms.com/) — 경쟁 프로그래밍 레퍼런스.
- [KACTL](https://github.com/kth-competitive-programming/kactl) — KTH 알고리즘 라이브러리.
- [graaf](https://github.com/bobluppes/graaf) — C++ 그래프 라이브러리 (구조적 영감).
- [galoisenne](https://github.com/breandan/galoisenne) — Kotlin 대수적 그래프 라이브러리 (DSL 영감).

## 라이선스

MIT.
