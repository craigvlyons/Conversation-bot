import sys
import asyncio
import signal
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop
from ui.chatwindow import ChatUI
from tools import TOOLS_LIST 
from utils.constants import GEMINI_KEY 
import setup.initialize_agents as initialize_agents


async def shutdown_mcp_servers():
    """Gracefully shutdown MCP servers on application exit"""
    print("Shutting down MCP servers...")
    server_manager = getattr(initialize_agents, "server_manager", None)
    if server_manager:
        await server_manager.stop_all_servers()
        print("MCP servers stopped")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Get the primary agent (or MCP agent if available)
    agent = initialize_agents.AgentRegistry.get("mcp")
    if agent is None:
        agent = initialize_agents.AgentRegistry.get("primary")
    
    # Create and show the chat UI
    chat_ui = ChatUI(agent)
    chat_ui.show()
    
    # Handle graceful shutdown
    def signal_handler(*args):
        print("Shutting down application...")
        loop.create_task(shutdown_mcp_servers())
        app.quit()
    
    # Register signal handlers
    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(sig, signal_handler)
    
    # Run the event loop
    with loop:
        try:
            loop.run_forever()
        finally:
            # Ensure MCP servers are stopped
            if hasattr(loop, "run_until_complete"):
                loop.run_until_complete(shutdown_mcp_servers())
