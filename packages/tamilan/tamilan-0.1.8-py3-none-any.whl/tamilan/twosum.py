import requests
from typing import List

class AI:
    def __init__(self, api_key):
        """
        Initialize the GeminiAPI client with the API key.
        """
        self.api_key = api_key
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    def generate_text(self, prompt):
        """
        Generate text using the Gemini API.

        Args:
            prompt (str): The input prompt for the API.

        Returns:
            str: The generated text.
        """
        # Define the payload
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        # Define the headers
        headers = {
            "Content-Type": "application/json"
        }

        # Make the POST request
        try:
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

            # Extract and return only the generated text
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error occurred while making API request: {e}")

def twoSumK(numbers: List[int], target: int) -> List[int]:
    """
    Find the 1-based indices of two numbers in a sorted list that add up to the target.

    Parameters:
    numbers (List[int]): A sorted list of integers.
    target (int): The target sum.

    Returns:
    List[int]: A list containing the 1-based indices of the two numbers that sum to the target.
    """
    start, end = 0, len(numbers) - 1  # left, right
    while start < end:
        if numbers[start] + numbers[end] == target:
            return [start + 1, end + 1]
        elif numbers[start] + numbers[end] < target:
            start += 1
        else:
            end -= 1
    return []

def twoSum(numbers: List[int], target: int) -> List[int]:
    """
    Find the 0-based indices of two numbers in a sorted list that add up to the target.

    Parameters:
    numbers (List[int]): A sorted list of integers.
    target (int): The target sum.

    Returns:
    List[int]: A list containing the 0-based indices of the two numbers that sum to the target.
    """
    start, end = 0, len(numbers) - 1  # left, right
    while start < end:
        if numbers[start] + numbers[end] == target:
            return [start, end]
        elif numbers[start] + numbers[end] < target:
            start += 1
        else:
            end -= 1
    return []

def is_subsequence(s: str, t: str) -> bool:
    """
    Check if string 's' is a subsequence of string 't'.

    Parameters:
    s (str): The string to check as a subsequence.
    t (str): The string in which to check for the subsequence.

    Returns:
    bool: Returns True if 's' is a subsequence of 't', otherwise False.
    """
    t_iter = iter(t)  # Create an iterator for 't'
    return all(char in t_iter for char in s)

def helper() -> List[str]:
    """
    Returns a list of function signatures for reference.

    Returns:
    List[str]: A list of function signatures.
    """
    return [
        "twoSumK(numbers: List[int], target: int) -> List[int]",
        "twoSum(numbers: List[int], target: int) -> List[int]",
        "is_subsequence(s: str, t: str) -> bool"
    ]
class Bot:
    def __init__(self, api_key):
        """
        Initialize the chatbot with the AI instance.
        """
        self.ai = AI(api_key)
        print("Tamilan AI Chatbot is ready to chat! 🚀")

    def chat(self):
        """
        Start the chatbot interaction.
        """
        print("Type 'exit' to end the chat.\n")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Chatbot: Goodbye! 👋")
                break
            try:
                response = self.ai.generate_text(user_input)
                print(f"Chatbot: {response}")
            except Exception as e:
                print(f"Chatbot: Sorry, an error occurred: {e}")