import openai
from PyQt5.QtCore import QThread, pyqtSignal
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")  # Make sure this matches your .env
)

class Worker(QThread):
    response = pyqtSignal(str)

    def __init__(self, prompt, chat_history=None):
        super().__init__()
        self.prompt = prompt
        self.chat_history = chat_history or []

    def run(self):
        try:
            result, self.chat_history = generate_openai_response(self.prompt, self.chat_history)
            self.response.emit(result)
        except Exception as e:
            self.response.emit(f"Error: {str(e)}")

def generate_openai_response(user_input, chat_history=None):
    chat_history = chat_history or []
    
    messages = [
        {
            "role": "system", 
            "content": "You are a screen-time management assistant."
        },
        *chat_history,
        {"role": "user", "content": user_input}
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150
        )
        assistant_response = response.choices[0].message.content
        chat_history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": assistant_response}
        ])
        return assistant_response, chat_history
    except Exception as e:
        print(f"API Error: {e}")
        return "Sorry, I couldn't process your request.", chat_history

chat_history = []
user_input = "How long should I use my computer each day?"
response, chat_history = generate_openai_response(user_input, chat_history)
#print("AI Response:", response)
