# lemma

## 소개

`lemma`는 자료구조와 알고리즘을 직접 구현하면서 동작 원리와 복잡도를 익히는 개인 학습 프로젝트입니다.

표준 라이브러리의 고수준 컨테이너나 알고리즘을 바로 가져다 쓰기보다, 동적 배열, 연결 리스트, 덱, 그래프 탐색, 정렬 같은 기본 구조를 Python으로 직접 구현합니다. 목표는 "무엇을 쓰는가"보다 "왜 그렇게 동작하는가"를 이해하는 것입니다.

## 구조

코드는 주제별 최상위 패키지로 나뉘어 있습니다.

```text
lemma/
├── sequential/                 # 선형 자료구조
├── sorting/                    # 비교 기반 정렬
├── graph/                      # 그래프 알고리즘 예제
├── sets/                       # 집합 계열 자료구조
├── map/                        # 맵 계열 자료구조 자리
├── scaffold/                   # 그래프 DSL, 테스트/시각화 보조 인프라
│   ├── graph/                  # 그래프 표현, DSL, I/O
│   ├── trace/                  # 알고리즘 실행 추적 이벤트
│   └── sort_tester             # 정렬 검증 및 벤치마크 보조 도구
└── notebooks/                  # 학습용 노트북
```

## 영역

### Sequential

선형 자료구조를 둡니다. 동적 배열, 연결 리스트, 덱, 큐, 스택처럼 원소의 순서가 핵심인 구조가 여기에 속합니다.

### Sorting

정렬 알고리즘을 둡니다. 제자리 정렬과 반환형 정렬을 모두 실험할 수 있게 열어 둡니다.

### Graph

그래프 탐색, 최단 경로, MST 같은 그래프 알고리즘을 둡니다.

### Map

맵 계열 자료구조를 둡니다. 해시 테이블처럼 세부 전략이 나뉘는 구조는 하위 폴더를 만들고, 각 전략도 구현 단위 폴더로 분리합니다.
해시 테이블은 충돌 해결 패러다임을 먼저 나누고, open addressing 안에서 probing 전략과 delete 전략을 다시 나눕니다.
probing 전략과 delete 전략이 독립적인 경우에는 mixin과 조합 클래스로 표현합니다.

### Scaffold

알고리즘 구현을 돕는 보조 인프라를 둡니다. 그래프 DSL, trace 이벤트, 정렬 검증기처럼 여러 실험에서 재사용되는 코드가 여기에 속합니다.

## 설계 원칙

- 자료구조는 가능한 한 작은 공개 API부터 구현합니다.
- 시험 대비용 구현에는 시간복잡도와 핵심 불변식을 docstring에 적습니다.
- 테스트는 공개 API의 동작을 먼저 검증하고, 필요할 때 내부 불변식도 확인합니다.
- 그래프 DSL처럼 순환 의존이 강한 코드는 일부 local import를 허용합니다.
- 알고리즘은 자료구조 메서드에 억지로 붙이기보다, 별도 함수로 두는 방향을 선호합니다.
- 패키지의 `__init__`는 re-export만 맡기고, 실제 구현은 이름이 있는 모듈에 둡니다.

## 도구

이 프로젝트는 `uv` 기반으로 실행합니다.

```bash
uv sync
```

자주 쓰는 명령:

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
uv run pyrefly check
```

## 테스트

주요 자료구조와 그래프 DSL에는 pytest 테스트가 있습니다.
테스트는 구현과 같은 폴더에 `*_test` 형태로 둡니다.
구현 하나를 독립적으로 실행하고 싶으면 해당 구현 폴더를 pytest 대상으로 넘깁니다.

```text
some_structure/
├── __init__
├── __main__
└── some_structure_test
```

아직 main 예제가 없는 구현은 `__main__` 없이 시작해도 됩니다.

```bash
uv run pytest some/package/some_structure
uv run python -m some.package.some_structure
```

자료구조 테스트는 주로 다음을 확인합니다.

- 빈 상태
- 삽입과 삭제
- 앞/뒤 접근
- 경계 조건
- 연속 연산 후 순서 유지
- 예외 발생

## 확장 후보

- Stack
- Queue
- Hash Table
- Binary Search Tree
- Heap / Priority Queue
- Binary Search
- 더 많은 그래프 알고리즘

## 참고

- Cormen, Leiserson, Rivest, Stein. _Introduction to Algorithms_.
- Sedgewick, Wayne. _Algorithms_.
- [cp-algorithms](https://cp-algorithms.com/)
- [KACTL](https://github.com/kth-competitive-programming/kactl)

## 라이선스

MIT.
