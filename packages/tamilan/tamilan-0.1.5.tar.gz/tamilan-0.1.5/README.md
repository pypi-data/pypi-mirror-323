# TwoSum Library

A simple Python library to find indices of numbers that sum up to a target in sorted arrays and check for subsequences.

## Functions

### 1. `twoSumK(numbers: List[int], target: int) -> List[int]`

**Description**:  
This function takes a sorted list of integers and a target integer. It returns the 1-based indices of the two numbers that add up to the target.

**Parameters**:
- `numbers` (List[int]): A sorted list of integers.
- `target` (int): The target sum.

**Returns**:
- List[int]: A list containing the 1-based indices of the two numbers that sum to the target. Returns an empty list if no such numbers exist.

**Example**:
```python
result = twoSumK([2, 7, 11, 15], 9)  # Output: [1, 2]
```

### 2. `twoSum(numbers: List[int], target: int) -> List[int]`

**Description**:  
This function operates similarly to `twoSumK`, but it returns 0-based indices.

**Parameters**:
- `numbers` (List[int]): A sorted list of integers.
- `target` (int): The target sum.

**Returns**:
- List[int]: A list containing the 0-based indices of the two numbers that sum to the target. Returns an empty list if no such numbers exist.

**Example**:
```python
result = twoSum([2, 7, 11, 15], 9)  # Output: [0, 1]
```

### 3. `is_subsequence(s: str, t: str) -> bool`

**Description**:  
This function checks if string `s` is a subsequence of string `t`.

**Parameters**:
- `s` (str): The string to check as a subsequence.
- `t` (str): The string in which to check for the subsequence.

**Returns**:
- bool: Returns `True` if `s` is a subsequence of `t`, otherwise `False`.

**Example**:
```python
result = is_subsequence("abc", "ahbgdc")  # Output: True
```

## Installation

To use this library, you can clone the repository or install it via pip (if published):

```bash
pip install your_library_name
```

## Usage

Import the functions into your script as follows:

```python
from your_library_name import twoSumK, twoSum, is_subsequence

# Example usage
indices = twoSumK([2, 3, 4], 6)
print(indices)  # Output: [1, 3]
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to modify any sections to better fit your library or personal style!