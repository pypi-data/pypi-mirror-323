from typing import List

def twoSumK(numbers: List[int], target: int) -> List[int]:
    start, end = 0, len(numbers) - 1
    while start < end:
        if numbers[start] + numbers[end] == target:
            return [start + 1, end + 1]
        elif numbers[start] + numbers[end] < target:
            start += 1
        else:
            end -= 1
    return []

def twoSum(numbers: List[int], target: int) -> List[int]:
    start, end = 0, len(numbers) - 1
    while start < end:
        if numbers[start] + numbers[end] == target:
            return [start, end]
        elif numbers[start] + numbers[end] < target:
            start += 1
        else:
            end -= 1
    return []

def is_subsequence(s: str, t: str) -> bool:
    t_iter = iter(t)
    return all(char in t_iter for char in s)
