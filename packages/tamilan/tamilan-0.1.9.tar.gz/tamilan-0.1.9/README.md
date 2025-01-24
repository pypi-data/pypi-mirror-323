# Tamilan Python Library

A Python library for interacting with the Gemini API, performing `TwoSum` operations, checking for subsequences, and chatting with an AI-powered chatbot.

## Features

- **AI Class**: Uses the Gemini API to generate text responses based on a given prompt.
- **TwoSumK & TwoSum Functions**: Efficient solutions to find pairs of numbers in a sorted list that sum to a target.
- **Subsequence Check**: Verifies if one string is a subsequence of another.
- **Bot Class**: A chatbot powered by the Gemini API that interacts with users.

## Installation

To install the library, you can use pip:

```bash
pip install tamilan

## Usage

### 1. **Importing the Library**

You can import the functions and classes from the `tamilan` package as follows:

```python
from tamilan import AI, Bot, twoSumK, twoSum, is_subsequence
```

### 2. **Using the `AI` Class**

The `AI` class allows you to generate text using the Gemini API. 

#### Example:
```python
# Initialize the AI instance with your Gemini API key
api_key = "YOUR_API_KEY"  # Replace with your actual API key
ai = AI(api_key)

# Generate a response based on a prompt
prompt = "What is the capital of France?"
response = ai.generate_text(prompt)
print(response)
```

### 3. **Using the `Bot` Class**

The `Bot` class allows you to interact with an AI chatbot. The chatbot responds to your inputs by calling the Gemini API.

#### Example:
```python
# Initialize the chatbot with your Gemini API key
bot = Bot(api_key="YOUR_API_KEY")  # Replace with your actual API key

# Start a chat with the chatbot
bot.chat()
```

Type your input in the terminal, and the chatbot will respond. To end the chat, type 'exit'.

### 4. **Using the `twoSumK` and `twoSum` Functions**

These functions help you find two numbers in a sorted list that sum up to a target.

#### Example: `twoSumK` (1-based index)
```python
numbers = [1, 2, 3, 4, 5]
target = 6
result = twoSumK(numbers, target)
print(result)  # Output: [1, 5] (1-based index)
```

#### Example: `twoSum` (0-based index)
```python
numbers = [1, 2, 3, 4, 5]
target = 6
result = twoSum(numbers, target)
print(result)  # Output: [0, 4] (0-based index)
```

### 5. **Using the `is_subsequence` Function**

This function checks if one string is a subsequence of another.

#### Example:
```python
s = "abc"
t = "ahbgdc"
result = is_subsequence(s, t)
print(result)  # Output: True
```

### 6. **Helper Function**

The `helper()` function provides a list of function signatures for reference.

```python
from tamilan import helper
functions = helper()
print(functions)
# Output:
# ['twoSumK(numbers: List[int], target: int) -> List[int]',
#  'twoSum(numbers: List[int], target: int) -> List[int]',
#  'is_subsequence(s: str, t: str) -> bool']
```

## Contributing

Contributions are welcome! Please feel free to fork the repository, submit pull requests, or open issues for suggestions or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

