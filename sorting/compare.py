"""모든 정렬 구현을 Python 내장 정렬과 나란히 비교한다."""

from scaffold.sort_tester import compare_sort
from sorting.bubble_sort import bubble_sort
from sorting.insertion_sort import insertion_sort
from sorting.merge_sort import merge_sort
from sorting.merge_sort_in_place import merge_sort as merge_sort_inplace
from sorting.quick_sort import quick_sort
from sorting.quick_sort_in_place import quick_sort as quick_sort_inplace
from sorting.selection_sort import selection_sort

merge_sort_inplace.__name__ = "merge_sort_inplace"
quick_sort_inplace.__name__ = "quick_sort_inplace"


def _list_sort(a):
    a.sort()


_list_sort.__name__ = "list.sort"


if __name__ == "__main__":
    compare_sort(
        bubble_sort,
        selection_sort,
        insertion_sort,
        merge_sort,
        merge_sort_inplace,
        quick_sort,
        quick_sort_inplace,
        sorted,
        _list_sort,
        bench=True,
    )
