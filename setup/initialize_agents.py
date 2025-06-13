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

logger = logging.getLogger(__name__)

# Run async setup
def run_async_setup():
    """Run async setup tasks"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Initialize MCP components
        logger.info("Initializing MCP Server Manager")
        server_manager = MCPServerManager()
        loop.run_until_complete(server_manager.load_servers_config())
        
        # Connect to MCP servers
        logger.info("Connecting to MCP servers")
        server_results = loop.run_until_complete(server_manager.connect_all_servers())
        
        logger.info(f"Connected to {sum(1 for success in server_results.values() if success)} MCP servers")
        for name, success in server_results.items():
            if success:
                logger.info(f"  ✅ {name}")
            else:
                logger.info(f"  ❌ {name}")
        
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
        loop.run_until_complete(mcp_agent.initialize())
        
        # Return the MCP components
        return {
            "server_manager": server_manager,
            "mcp_client": mcp_client,
            "tool_registry": tool_registry,
            "mcp_agent": mcp_agent
        }
    except Exception as e:
        logger.error(f"Error in async setup: {e}")
        return {}
    finally:
        loop.close()

# Initialize MCP components
mcp_components = run_async_setup()

# Get MCP components
server_manager = mcp_components.get("server_manager")
mcp_client = mcp_components.get("mcp_client")
tool_registry = mcp_components.get("tool_registry")
mcp_agent = mcp_components.get("mcp_agent")

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

# Register MCP agent if available
if mcp_agent:
    AgentRegistry.register("mcp", mcp_agent)
    logger.info("Registered MCP agent")

# Register MCP tools with each agent if available
if tool_registry and mcp_agent:
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