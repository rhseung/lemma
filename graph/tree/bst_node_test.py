import types

import pytest

from graph.tree.bst_node import BST, BSTNode

VARIANTS = ["recursive", "iterative"]


@pytest.fixture(params=VARIANTS)
def variant(request) -> str:
    return request.param


def _insert(bst: BST[int], variant: str, key: int) -> None:
    getattr(bst, f"insert_{variant}")(key)


def _search(bst: BST[int], variant: str, key: int):
    return getattr(bst, f"search_{variant}")(key)


def _delete(bst: BST[int], variant: str, key: int) -> None:
    getattr(bst, f"delete_{variant}")(key)


def _build(variant: str, keys: list[int]) -> BST[int]:
    bst = BST[int]()
    for k in keys:
        _insert(bst, variant, k)
    return bst


# 트리 모양:
#         50
#        /  \
#      30    70
#     / \    / \
#    20 40  60 80
FULL = [50, 30, 70, 20, 40, 60, 80]


class TestInsert:
    def test_into_empty_sets_root(self, variant: str):
        bst = BST[int]()

        _insert(bst, variant, 50)

        root = bst._root
        assert root is not None
        assert root.key == 50

    def test_places_smaller_left_larger_right(self, variant: str):
        bst = _build(variant, [50, 30, 70])

        root = bst._root
        assert root is not None
        assert root.left is not None and root.right is not None
        assert root.key == 50
        assert root.left.key == 30
        assert root.right.key == 70

    def test_builds_sorted_inorder(self, variant: str):
        bst = _build(variant, FULL)

        assert list(bst.inorder()) == [20, 30, 40, 50, 60, 70, 80]

    def test_duplicate_raises_value_error(self, variant: str):
        bst = _build(variant, [50, 30])

        with pytest.raises(ValueError):
            _insert(bst, variant, 30)

    def test_skewed_chain(self, variant: str):
        bst = _build(variant, [10, 20, 30, 40])

        assert list(bst.inorder()) == [10, 20, 30, 40]
        # 오름차순 삽입 → 오른쪽으로만 자라는 사슬
        root = bst._root
        assert root is not None and root.right is not None and root.right.right is not None
        assert root.key == 10
        assert root.right.key == 20
        assert root.right.right.key == 30


class TestSearch:
    def test_empty_tree_raises(self, variant: str):
        bst = BST[int]()

        with pytest.raises(KeyError):
            _search(bst, variant, 1)

    def test_finds_every_key(self, variant: str):
        bst = _build(variant, FULL)

        for k in FULL:
            assert _search(bst, variant, k).key == k

    def test_returns_node(self, variant: str):
        bst = _build(variant, [50, 30, 70])

        node = _search(bst, variant, 30)

        assert isinstance(node, BSTNode)
        assert node.key == 30

    def test_missing_raises(self, variant: str):
        bst = _build(variant, [50, 30, 70])

        with pytest.raises(KeyError):
            _search(bst, variant, 25)  # 왼쪽 끝까지 갔다가 없음
        with pytest.raises(KeyError):
            _search(bst, variant, 999)  # 오른쪽 끝까지 갔다가 없음


class TestDelete:
    def test_leaf(self, variant: str):  # 자식 0개
        bst = _build(variant, FULL)

        _delete(bst, variant, 20)

        assert list(bst.inorder()) == [30, 40, 50, 60, 70, 80]
        with pytest.raises(KeyError):
            _search(bst, variant, 20)

    def test_node_with_one_child(self, variant: str):  # 자식 1개
        bst = _build(variant, [50, 30, 70, 60])  # 70 은 왼쪽 자식 60 만

        _delete(bst, variant, 70)

        assert list(bst.inorder()) == [30, 50, 60]
        with pytest.raises(KeyError):
            _search(bst, variant, 70)

    def test_node_with_two_children(self, variant: str):  # 자식 2개
        bst = _build(variant, FULL)

        _delete(bst, variant, 30)  # 후계자 40

        assert list(bst.inorder()) == [20, 40, 50, 60, 70, 80]
        with pytest.raises(KeyError):
            _search(bst, variant, 30)

    def test_root_with_two_children(self, variant: str):
        bst = _build(variant, FULL)

        _delete(bst, variant, 50)  # 후계자 60

        assert list(bst.inorder()) == [20, 30, 40, 60, 70, 80]
        with pytest.raises(KeyError):
            _search(bst, variant, 50)

    def test_successor_with_right_child_is_preserved(self, variant: str):
        # 50 삭제 → 후계자 60, 그런데 60 은 오른쪽 자식 65 를 가짐 → 65 가 살아남아야
        bst = _build(variant, [50, 30, 70, 60, 80, 65])

        _delete(bst, variant, 50)

        assert list(bst.inorder()) == [30, 60, 65, 70, 80]
        assert _search(bst, variant, 65).key == 65

    def test_root_with_one_child(self, variant: str):
        bst = _build(variant, [50, 30])

        _delete(bst, variant, 50)

        root = bst._root
        assert root is not None
        assert root.key == 30
        assert list(bst.inorder()) == [30]

    def test_only_node_empties_tree(self, variant: str):
        bst = _build(variant, [50])

        _delete(bst, variant, 50)

        assert bst._root is None
        with pytest.raises(KeyError):
            _search(bst, variant, 50)

    def test_missing_key_raises_and_keeps_tree(self, variant: str):
        bst = _build(variant, [50, 30, 70])

        with pytest.raises(KeyError):
            _delete(bst, variant, 999)
        assert list(bst.inorder()) == [30, 50, 70]  # 실패한 삭제는 트리를 안 건드림

    def test_repeated_deletes_preserve_invariant(self, variant: str):
        bst = _build(variant, [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45])

        for k in [50, 20, 70, 35]:
            _delete(bst, variant, k)

        keys = list(bst.inorder())
        assert keys == sorted(keys)  # 항상 정렬 유지
        assert not ({50, 20, 70, 35} & set(keys))  # 삭제된 키는 없음
        assert {10, 25, 30, 40, 45, 60, 80} == set(keys)  # 나머지는 보존


class TestReplaceChild:
    """반복형 삭제의 헬퍼 _replace_child 직접 검증."""

    def test_noop_when_no_child_matches_key(self):
        # parent의 어느 자식도 key와 안 맞으면 트리를 건드리지 않는다 (방어 분기)
        bst = _build("iterative", [50, 30, 70])
        root = bst._root
        assert root is not None

        bst._replace_child(root, 999, None)  # 30도 70도 999가 아님

        assert list(bst.inorder()) == [30, 50, 70]

    def test_replaces_matching_left_child(self):
        bst = _build("iterative", [50, 30, 70])
        root = bst._root
        assert root is not None

        bst._replace_child(root, 30, None)  # 왼쪽 자식(30) 링크 끊기

        assert list(bst.inorder()) == [50, 70]


class TestTraversal:
    def test_preorder_visits_root_left_right(self):
        bst = _build("recursive", FULL)

        assert list(bst.preorder()) == [50, 30, 20, 40, 70, 60, 80]

    def test_inorder_is_sorted(self):
        bst = _build("recursive", FULL)

        assert list(bst.inorder()) == [20, 30, 40, 50, 60, 70, 80]

    def test_postorder_visits_left_right_root(self):
        bst = _build("recursive", FULL)

        assert list(bst.postorder()) == [20, 40, 30, 60, 80, 70, 50]

    def test_is_lazy_generator(self):
        bst = _build("recursive", FULL)

        gen = bst.inorder()

        assert isinstance(gen, types.GeneratorType)
        assert next(gen) == 20  # 첫 값만 뽑아도 동작 (지연 평가)

    def test_empty_tree_traversals_are_empty(self):
        bst = BST[int]()

        assert list(bst.preorder()) == []
        assert list(bst.inorder()) == []
        assert list(bst.postorder()) == []
