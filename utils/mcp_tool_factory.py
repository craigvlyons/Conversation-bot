from typing import Dict, List, Any, Optional, Union, Callable, TypeVar, Generic, Tuple, Type
import json
import uuid
import time
import re
from dataclasses import dataclass, field

# Import the MCP Client
from utils.mcp_client import MCPClient, ToolResponse
from utils.mcp_tool_base import MCPToolBase, MCPExecuteTool, MCPUITool, MCPDevOpsTool, MCPFileSystemTool, MCPSearchTool

class MCPToolFactory:
    """
    Factory for creating MCP tool instances based on tool metadata.
    This eliminates the need to create manual wrapper classes for each tool.
    """
    
    # Category patterns for automatic categorization
    CATEGORY_PATTERNS = {
        "browser": [
            r"browser_", r"playwright", r"click", r"type", r"navigate", 
            r"screenshot", r"tab", r"hover", r"select"
        ],
        "devops": [
            r"azure", r"devops", r"work_item", r"pull_request", r"repository",
            r"pipeline", r"build", r"deploy"
        ],
        "filesystem": [
            r"file", r"directory", r"folder", r"path", r"read", r"write", 
            r"create", r"delete", r"list"
        ],
        "search": [
            r"search", r"find", r"query", r"lookup", r"discover"
        ],
        "utility": [
            r"util", r"format", r"convert", r"parse", r"transform"
        ]
    }
    
    # Map of category to tool class
    CATEGORY_CLASSES = {
        "browser": MCPUITool,
        "devops": MCPDevOpsTool,
        "filesystem": MCPFileSystemTool,
        "search": MCPSearchTool,
        "utility": MCPExecuteTool,
        "default": MCPExecuteTool
    }
    
    def __init__(self, client: MCPClient):
        self.client = client
        self.tool_cache: Dict[str, MCPToolBase] = {}
    
    def get_tool(self, tool_name: str, server_name: Optional[str] = None) -> Optional[MCPToolBase]:
        """
        Get a tool instance by name and optionally server name.
        If the tool is already cached, return the cached instance.
        Otherwise, create a new instance.
        """
        # Check cache first
        cache_key = f"{server_name or 'any'}:{tool_name}"
        if cache_key in self.tool_cache:
            return self.tool_cache[cache_key]
        
        # Find the tool metadata
        if server_name:
            server = self.client.get_server(server_name)
            if not server or not server.tools or tool_name not in server.tools:
                print(f"Tool {tool_name} not found on server {server_name}")
                return None
            tool_info = server.tools[tool_name]
        else:
            server_name, tool_info = self.client.find_tool_by_name(tool_name)
            if not server_name or not tool_info:
                print(f"Tool {tool_name} not found on any server")
                return None
        
        # Create a new tool instance
        tool = self._create_tool_instance(tool_name, server_name, tool_info)
        if tool:
            self.tool_cache[cache_key] = tool
        
        return tool
    
    def _create_tool_instance(self, tool_name: str, server_name: str, tool_info: Dict[str, Any]) -> Optional[MCPToolBase]:
        """Create a tool instance based on tool metadata"""
        try:
            # Determine the tool category
            category = self._determine_category(tool_name, tool_info)
            
            # Get the appropriate tool class for the category
            tool_class = self.CATEGORY_CLASSES.get(category, self.CATEGORY_CLASSES["default"])
            
            # Create the instance
            tool = tool_class(tool_name, self.client, server_name)
            
            # Set additional properties from tool_info
            tool.description = tool_info.get("description", "")
            tool.schema = tool_info.get("schema", {})
            
            # For specialized tools, set additional properties
            if isinstance(tool, MCPUITool):
                tool.ui_element_type = self._determine_ui_element_type(tool_name, tool_info)
            elif isinstance(tool, MCPDevOpsTool):
                tool.resource_type = self._determine_resource_type(tool_name, tool_info)
            elif isinstance(tool, MCPFileSystemTool):
                tool.file_operation = self._determine_file_operation(tool_name, tool_info)
            elif isinstance(tool, MCPSearchTool):
                tool.search_type = self._determine_search_type(tool_name, tool_info)
            
            return tool
            
        except Exception as e:
            print(f"Error creating tool instance: {e}")
            return None
    
    def _determine_category(self, tool_name: str, tool_info: Dict[str, Any]) -> str:
        """Determine the category of a tool based on its name and metadata"""
        name_lower = tool_name.lower()
        description = tool_info.get("description", "").lower()
        
        # Check each category pattern
        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, name_lower) or re.search(pattern, description):
                    return category
        
        # Default category
        return "default"
    
    def _determine_ui_element_type(self, tool_name: str, tool_info: Dict[str, Any]) -> str:
        """Determine the UI element type for a browser tool"""
        name_lower = tool_name.lower()
        
        if "click" in name_lower:
            return "button"
        elif "type" in name_lower:
            return "input"
        elif "select" in name_lower:
            return "select"
        elif "hover" in name_lower:
            return "element"
        elif "tab" in name_lower:
            return "tab"
        elif "navigate" in name_lower:
            return "navigation"
        elif "screenshot" in name_lower:
            return "screen"
        else:
            return "browser"
    
    def _determine_resource_type(self, tool_name: str, tool_info: Dict[str, Any]) -> str:
        """Determine the resource type for a DevOps tool"""
        name_lower = tool_name.lower()
        
        if "work_item" in name_lower:
            return "workitem"
        elif "pull_request" in name_lower:
            return "pullrequest"
        elif "repository" in name_lower:
            return "repository"
        elif "pipeline" in name_lower:
            return "pipeline"
        elif "build" in name_lower:
            return "build"
        elif "project" in name_lower:
            return "project"
        else:
            return "devops"
    
    def _determine_file_operation(self, tool_name: str, tool_info: Dict[str, Any]) -> str:
        """Determine the file operation for a file system tool"""
        name_lower = tool_name.lower()
        
        if "read" in name_lower:
            return "read"
        elif "write" in name_lower or "create" in name_lower:
            return "write"
        elif "delete" in name_lower:
            return "delete"
        elif "list" in name_lower:
            return "list"
        elif "copy" in name_lower:
            return "copy"
        elif "move" in name_lower:
            return "move"
        else:
            return "filesystem"
    
    def _determine_search_type(self, tool_name: str, tool_info: Dict[str, Any]) -> str:
        """Determine the search type for a search tool"""
        name_lower = tool_name.lower()
        
        if "web" in name_lower:
            return "web"
        elif "code" in name_lower:
            return "code"
        elif "document" in name_lower:
            return "document"
        elif "semantic" in name_lower:
            return "semantic"
        else:
            return "general"


class MCPToolExecutor:
    """
    Unified executor for MCP tools.
    Provides a consistent interface for executing any MCP tool.
    """
    
    def __init__(self, factory: MCPToolFactory):
        self.factory = factory
    
    async def execute(self, tool_name: str, **kwargs) -> ToolResponse:
        """
        Execute a tool by name with the given parameters.
        This is the main entry point for tool execution.
        """
        # Get the tool instance
        tool = self.factory.get_tool(tool_name)
        if not tool:
            return ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=tool_name,
                result=None,
                is_success=False,
                error=f"Tool not found: {tool_name}"
            )
        
        # Execute the tool
        return await tool.execute(**kwargs)
    
    async def execute_with_server(self, server_name: str, tool_name: str, **kwargs) -> ToolResponse:
        """Execute a tool on a specific server"""
        # Get the tool instance from the specific server
        tool = self.factory.get_tool(tool_name, server_name)
        if not tool:
            return ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=tool_name,
                result=None,
                is_success=False,
                error=f"Tool {tool_name} not found on server {server_name}"
            )
        
        # Execute the tool
        return await tool.execute(**kwargs)
    
    async def execute_with_validation(self, tool_name: str, **kwargs) -> ToolResponse:
        """Execute a tool with additional parameter validation"""
        # Get the tool instance
        tool = self.factory.get_tool(tool_name)
        if not tool:
            return ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=tool_name,
                result=None,
                is_success=False,
                error=f"Tool not found: {tool_name}"
            )
        
        # Validate parameters
        is_valid, error = tool.validate_parameters(kwargs)
        if not is_valid:
            return ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=tool_name,
                result=None,
                is_success=False,
                error=error
            )
        
        # Execute the tool
        return await tool.execute(**kwargs)
