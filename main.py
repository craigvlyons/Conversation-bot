import os
import sys
import dotenv
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop
from agents.gemini_agent import GeminiAIAgent
from ui.chatwindow import ChatUI
from tools import Tools 


dotenv.load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_KEY")
if not GEMINI_KEY:
    print("GEMINI_API_KEY not found. Please set it in your environment variables.")
    sys.exit(1)

# Agent.
agent = GeminiAIAgent(GEMINI_KEY, tools=[Tools])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    chat_ui = ChatUI(agent)
    chat_ui.show()
    with loop:
        loop.run_forever()
