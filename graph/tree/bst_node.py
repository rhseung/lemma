from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, Self


class _Comparable(Protocol):
    def __lt__(self, value: Self, /) -> bool: ...
    def __gt__(self, value: Self, /) -> bool: ...


@dataclass
class BSTNode[T: _Comparable]:
    key: T
    left: BSTNode[T] | None = None
    right: BSTNode[T] | None = None


class BST[T: _Comparable]:
    """중복 키를 허용하지 않는 Set 의미의 이진 탐색 트리.

    불변식:
        모든 노드 n에 대해
            left subtree의 모든 키 < n.key < right subtree의 모든 키

    비교 규약 (search/insert/delete 가 전부 동일하게 따른다):
        node.key < key  → 오른쪽으로
        node.key > key  → 왼쪽으로
        그 외 (else)     → 같은 키 (== 를 직접 쓰지 않고 else 로 잡는다)

    에러 계약:
        - 없는 키 조회/삭제 → KeyError   ("키 없음")
        - 중복 키 삽입       → ValueError ("키 충돌")

    재귀형과 반복형을 둘 다 구현한다. 동일 계약을 따르므로
    어느 쪽을 호출하든 외부 동작은 같아야 한다.
    """

    def __init__(self) -> None:
        self._root: BSTNode[T] | None = None

    # ── search ─────────────────────────────────────────────
    def search_recursive(self, key: T) -> BSTNode[T]:
        """재귀형. 없으면 KeyError. _root 가 None 인 경우도 처리."""
        return self._search(self._root, key)

    def _search(self, node: BSTNode[T] | None, key: T) -> BSTNode[T]:
        """재귀 헬퍼. 진행할 방향의 자식이 없으면 KeyError."""
        if node is None:
            raise KeyError("키 없음")

        if node.key < key:
            return self._search(node.right, key)
        if node.key > key:
            return self._search(node.left, key)
        return node

    def search_iterative(self, key: T) -> BSTNode[T]:
        """반복형. node 를 루트부터 한쪽으로 내리는 while 루프.
        루프가 None 으로 떨어지면 → 키 없음 → KeyError.
        """
        node = self._root
        while node is not None:
            if node.key < key:
                node = node.right
            elif node.key > key:
                node = node.left
            else:
                return node

        raise KeyError("키 없음")

    # ── insert ─────────────────────────────────────────────
    def insert_recursive(self, key: T) -> None:
        """재귀형. 이미 존재하면 ValueError. _root 가 None 이면 루트 생성."""
        if self._root is None:
            self._root = BSTNode(key)
        else:
            self._insert(self._root, key)

    def _insert(self, node: BSTNode[T], key: T) -> None:
        """재귀 헬퍼. 가야 할 방향 자식이 None 이면 거기에 매단다.
        같은 키를 만나면 ValueError.
        """
        if node.key < key:
            if node.right is None:
                node.right = BSTNode(key)
                return
            self._insert(node.right, key)
        elif node.key > key:
            if node.left is None:
                node.left = BSTNode(key)
                return
            self._insert(node.left, key)
        else:
            raise ValueError(f"키 충돌 {key=}")

    def insert_iterative(self, key: T) -> None:
        """반복형. _root 가 None 이면 루트 생성.
        아니면 node 를 내리며 None 인 변을 찾아 새 노드를 매단다.
        도중에 같은 키 → ValueError.
        """
        if self._root is None:
            self._root = BSTNode(key)
            return

        node = self._root
        while (
            node is not None
        ):  # pragma: no branch  # node는 항상 break/raise로 빠짐 (None 도달 불가)
            if node.key < key:
                if node.right is None:
                    node.right = BSTNode(key)
                    break
                node = node.right
            elif node.key > key:
                if node.left is None:
                    node.left = BSTNode(key)
                    break
                node = node.left
            else:
                raise ValueError(f"키 충돌 {key=}")

    # ── delete ─────────────────────────────────────────────
    def delete_recursive(self, key: T) -> None:
        """재귀형. 없으면 KeyError. _root = self._delete(self._root, key)."""
        self._root = self._delete(self._root, key)

    def _delete(self, node: BSTNode[T] | None, key: T) -> BSTNode[T] | None:
        """재귀 헬퍼. 수정된 서브트리 루트를 반환하면 부모가 다시 연결한다
        (반환값 재연결이 부모 포인터 역할을 대신함).

        대상 노드를 찾으면 자식 수로 분기:
        - 0/1개 : 떼어내거나 자식으로 대체.
        - 2개   : inorder successor(오른쪽 서브트리 최솟값)의 key 를 복사한 뒤,
                  그 successor 를 node.right 에서부터 삭제 (cur 자체에서
                  시작하면 부모 링크가 끊기므로 금지).
        """
        if node is None:
            raise KeyError("키 없음")

        if node.key < key:
            node.right = self._delete(node.right, key)
        elif node.key > key:
            node.left = self._delete(node.left, key)
        else:
            # Case 1: no children
            if node.left is None and node.right is None:
                return None

            # Case 2: single children
            if node.right is None:
                return node.left
            if node.left is None:
                return node.right

            # Case 3: double children - i'll choose right subtree's minimum
            cur = node.right
            while cur.left is not None:
                cur = cur.left

            node.key = cur.key
            node.right = self._delete(node.right, cur.key)  # should be case 1 or 2

        return node

    def _replace_child(self, parent: BSTNode[T] | None, key: T, value: BSTNode[T] | None):
        if parent is None:
            self._root = value
            return

        if parent.left is not None and parent.left.key == key:
            parent.left = value
        elif parent.right is not None and parent.right.key == key:
            parent.right = value

    def delete_iterative(self, key: T) -> None:
        """반복형. parent 와 '어느 쪽 자식인지'를 손으로 추적해야 한다.
        대상을 찾으면:
        - 0/1개 : parent 의 해당 자식 링크를 교체 (대상이 루트면 _root 갱신).
        - 2개   : successor 와 그 부모를 찾아 key 복사 후 successor 를 떼어냄.
        재귀가 공짜로 해주던 부모 추적을 직접 한다.
        """
        node = self._root
        parent = None

        while node is not None:
            if node.key < key:
                parent = node
                node = node.right
            elif node.key > key:
                parent = node
                node = node.left
            else:
                # Case 1: no children
                if node.left is None and node.right is None:
                    self._replace_child(parent, key, None)
                    return

                # Case 2: single children
                if node.left is None:
                    self._replace_child(parent, key, node.right)
                    return
                if node.right is None:
                    self._replace_child(parent, key, node.left)
                    return

                # Case 3: double children
                cur = node.right
                succ_parent = node
                while cur.left is not None:
                    succ_parent = cur
                    cur = cur.left

                node.key = cur.key
                # cur은 left는 무조건 없고 right는 존재할 수도 있다.
                self._replace_child(succ_parent, cur.key, cur.right)
                return

        raise KeyError("키 없음")

    # ── traversal ──────────────────────────────────────────
    def preorder(self) -> Iterator[T]:
        """root → left → right."""
        yield from self._preorder(self._root)

    def inorder(self) -> Iterator[T]:
        """left → root → right. BST 에서는 오름차순."""
        yield from self._inorder(self._root)

    def postorder(self) -> Iterator[T]:
        """left → right → root."""
        yield from self._postorder(self._root)

    def _preorder(self, node: BSTNode[T] | None) -> Iterator[T]:
        """재귀 헬퍼 (yield from)."""
        if node is not None:
            yield node.key
            yield from self._preorder(node.left)
            yield from self._preorder(node.right)

    def _inorder(self, node: BSTNode[T] | None) -> Iterator[T]:
        """재귀 헬퍼 (yield from)."""
        if node is not None:
            yield from self._inorder(node.left)
            yield node.key
            yield from self._inorder(node.right)

    def _postorder(self, node: BSTNode[T] | None) -> Iterator[T]:
        """재귀 헬퍼 (yield from)."""
        if node is not None:
            yield from self._postorder(node.left)
            yield from self._postorder(node.right)
            yield node.key


if __name__ == "__main__":
    from scaffold.tree import Tree  # BST 본체는 scaffold 와 무관 — 데모에서만 사용

    bst = BST[int]()
    for key in [50, 30, 70, 20, 40, 60, 80]:
        bst.insert_recursive(key)

    def show(step: str) -> None:
        print(f"\n[{step}]")
        print(Tree.from_root(bst._root, left="left", right="right", label="key"))
        print("inorder:", list(bst.inorder()))

    show("insert 50, 30, 70, 20, 40, 60, 80")

    print("\npreorder :", list(bst.preorder()))
    print("postorder:", list(bst.postorder()))
    print("search_iterative(40):", bst.search_iterative(40))

    bst.delete_recursive(30)
    show("delete_recursive(30)  # 자식 2개 → 후계자 40")

    bst.delete_recursive(50)
    show("delete_recursive(50)  # 루트(자식 2개) → 후계자 60")
