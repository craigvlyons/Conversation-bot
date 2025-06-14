from typing import Any, Optional, Dict, List, Tuple
import asyncio
import json
from datetime import datetime

from agents.base_agent import BaseAgent
from utils.mcp_server_manager import MCPServerManager
from utils.tool_manager import ToolManager
from utils.dynamic_tool_handler import DynamicToolHandler, ToolRouter

class MCPAgent(BaseAgent):
    """
    Modern MCP Agent using dynamic tool discovery and routing.
    Automatically discovers and executes any MCP tool without hard-coded handlers.
    """
    
    def __init__(self, name: str = "mcp_agent", 
                 server_manager: Optional[MCPServerManager] = None):
        super().__init__(name)
        
        # Set up MCP components with new dynamic system
        self.server_manager = server_manager or MCPServerManager()
        self.tool_manager = ToolManager(self.server_manager)
        self.tool_handler = DynamicToolHandler(self.tool_manager)
        self.tool_router = ToolRouter(self.tool_manager)
        
        # Track initialization state
        self.initialized = False
        self.tools_discovered = False
        
        # Enable MCP by default
        self.enable_mcp()
    
    async def initialize(self):
        """Initialize the agent by discovering tools from all connected servers"""
        if self.initialized:
            return
        
        print("🔧 Initializing MCP Agent with dynamic tool discovery...")
        
        # Discover all tools from connected servers
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
            print(f"✅ MCP Agent initialized with {len(discovered_tools)} tools")
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
        discovered_tools = self.tool_manager.get_all_tools()
        result = {}
        
        for name, tool in discovered_tools.items():
            result[name] = {
                "name": name,
                "description": tool.description,
                "schema": tool.schema,
                "server_id": tool.server_id,
                "metadata": tool.metadata
            }
        
        return result
    
    def _get_tools_summary(self) -> str:
        """Get a formatted summary of all available tools."""
        if not self.tools_discovered:
            return "Tool discovery has not completed yet."
        
        return self.tool_manager.get_tool_info_summary()
    
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
