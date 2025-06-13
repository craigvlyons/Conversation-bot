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
    
    async def initialize(self):
        """Initialize the agent by loading servers and tools"""
        # Load and connect to MCP servers
        await self.server_manager.load_servers_config()
        await self.server_manager.connect_all_servers()
        
        # Set up client with server information
        self.mcp_client.set_servers(self.server_manager.servers)
        
        # Register tools from the MCP client
        self.tool_registry.register_from_mcp_client()
        
        # Register MCP tools with the agent
        all_tools = self.mcp_client.get_all_tools()
        self.register_mcp_tools(all_tools)
    
    async def get_response(self, user_input: str, history: Optional[str] = None) -> Any:
        """
        Generate a response based on user input and conversation history.
        If the input indicates a tool should be used, will execute the tool.
        """
        # Placeholder implementation - subclass should implement real LLM integration
        if not self.mcp_enabled:
            return "MCP functionality is not enabled for this agent."
        
        # Simple rule-based tool selection for demo purposes
        # In a real implementation, you'd use an LLM to decide when to use tools
        if "tools" in user_input.lower() or "list tools" in user_input.lower():
            tools = self.get_all_mcp_tools()
            response = f"Available tools ({len(tools)}):\n\n"
            for name, tool in tools.items():
                response += f"- {name}: {tool.get('description', 'No description')}\n"
            return response
        
        # Check if user is explicitly asking to use a tool
        tool_name = None
        tool_params = {}
        
        if "use tool" in user_input.lower() or "execute tool" in user_input.lower():
            # Very basic parsing - in real implementation, use LLM
            for name in self.mcp_tools.keys():
                if name.lower() in user_input.lower():
                    tool_name = name
                    tool = self.get_mcp_tool(name)
                    if tool and "schema" in tool:
                        # Try to extract parameters from the user input
                        tool_params = self.parameter_transformer.extract_parameters(
                            user_input, tool["schema"]
                        )
                    break
        
        if tool_name:
            # Execute the tool and return results
            result = await self.execute_mcp_tool(tool_name, tool_params)
            
            # Format the response
            response = f"Executed tool: {tool_name}\n\n"
            if result.get("is_success", False):
                response += f"Result: {json.dumps(result.get('result', {}), indent=2)}"
            else:
                response += f"Error: {result.get('error', 'Unknown error')}"
            
            return response
        
        # Default response if no tool execution
        return f"I understand your request: '{user_input}'. To use MCP tools, please specify a tool name."
    
    async def execute_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool with parameters"""
        try:
            # Find the tool
            tool = self.get_mcp_tool(tool_name)
            if not tool:
                return {
                    "is_success": False,
                    "error": f"Tool not found: {tool_name}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get the tool category
            category = "default"
            server_name, server_tool = self.mcp_client.find_tool_by_name(tool_name)
            if server_tool:
                # Use the tool factory to determine category
                category = self.tool_factory._determine_category(tool_name, server_tool)
            
            # Validate parameters
            if "schema" in tool:
                is_valid, error = self.parameter_validator.validate_against_schema(params, tool["schema"])
                if not is_valid:
                    return {
                        "is_success": False,
                        "error": f"Invalid parameters: {error}",
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Preprocess parameters
            processed_params = self.category_handlers.preprocess_params(category, tool_name, params)
            
            # Execute the tool
            response = await self.tool_executor.execute(tool_name, **processed_params)
            
            # Format the result
            formatted_response = self.category_handlers.format_result(category, tool_name, response)
            
            # Add to execution history
            self.tool_execution_history.append({
                "tool_name": tool_name,
                "params": params,
                "processed_params": processed_params,
                "timestamp": datetime.now().isoformat(),
                "response": {
                    "is_success": formatted_response.is_success,
                    "error": formatted_response.error,
                    "result": formatted_response.result
                }
            })
            
            # Return a dict with the result
            return {
                "is_success": formatted_response.is_success,
                "result": formatted_response.result,
                "error": formatted_response.error,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "is_success": False,
                "error": f"Error executing tool: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def suggest_tools(self, user_input: str) -> List[Dict[str, Any]]:
        """
        Suggest tools that might be relevant for the user input.
        This is a simple keyword-based implementation.
        In a real system, you'd use an LLM to determine relevant tools.
        """
        suggestions = []
        
        # Extract keywords from input
        keywords = user_input.lower().split()
        
        # Map of keywords to tool categories
        keyword_mappings = {
            "browser": ["browser", "web", "website", "url", "navigate", "click", "type", "browse"],
            "devops": ["work", "item", "task", "bug", "project", "azure", "devops"],
            "filesystem": ["file", "folder", "directory", "read", "write", "create", "list"],
            "search": ["search", "find", "lookup", "google", "query"],
        }
        
        # Find matching categories
        matching_categories = set()
        for category, category_keywords in keyword_mappings.items():
            for keyword in keywords:
                if keyword in category_keywords or any(k in keyword for k in category_keywords):
                    matching_categories.add(category)
        
        # If no categories match, try to match tools directly
        if not matching_categories:
            for tool_name, tool in self.mcp_tools.items():
                name_words = tool_name.lower().split('_')
                for word in name_words:
                    if word in keywords or any(k in word for k in keywords):
                        category = self.tool_factory._determine_category(tool_name, tool)
                        matching_categories.add(category)
        
        # Get tools from matching categories
        for category in matching_categories:
            tools = self.tool_registry.get_tools_by_category(category)
            suggestions.extend(tools[:3])  # Limit to 3 tools per category
        
        return suggestions[:5]  # Return up to 5 tools total
    
    def get_tool_execution_history(self) -> List[Dict[str, Any]]:
        """Get the tool execution history"""
        return self.tool_execution_history
