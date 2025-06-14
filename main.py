import sys
import asyncio
import signal
import threading
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop
from ui.chatwindow import ChatUI
from utils.constants import GEMINI_KEY 
import setup.initialize_agents_new as initialize_agents


async def shutdown_mcp_servers():
    """Gracefully shutdown MCP servers on application exit"""
    print("Shutting down MCP servers...")
    if hasattr(initialize_agents, 'server_manager') and initialize_agents.server_manager:
        await initialize_agents.server_manager.stop_all_servers()
        print("MCP servers stopped")
    else:
        print("No MCP servers to shut down")


if __name__ == "__main__":
    print("Starting Conversation Bot...")
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # MCP servers should be initialized in the background
    # Don't wait for them to be fully ready before starting the UI
    
    # Get the primary agent (not MCP agent, since it might still be initializing)
    # We'll check for MCP later when needed
    agent = initialize_agents.AgentRegistry.get("primary")
    
    # Create and show the chat UI
    chat_ui = ChatUI(agent)
    chat_ui.show()    # Handle graceful shutdown
    def signal_handler(*args):
        print("Shutting down application...")
        if hasattr(initialize_agents, 'server_manager') and initialize_agents.server_manager:
            loop.create_task(shutdown_mcp_servers())
        app.quit()
    
    # Register signal handlers - using try/except to handle Windows compatibility
    try:
        for sig in [signal.SIGINT, signal.SIGTERM]:
            loop.add_signal_handler(sig, signal_handler)
    except NotImplementedError:
        # Windows doesn't support add_signal_handler
        import atexit
        atexit.register(signal_handler)
    
    # Run the event loop
    with loop:
        try:
            sys.exit(app.exec())
        finally:            # Ensure MCP servers are stopped
            if hasattr(initialize_agents, 'server_manager') and initialize_agents.server_manager:
                try:
                    loop.run_until_complete(shutdown_mcp_servers())
                except Exception as e:
                    print(f"Failed to gracefully shut down MCP servers: {e}")
