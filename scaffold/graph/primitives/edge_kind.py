from enum import Enum


class EdgeKind(Enum):
    """간선의 방향성 종류를 나타내는 열거형.

    Attributes:
        UNDIRECTED: 무방향 간선. 양쪽 방향 모두 이동 가능. 기호: ``-``
        DIRECTED: 단방향 간선. 출발지 → 도착지 방향만 이동 가능. 기호: ``→``
        BIDIRECTED: 양방향 간선. 두 방향을 명시적으로 모두 표현. 기호: ``↔``
    """

    UNDIRECTED = "-"
    DIRECTED = "→"
    BIDIRECTED = "↔"
