def quick_sort(A: list[int]):
    if len(A) <= 1:
        return A
    
    pivot = A[0]
    L = [x for x in A[1:] if x < pivot]
    E = [x for x in A[1:] if x == pivot]
    R = [x for x in A[1:] if x > pivot]
    return quick_sort(L) + [pivot] + E + quick_sort(R)


if __name__ == "__main__":
    from core.sort_tester import test_sort
    print(test_sort(quick_sort, bench=True))
