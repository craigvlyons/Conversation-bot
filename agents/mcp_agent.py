from typing import Any, Optional, Dict, List, Tuple
import asyncio
import json
from datetime import datetime

from agents.base_agent import BaseAgent
from utils.mcp_server_manager import MCPServerManager
from utils.tool_manager import ToolManager
from utils.dynamic_tool_handler import DynamicToolHandler, ToolRouter
from utils.mcp_tool_registry import MCPToolRegistry

class MCPAgent(BaseAgent):
    """
    Modern MCP Agent using dynamic tool discovery and routing.
    Automatically discovers and executes any MCP tool without hard-coded handlers.
    """
    
    def __init__(self, name: str = "mcp_agent", 
                 server_manager: Optional[MCPServerManager] = None,
                 tool_registry: Optional[MCPToolRegistry] = None):
        super().__init__(name)
        
        # Set up MCP components with new dynamic system
        self.server_manager = server_manager or MCPServerManager()
        self.tool_registry = tool_registry  # Use cached tool registry if available
        self.tool_manager = ToolManager(self.server_manager)
        self.tool_handler = DynamicToolHandler(self.tool_manager)
        self.tool_router = ToolRouter(self.tool_manager)
        
        # Track initialization state
        self.initialized = False
        self.tools_discovered = False
        
        # Enable MCP by default
        self.enable_mcp()
    
    async def initialize(self):
        """Initialize the agent by using cached tools or discovering from servers"""
        if self.initialized:
            return
        
        print("🔧 Initializing MCP Agent...")
        
        # First try to use cached tools from tool registry
        if self.tool_registry:
            print("📋 Using cached tools from tool registry...")
            cached_tools = self.tool_registry.get_tools_for_agent()
            
            if cached_tools:
                # Register cached tools with the base agent
                for tool_name, tool_info in cached_tools.items():
                    self.register_mcp_tool(tool_name, {
                        "description": tool_info.get("description", ""),
                        "schema": tool_info.get("inputSchema", {}),
                        "server_id": tool_info.get("server", "unknown"),
                        "metadata": tool_info
                    })
                
                self.tools_discovered = True
                print(f"✅ MCP Agent initialized with {len(cached_tools)} cached tools")
                self.initialized = True
                return
            else:
                print("⚠️ No cached tools found in registry")
        
        # Fallback to dynamic discovery
        print("🔄 Falling back to dynamic tool discovery...")
        
        # First ensure servers are connected
        print("🔗 Connecting to MCP servers...")
        self.server_manager.connect_to_servers(timeout=15)
        
        if not self.server_manager.connected_servers:
            print("❌ No MCP servers connected")
        else:
            print(f"✅ Connected to {len(self.server_manager.connected_servers)} servers")
        
        discovered_tools = await self.tool_manager.discover_all_tools()
        
        if discovered_tools:
            # Register tools with the base agent
            for tool_name, tool in discovered_tools.items():
                self.register_mcp_tool(tool_name, {
                    "description": tool.description,
                    "schema": tool.schema,
                    "server_id": tool.server_id,
                    "metadata": tool.metadata
                })
            
            self.tools_discovered = True
            print(f"✅ MCP Agent initialized with {len(discovered_tools)} discovered tools")
        else:
            print("⚠️ No tools discovered during MCP Agent initialization")
        
        self.initialized = True

    async def get_response(self, user_input: str, history=None) -> str:
        """
        Process user input using dynamic tool routing and execution.
        """
        # Ensure we're initialized
        if not self.initialized:
            await self.initialize()
        
        # Handle tool information queries
        if any(phrase in user_input.lower() for phrase in ["what tools", "available tools", "list tools", "show tools"]):
            return self._get_tools_summary()
        
        # Try to route and execute a tool
        try:
            result = await self.tool_router.route_and_execute(user_input)
            
            if result:
                if result.success:
                    return f"Tool executed successfully: {result.result}"
                else:
                    return f"Tool execution failed: {result.error}"
            else:
                return "No matching tools found for your request."
                
        except Exception as e:
            return f"Error processing tool request: {str(e)}"
        
    def get_all_mcp_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all MCP tools available from the tool manager.
        
        Returns:
            Dictionary of tool details keyed by tool name
        """
        # Use the base agent's MCP tools registry instead of dynamic discovery
        return super().get_all_mcp_tools()
        
    def get_mcp_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Alias for get_all_mcp_tools for backward compatibility.
        """
        return self.get_all_mcp_tools()
    
    def _get_tools_summary(self) -> str:
        """Get a formatted summary of all available tools."""
        if not self.tools_discovered:
            return "Tool discovery has not completed yet."
        
        # Get tools from the agent's own MCP tools registry
        mcp_tools = self.get_all_mcp_tools()
        
        if not mcp_tools:
            return "No MCP tools are currently available."
        
        # Format tools by category/server
        tool_summary = f"I have access to {len(mcp_tools)} MCP tools:\n\n"
        
        # Group tools by server
        tools_by_server = {}
        for tool_name, tool_info in mcp_tools.items():
            server_id = tool_info.get("server_id", "unknown")
            if server_id not in tools_by_server:
                tools_by_server[server_id] = []
            tools_by_server[server_id].append({
                "name": tool_name,
                "description": tool_info.get("description", "No description")
            })
        
        # Format output
        for server_id, tools in tools_by_server.items():
            tool_summary += f"**{server_id.title()} Tools** ({len(tools)} tools):\n"
            for tool in tools:
                tool_summary += f"- `{tool['name']}`: {tool['description']}\n"
            tool_summary += "\n"
        
        return tool_summary
    
    def register_mcp_tool(self, tool_name: str, tool_info: dict):
        """
        Register an MCP tool with the agent.
        """
        # Store tool info in the base agent's MCP tools registry
        super().register_mcp_tool(tool_name, tool_info)
    
    def enable_mcp(self):
        """
        Enable MCP capabilities for this agent
        """
        self.mcp_enabled = True

    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute an MCP tool using the dynamic tool handler."""
        try:
            # Execute the tool using our dynamic handler
            result = await self.tool_handler.execute_tool(tool_name, parameters)
            
            if result.success:
                return result.result
            else:
                return {"error": result.error}
                
        except Exception as e:
            return {"error": str(e)}
