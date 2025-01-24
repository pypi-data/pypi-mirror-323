import requests

class AI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    def generate_text(self, prompt):
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error occurred while making API request: {e}")

class Bot:
    def __init__(self, api_key):
        self.ai = AI(api_key)

    def chat(self):
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
