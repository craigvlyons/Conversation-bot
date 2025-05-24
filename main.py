import os
import sys
import dotenv
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop
from agents.gemini_agent import GeminiAIAgent
from ui.chatwindow import ChatUI
from tools.weather_tool import WeatherTool
from models.cities import get_city

dotenv.load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_KEY")
if not GEMINI_KEY:
    print("GEMINI_API_KEY not found. Please set it in your environment variables.")
    sys.exit(1)

from tools.weather_tool import WeatherTool
weather_tool = WeatherTool()
agent = GeminiAIAgent(GEMINI_KEY, tools=[weather_tool])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    chat_ui = ChatUI(agent)
    chat_ui.show()
    with loop:
        loop.run_forever()
