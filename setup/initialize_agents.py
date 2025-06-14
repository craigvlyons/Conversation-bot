from agents.mcp_agent import MCPAgent
from agents.gemini_agent import GeminiAIAgent
from agents.gemini2agent import GeminiAIAgent2 
from agents.gpt_agent import GPT4oAgent
from agents.registry import AgentRegistry
from utils.constants import GEMINI_KEY, OPENAI_KEY
from utils.mcp_server_manager import MCPServerManager
from utils.mcp_client import MCPClient
from utils.mcp_tool_registry import MCPToolRegistry
from utils.mcp_agent_integration import get_mcp_integration, MCPEnhancedGeminiAgent, MCPEnhancedGPTAgent
import logging
import asyncio
import sys
import traceback
import threading

# Configure logging to be more verbose
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Global variable to store the MCP components
server_manager = None
mcp_client = None
tool_registry = None
mcp_agent = None

# Run MCP setup in a background thread to avoid blocking the UI
def run_mcp_setup_thread():
    """Run MCP setup tasks in a separate thread"""
    global server_manager, mcp_client, tool_registry, mcp_agent
    
    logger.debug("====== MCP SETUP THREAD STARTED ======")
    try:
        # Create a new event loop for this thread
        logger.debug("Creating new event loop for MCP setup thread")
        thread_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(thread_loop)
        logger.debug("Event loop created successfully")
        
        # Initialize MCP components
        logger.info("Initializing MCP Server Manager")
        server_manager = MCPServerManager()
        logger.debug(f"Server manager created: {server_manager}")
        
        # Connect to MCP servers with timeout
        logger.info("Connecting to MCP servers")
        logger.debug(f"Available servers before connection: {list(server_manager.servers.keys())}")
        server_manager.connect_to_servers(timeout=10)        # Log connected servers
        connected_servers = list(server_manager.connected_servers.keys())
        logger.info(f"Connected to {len(connected_servers)} MCP servers")
        logger.debug(f"Connected servers: {connected_servers}")
        for server_id in connected_servers:
            server = server_manager.connected_servers[server_id]
            logger.info(f"  ✅ {server_id} (URL: {server.url}, PID: {server.process.pid if server.process else 'None'})")
        
        # Discover server capabilities
        if connected_servers:
            logger.info("Discovering server capabilities")
            server_manager.discover_capabilities()
            logger.debug("Server capabilities discovery completed")
        
        if connected_servers:
            # Set up MCP client
            logger.info("Setting up MCP Client")
            mcp_client = MCPClient(server_manager.servers)
            logger.debug(f"MCP client created: {mcp_client}")
            
            # Initialize tool registry
            logger.info("Initializing MCP Tool Registry")
            tool_registry = MCPToolRegistry(mcp_client)
            logger.debug(f"Tool registry created: {tool_registry}")
            
            logger.debug("Registering tools from MCP client")
            tool_count = tool_registry.register_from_mcp_client()
            logger.info(f"Registered {tool_count} MCP tools")
            
            # Log available tools
            all_tools = mcp_client.get_all_tools()
            logger.debug(f"Available tools from MCP client: {list(all_tools.keys()) if all_tools else 'None'}")
            
            # Create MCP agent
            logger.info("Creating MCP-aware agent")
            mcp_agent = MCPAgent("mcp_agent", server_manager, tool_registry)
            logger.debug(f"MCP agent created: {mcp_agent}")
            
            # Register MCP agent globally
            logger.debug("Registering MCP agent with AgentRegistry")
            AgentRegistry.register("mcp", mcp_agent)
            logger.info("Registered MCP agent")
            
            # Set up MCP integration
            logger.info("Setting up MCP integration with agents")
            mcp_integration = get_mcp_integration()
            mcp_integration.set_mcp_executor(mcp_agent.execute_mcp_tool)            # Register MCP tools with each agent if available
            if tool_registry and mcp_agent:
                logger.debug("Getting all MCP tools from agent")
                tools = mcp_agent.get_all_mcp_tools()
                logger.info(f"Registering {len(tools)} MCP tools with agents")
                logger.debug(f"Tool names: {list(tools.keys())}")
                
                # Register MCP tools with enhanced agents
                logger.debug("Registering MCP tools with enhanced agents")
                try:
                    # Register with primary agent
                    logger.debug("Registering MCP tools with primary agent")
                    for tool_name, tool_info in tools.items():
                        primary_agent.register_mcp_tool(tool_name, tool_info)
                    primary_agent.enable_mcp()
                    primary_agent.setup_mcp_integration(tools)
                    
                    # Register with secondary agent  
                    logger.debug("Registering MCP tools with secondary agent")
                    for tool_name, tool_info in tools.items():
                        secondary_agent.register_mcp_tool(tool_name, tool_info)
                    secondary_agent.enable_mcp()
                    secondary_agent.setup_mcp_integration(tools)
                    
                    # Register with fallback agent
                    logger.debug("Registering MCP tools with fallback agent")
                    for tool_name, tool_info in tools.items():
                        fallback_agent.register_mcp_tool(tool_name, tool_info)
                    fallback_agent.enable_mcp()
                    fallback_agent.setup_mcp_integration(tools)
                    
                    logger.info("MCP tools registered with all agents")
                    
                except Exception as e:
                    logger.error(f"Error registering MCP tools with agents: {e}")
                    logger.error(traceback.format_exc())
            else:
                logger.warning("tool_registry or mcp_agent is None, skipping tool registration")
        else:
            logger.warning("No MCP servers connected, skipping MCP client and tool setup")
        
        logger.info("MCP setup completed in background thread")
        logger.debug("====== MCP SETUP THREAD COMPLETED ======")
    except Exception as e:
        logger.error(f"Error in MCP setup thread: {e}")
        logger.error(traceback.format_exc())

def run_setup():
    """Start the MCP setup process in a background thread and return immediately"""
    try:
        # Start a background thread for MCP server setup
        setup_thread = threading.Thread(
            target=run_mcp_setup_thread,
            name="mcp-setup-thread",
            daemon=True  # Mark as daemon so it won't block application exit
        )
        setup_thread.start()
        
        # Return immediately - setup will continue in the background
        logger.info("MCP setup started in background thread")
        
        # Return empty dictionary since the real initialization happens in the background
        return {}
    except Exception as e:
        logger.error(f"Error starting MCP setup thread: {e}")
        return {}

# Instantiate core agents with MCP enhancement capability
# Note: We'll use regular agents initially and enhance them when MCP tools are available
primary_agent = GeminiAIAgent(api_key=GEMINI_KEY)       # Gemini - is probably good enough for basic tasks and cheap.
fallback_agent = GPT4oAgent(api_key=OPENAI_KEY)         # GPT - is probably better for code, then Gemini
secondary_agent = GeminiAIAgent2(api_key=GEMINI_KEY)    # Gemini2 - is probably better for more complex tasks, then Gemini 1.

# Register them globally
AgentRegistry.register("primary", primary_agent)
AgentRegistry.register("fallback", fallback_agent)
AgentRegistry.register("gemini", primary_agent)
AgentRegistry.register("gpt4o", fallback_agent)
AgentRegistry.register("gemini2", secondary_agent)

# Start the MCP setup process in the background
run_setup()
