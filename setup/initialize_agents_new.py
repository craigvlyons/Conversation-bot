from agents.mcp_agent import MCPAgent
from agents.gemini_agent import GeminiAIAgent
from agents.gemini2agent import GeminiAIAgent2 
from agents.gpt_agent import GPT4oAgent
from agents.registry import AgentRegistry
from utils.constants import GEMINI_KEY, OPENAI_KEY
from utils.mcp_server_manager import MCPServerManager
from utils.mcp_client import MCPClient
from utils.mcp_tool_registry import MCPToolRegistry
import logging
import asyncio
import threading

logger = logging.getLogger(__name__)

# Global variable to store the MCP components
server_manager = None
mcp_client = None
tool_registry = None
mcp_agent = None

# Run MCP setup in a background thread to avoid blocking the UI
def run_mcp_setup_thread():
    """Run MCP setup tasks in a separate thread"""
    try:
        global server_manager, mcp_client, tool_registry, mcp_agent
        
        # Create a new event loop for this thread
        thread_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(thread_loop)
        
        # Initialize MCP components
        logger.info("Initializing MCP Server Manager")
        server_manager = MCPServerManager()
        
        # Connect to MCP servers with timeout
        logger.info("Connecting to MCP servers")
        server_manager.connect_to_servers(timeout=10)
        
        # Log connected servers
        connected_servers = list(server_manager.connected_servers.keys())
        logger.info(f"Connected to {len(connected_servers)} MCP servers")
        for server_id in connected_servers:
            logger.info(f"  ✅ {server_id}")
        
        if connected_servers:
            # Set up MCP client
            mcp_client = MCPClient(server_manager.servers)
            
            # Initialize tool registry
            logger.info("Initializing MCP Tool Registry")
            tool_registry = MCPToolRegistry(mcp_client)
            tool_count = tool_registry.register_from_mcp_client()
            logger.info(f"Registered {tool_count} MCP tools")
            
            # Create MCP agent
            logger.info("Creating MCP-aware agent")
            mcp_agent = MCPAgent("mcp_agent", server_manager, tool_registry)
            
            # Register MCP agent if available
            AgentRegistry.register("mcp", mcp_agent)
            logger.info("Registered MCP agent")
            
            # Register MCP tools with each agent if available
            if mcp_agent:
                tools = mcp_agent.get_all_mcp_tools()
                logger.info(f"Registering {len(tools)} MCP tools with agents")
                
                # Register tool metadata with regular agents
                for tool_name, tool_info in tools.items():
                    primary_agent.register_mcp_tool(tool_name, tool_info)
                    secondary_agent.register_mcp_tool(tool_name, tool_info)
                    fallback_agent.register_mcp_tool(tool_name, tool_info)
                
                # Enable MCP for all agents
                primary_agent.enable_mcp()
                secondary_agent.enable_mcp()
                fallback_agent.enable_mcp()
                
                logger.info("MCP tools registered with all agents")
        
        logger.info("MCP setup completed in background thread")
    except Exception as e:
        logger.error(f"Error in MCP setup thread: {e}")
        import traceback
        logger.error(traceback.format_exc())

def run_setup():
    """Start the MCP setup process in a background thread and return immediately"""
    # Start a background thread for MCP server setup
    setup_thread = threading.Thread(
        target=run_mcp_setup_thread,
        name="mcp-setup-thread",
        daemon=True  # Mark as daemon so it won't block application exit
    )
    setup_thread.start()
    
    # Return immediately - setup will continue in the background
    logger.info("MCP setup started in background thread")

# Instantiate core agents
primary_agent = GeminiAIAgent(api_key=GEMINI_KEY)       # Gemini - is probably good enough for basic tasks and cheap.
fallback_agent = GPT4oAgent(api_key=OPENAI_KEY)         # GPT - is probably better for code, then Gemini
secondary_agent = GeminiAIAgent2(api_key=GEMINI_KEY)    # Gemini2 - is probably better for more complex tasks, then Gemini 1.

# Register them globally
AgentRegistry.register("primary", primary_agent)
AgentRegistry.register("fallback", fallback_agent)
AgentRegistry.register("gemini", primary_agent)
AgentRegistry.register("gpt4o", fallback_agent)
AgentRegistry.register("gemini2", secondary_agent)

# For now, skip MCP setup to make sure the application starts properly
# run_setup()
