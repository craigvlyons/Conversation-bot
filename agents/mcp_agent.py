from typing import Any, Optional, Dict, List, Tuple
import asyncio
import json
from datetime import datetime

from agents.base_agent import BaseAgent
from utils.mcp_server_manager import MCPServerManager
from utils.mcp_client import MCPClient, ToolResponse
from utils.mcp_tool_registry import MCPToolRegistry
from utils.mcp_tool_factory import MCPToolFactory, MCPToolExecutor
from utils.mcp_category_handlers import CategoryHandlerRegistry
from utils.mcp_parameter_validation import ToolParameterValidator, ParameterTransformer, ToolResultFormatter

class MCPAgent(BaseAgent):
    """
    Agent that's aware of MCP capabilities.
    Can discover, select, and execute MCP tools.
    """
    
    def __init__(self, name: str = "mcp_agent", 
                 server_manager: Optional[MCPServerManager] = None,
                 tool_registry: Optional[MCPToolRegistry] = None):
        super().__init__(name)
        
        # Set up MCP components
        self.server_manager = server_manager or MCPServerManager()
        self.mcp_client = MCPClient()
        self.tool_registry = tool_registry or MCPToolRegistry(self.mcp_client)
        
        # Tool factory and executor
        self.tool_factory = MCPToolFactory(self.mcp_client)
        self.tool_executor = MCPToolExecutor(self.tool_factory)
        
        # Handlers and validators
        self.category_handlers = CategoryHandlerRegistry()
        self.parameter_validator = ToolParameterValidator()
        self.parameter_transformer = ParameterTransformer()
        self.result_formatter = ToolResultFormatter()
        
        # Track tool execution history
        self.tool_execution_history = []
        
        # Enable MCP by default
        self.enable_mcp()
    
    def initialize(self):
        """Initialize the agent by loading servers and tools"""
        # The servers and connections should already be set up
        # Just make sure the client has the server information
        self.mcp_client.set_servers(self.server_manager.servers)
        
        # Register tools from the MCP client
        self.tool_registry.register_from_mcp_client()
        
        # Register MCP tools with the agent
        all_tools = self.mcp_client.get_all_tools()
        self.register_mcp_tools(all_tools)

    async def get_response(self, user_input: str, history=None) -> str:
        """
        Process user input and return a response, potentially using MCP tools
        """
        # If we have a primary agent attached, delegate to it by default
        if hasattr(self, 'primary_agent') and self.primary_agent:
            return await self.primary_agent.get_response(user_input, history)
        
        # Basic handling if no primary agent is available
        if "what tools" in user_input.lower() or "available tools" in user_input.lower():
            all_tools = self.mcp_client.get_all_tools() if hasattr(self, 'mcp_client') else {}
            if not all_tools:
                return "No MCP tools are currently available."
            
            tool_list = "\n".join([f"- {name}: {info.get('description', 'No description')}" 
                                  for name, info in all_tools.items()])
            return f"Available MCP tools:\n{tool_list}"
        
        return "I'm the MCP Agent, but I need to be connected to other agents to process your request fully."

    def get_all_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Get all MCP tools available from the client
        
        Returns:
            List of tool details
        """
        if not hasattr(self, 'mcp_client') or not self.mcp_client:
            return []
        
        tools = self.mcp_client.get_all_tools()
        return [
            {
                "name": name,
                "description": details.get("description", ""),
                "parameters": details.get("parameters", {}),
                "server_id": details.get("server_id", "unknown")
            }
            for name, details in tools.items()
        ]
    
    def register_mcp_tools(self, tools_dict: Dict[str, Any]):
        """Register MCP tools with the agent"""
        if not tools_dict:
            return
            
        for tool_name, tool_info in tools_dict.items():
            # Register the tool with the agent
            self.register_tool(
                tool_name,
                tool_info.get("description", "No description available"),
                self.execute_mcp_tool,
                tool_info.get("parameters", {})
            )
            
        # Log the registration
        tool_names = list(tools_dict.keys())
        print(f"Registered {len(tool_names)} MCP tools with {self.name}")
        
    def register_mcp_tool(self, tool_name: str, tool_info: dict):
        """
        Register an MCP tool with the agent
        """
        if not hasattr(self, 'registered_tools'):
            self.registered_tools = {}
            
        # Store tool info
        self.registered_tools[tool_name] = tool_info
        
        # Add the tool to our capabilities
        self.register_tool(
            name=tool_name,
            description=tool_info.get("description", f"Tool {tool_name}"),
            function=self.execute_mcp_tool,  # All tools use the same executor
            parameters=tool_info.get("parameters", {})
        )
    
    def enable_mcp(self):
        """
        Enable MCP capabilities for this agent
        """
        self.mcp_enabled = True

    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute an MCP tool by name with parameters"""
        try:
            # Add to history
            self.tool_execution_history.append({
                "tool": tool_name,
                "parameters": parameters,
                "timestamp": datetime.now().isoformat()
            })
            
            # Transform parameters if needed
            transformed_params = self.parameter_transformer.transform(tool_name, parameters)
            
            # Validate parameters
            self.parameter_validator.validate(tool_name, transformed_params)
            
            # Execute the tool
            response: ToolResponse = await self.tool_executor.execute_tool(
                tool_name, 
                transformed_params
            )
            
            # Format the result
            formatted_result = self.result_formatter.format_result(tool_name, response)
            
            return formatted_result
        except Exception as e:
            return {"error": str(e)}
