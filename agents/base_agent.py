from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Tuple
import asyncio


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Each agent must implement the `get_response` method.
    Optionally, agents can handle memory, tools, and chat history.
    """

    def __init__(self, name: str = "base", tools: Optional[list] = None):
        self.name = name
        self.tools = tools or []
        self.mcp_tools: Dict[str, Any] = {}
        self.mcp_enabled = False

    @abstractmethod
    async def get_response(self, user_input: str, history: Optional[str] = None) -> Any:
        """
        Generate a response based on user input (and optionally conversation history).
        Must be implemented by subclasses.
        """
        pass

    def name(self) -> str:
        """Return the name of the agent."""
        return self.name

    def register_tool(self, tool):
        """Optionally allow tools to be registered dynamically."""
        self.tools.append(tool)
    
    def register_mcp_tool(self, tool_name: str, tool_metadata: Dict[str, Any]):
        """Register an MCP tool with metadata."""
        self.mcp_tools[tool_name] = tool_metadata
    
    def register_mcp_tools(self, tools: Dict[str, Dict[str, Any]]):
        """Register multiple MCP tools at once."""
        self.mcp_tools.update(tools)
    
    def get_mcp_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get an MCP tool by name."""
        return self.mcp_tools.get(tool_name)
    
    def get_all_mcp_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered MCP tools."""
        return self.mcp_tools
    
    def get_mcp_tools_for_prompt(self) -> str:
        """Get MCP tools formatted for inclusion in prompts."""
        tools_str = ""
        for name, tool in self.mcp_tools.items():
            description = tool.get("description", "No description")
            tools_str += f"- {name}: {description}\n"
        return tools_str
    
    def get_mcp_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all MCP tools in OpenAI function format."""
        schemas = []
        for name, tool in self.mcp_tools.items():
            if "schema" in tool:
                schema = {
                    "name": name,
                    "description": tool.get("description", ""),
                    "parameters": tool.get("schema", {}),
                }
                schemas.append(schema)
        return schemas
    
    def enable_mcp(self):
        """Enable MCP functionality."""
        self.mcp_enabled = True
    
    def disable_mcp(self):
        """Disable MCP functionality."""
        self.mcp_enabled = False
    
    async def execute_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool. Must be implemented by MCP-aware agents.
        Default implementation raises NotImplementedError.
        """
        raise NotImplementedError("This agent does not support MCP tool execution")