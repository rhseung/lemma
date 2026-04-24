# algoforge

## 소개

algoforge는 고전적인 자료구조와 알고리즘을 처음부터 직접 구현해보는 개인 프로젝트입니다. 모든 컨테이너, 트리, 힙, 그래프 알고리즘을 손으로 짭니다. `collections.deque`, `heapq`, `networkx` 같은 건 쓰지 않습니다. 목표는 표준 라이브러리를 이기는 게 아니라, 이 구조들이 *왜* 이렇게 생겼는지 이해하는 것입니다.

프로덕션용 성능이 필요하다면 표준 라이브러리나 `sortedcontainers`를 쓰세요. 이 레포는 내부 동작을 투명하게 보여주기 위해 존재합니다.

## 범위

- **핵심 자료구조**: STL 스타일 컨테이너(동적 배열, 덱, 연결 리스트, 해시 맵), 균형 트리(RB, AVL, 트립, 스플레이, 스킵 리스트), 힙(이진, 페어링, 좌편향, 피보나치), 고전 구조(유니온 파인드, 펜윅 트리, 세그먼트 트리, 트라이).
- **그래프 라이브러리**: 간결한 DSL을 갖춘 경량 그래프 추상화. 세부 설계는 [`notes/graph/design.md`](notes/graph/design.md) 참고.
- **알고리즘**: 그래프 알고리즘, 문자열 알고리즘, 계산 기하, 정수론, 고전 DP 패턴.
- **시각화**: 그래프 렌더링과 알고리즘 단계별 애니메이션.

## 프로젝트 구조

```
algoforge/
├── README.md
├── pyproject.toml
├── pyrefly.toml
├── algoforge/
│   ├── core/                       # 자료구조
│   │   ├── containers/             # STL 스타일 컨테이너
│   │   ├── trees/                  # 균형 BST
│   │   ├── heaps/
│   │   ├── graph/                  # Graph, FlowGraph (자료구조만)
│   │   ├── union_find.py
│   │   ├── fenwick.py
│   │   ├── segment_tree.py
│   │   └── trie.py
│   ├── graph/                      # 그래프 이론 알고리즘
│   │   ├── traversal.py
│   │   ├── shortest_path.py
│   │   ├── mst.py
│   │   ├── scc.py
│   │   ├── flow.py
│   │   ├── matching.py
│   │   ├── layout.py
│   │   ├── render.py
│   │   └── animate.py
│   ├── string/
│   ├── geometry/
│   ├── number_theory/
│   └── dp/
├── notes/                          # 마크다운 노트 (소스와 1:1 대응)
├── tests/                          # pytest, brute-force 교차검증 포함
├── benchmarks/                     # CPython vs PyPy vs 표준 라이브러리
└── examples/                       # 시각화 노트북
```

설계 원칙:

- `core/`에는 알고리즘을 모르는 순수 자료구조만 둡니다.
- 알고리즘 레이어(`graph/`, `string/` 등)는 `core/`를 import할 수 있지만, 알고리즘 레이어끼리는 서로 참조하지 않습니다.
- 알고리즘은 메서드가 아닌 함수로 구현합니다. `g.dijkstra(src)`가 아니라 `dijkstra(g, src)`. 편의를 위해 `Graph`에 얇은 메서드 래퍼를 제공합니다.
- 렌더링과 애니메이션은 알고리즘 로직과 분리됩니다. 단계별 시각화가 필요한 알고리즘은 제너레이터 버전(예: `dijkstra_steps`)을 따로 제공합니다.

## 주제 × 패러다임 인덱스

| | 분할 정복 | 동적 계획법 | 탐욕법 | 그래프 순회 |
|---|---|---|---|---|
| 그래프 | — | Floyd-Warshall | Kruskal, Prim | BFS, DFS, Dijkstra |
| 문자열 | — | Edit distance | — | Aho-Corasick |
| 기하 | 최근접 점쌍, 볼록 껍질 | — | — | — |
| DP | — | LIS, Knapsack, CHT | — | — |

(구현이 추가될 때마다 칸을 채워 나갑니다.)

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
cd algoforge
uv sync
```

## 개발

```bash
uv run ruff check .              # 린트
uv run ruff check --fix .        # 자동 수정 가능한 부분 수정
uv run ruff format .             # 포맷
uv run pyrefly check             # 타입 체크
uv run pytest                    # 테스트 실행
uv run pytest --cov=algoforge    # 커버리지 포함
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

- Cormen, Leiserson, Rivest, Stein. *Introduction to Algorithms* (CLRS).
- Sedgewick, Wayne. *Algorithms*.
- [cp-algorithms](https://cp-algorithms.com/) — 경쟁 프로그래밍 레퍼런스.
- [KACTL](https://github.com/kth-competitive-programming/kactl) — KTH 알고리즘 라이브러리.
- [graaf](https://github.com/bobluppes/graaf) — C++ 그래프 라이브러리 (구조적 영감).
- [galoisenne](https://github.com/breandan/galoisenne) — Kotlin 대수적 그래프 라이브러리 (DSL 영감).

## 라이선스

MIT.
