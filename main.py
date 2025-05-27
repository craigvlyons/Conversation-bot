import sys
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop
from ui.chatwindow import ChatUI
from tools import TOOLS_LIST 
from utils.constants import GEMINI_KEY 
import setup.initialize_agents as initialize_agents


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    agent = initialize_agents.AgentRegistry.get("primary")
    chat_ui = ChatUI(agent)
    chat_ui.show()

    with loop:
        loop.run_forever()
