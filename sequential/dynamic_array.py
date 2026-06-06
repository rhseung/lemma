from typing import cast
from math import log2, ceil

class DynamicArray[T]:
    """용량이 가득 차면 내부 배열 크기를 2배로 늘리는 동적 배열."""

    def __init__(self, capacity: int):
        """초기 용량 이상인 2의 거듭제곱 크기 배열을 만든다. 시간복잡도는 O(capacity)."""
        self._capacity = 1 << ceil(log2(capacity))
        self._len = 0
        self._content: list[T | None] = [None] * self._capacity
    
    def __len__(self) -> int:
        """저장된 원소 개수를 반환한다. 시간복잡도는 O(1)."""
        return self._len
    
    def __str__(self) -> str:
        """내부 배열 전체를 문자열로 반환한다. 시간복잡도는 O(capacity)."""
        return str(self._content)

    def __repr__(self) -> str:
        """디버깅용 표현을 반환한다. 시간복잡도는 O(capacity)."""
        return f"DynamicArray(len={self._len}, capacity={self._capacity}, content={self._content})"
    
    def __getitem__(self, idx: int) -> T:
        """idx 위치의 값을 반환한다. 시간복잡도는 O(1)."""
        if not(0 <= idx < self._len):
            raise IndexError(f"0 <= {idx=} < len={self._len}")
        
        return cast(T, self._content[idx])

    def is_empty(self) -> bool:
        """배열이 비어 있으면 True를 반환한다. 시간복잡도는 O(1)."""
        return self._len == 0

    def front(self) -> T:
        """맨 앞 값을 반환한다. 시간복잡도는 O(1)."""
        return self[0]

    def back(self) -> T:
        """맨 뒤 값을 반환한다. 시간복잡도는 O(1)."""
        return self[self._len - 1]

    def clear(self):
        """모든 값을 제거한다. 시간복잡도는 O(n).

        기존 원소가 가리키던 객체를 해제할 수 있도록 사용 중이던 칸을 None으로 바꾼다.
        """
        for i in range(self._len):
            self._content[i] = None

        self._len = 0
    
    def _extend(self):
        """내부 배열 크기를 2배로 늘린다. 시간복잡도는 O(n).

        n개의 기존 원소를 새 배열로 복사해야 하므로 한 번의 확장은 O(n)이다.
        하지만 append에서 배열이 가득 찰 때마다 용량을 2배로 늘리면, n번 append 동안
        확장에서 복사되는 원소 수는 1, 2, 4, ..., 2^k 꼴이다.
        마지막 복사 크기는 n 이하이므로 2^k <= n 이고,

            1 + 2 + 4 + ... + 2^k = 2^(k + 1) - 1 < 2 * 2^k <= 2n

        이다. 따라서 n번 append 동안 확장 때문에 드는 총 복사 비용은 O(n)이다.
        각 append 자체의 대입 비용 O(1)을 n번 더해도 전체 비용은 O(n)이므로,
        append 1번의 amortized 비용은 O(1)이다.
        """
        new_capacity = self._capacity << 1
        new_content: list[T | None] = [None] * new_capacity

        for i in range(self._len):
            new_content[i] = self._content[i]
        
        self._capacity = new_capacity
        self._content = new_content

    def insert(self, idx: int, value: T) -> bool:
        """idx 위치에 값을 삽입한다. 시간복잡도는 O(n).

        idx 뒤의 원소들을 한 칸씩 밀어야 하므로 최악의 경우 O(n)이다.
        배열이 가득 찬 경우 확장도 O(n)이지만, 전체 시간복잡도는 여전히 O(n)이다.
        """
        # 뒤에 append 하는 것까지 고려해서 <= len
        if not(0 <= idx <= self._len):
            return False

        if self._len == self._capacity:
            self._extend()
        
        for i in range(self._len - 1, idx - 1, -1):
            self._content[i + 1] = self._content[i]
        
        self._content[idx] = value
        self._len += 1
        return True
    
    def append(self, value: T) -> bool:
        """맨 뒤에 값을 추가한다. amortized 시간복잡도는 O(1).

        배열에 빈 칸이 있으면 단순 대입만 하므로 O(1)이다.
        배열이 가득 찬 순간에는 _extend 때문에 한 번의 append가 O(n)이 될 수 있다.
        그러나 용량을 2배씩 늘리므로 n번 append 동안 확장에서 복사되는 원소 수의 합은

            1 + 2 + 4 + ... + 2^k = 2^(k + 1) - 1 < 2n

        으로 O(n)에 묶인다. 여기에 n번의 기본 대입 비용 O(n)을 더해도 전체 비용은 O(n)이다.
        따라서 n번 append의 평균 비용, 즉 append 1번의 amortized 비용은 O(1)이다.
        """
        return self.insert(self._len, value)
    
    def pop(self, idx: int) -> bool:
        """idx 위치의 값을 제거한다. 시간복잡도는 O(n).

        idx 뒤의 원소들을 한 칸씩 당겨야 하므로 최악의 경우 O(n)이다.
        맨 뒤 원소를 제거하는 경우에는 O(1)이다.
        """
        if not(0 <= idx < self._len):
            return False
        
        # 1/4이면 shrink도 구현해야 한다 함
        
        for i in range(idx, self._len - 1):
            self._content[i] = self._content[i + 1]
        
        self._content[self._len - 1] = None
        self._len -= 1
        return True
    
    def remove(self, target_value: T) -> bool:
        """처음 등장하는 target_value를 제거한다. 시간복잡도는 O(n).

        값을 찾기 위해 앞에서부터 최대 n개를 확인하고, 제거 후 원소를 당길 수 있으므로 O(n)이다.
        """
        idx = None
        for i in range(self._len):
            if self._content[i] == target_value:
                idx = i
                break
        else:
            return False
        
        return self.pop(idx)


if __name__ == "__main__":
    arr = DynamicArray[int](2)
    print(arr)

    arr.append(10)
    arr.append(20)
    arr.append(40)
    print("after append:", arr)

    arr.insert(2, 30)
    print("after insert:", arr)

    print("arr[0]:", arr[0])
    print("arr[2]:", arr[2])

    arr.pop(1)
    print("after pop:", arr)

    arr.remove(40)
    print("after remove:", arr)
