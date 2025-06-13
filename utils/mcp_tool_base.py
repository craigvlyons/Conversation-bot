from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable, TypeVar, Generic, Tuple
import json
import uuid
import time
from dataclasses import dataclass, field

# Import the MCP Client
from utils.mcp_client import MCPClient, ToolResponse

T = TypeVar('T')

class MCPToolBase(ABC):
    """Base class for all MCP tools"""
    
    def __init__(self, name: str, client: MCPClient, server_name: Optional[str] = None):
        self.name = name
        self.client = client
        self.server_name = server_name
        self.description = ""
        self.schema = {}
        
        # Try to find the tool by name if server_name is not provided
        if not self.server_name:
            server_name, tool_info = self.client.find_tool_by_name(name)
            if server_name:
                self.server_name = server_name
                if tool_info:
                    self.description = tool_info.get("description", "")
                    self.schema = tool_info.get("schema", {})
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the tool with the given parameters"""
        pass
    
    def validate_parameters(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate parameters against the schema"""
        # Basic validation - in a real implementation you'd use a proper JSON schema validator
        if not self.schema:
            return True, ""
        
        required_props = self.schema.get("properties", {})
        required = self.schema.get("required", [])
        
        # Check required properties
        for prop in required:
            if prop not in params:
                return False, f"Missing required parameter: {prop}"
        
        return True, ""


class MCPExecuteTool(MCPToolBase):
    """Basic implementation that directly executes an MCP tool"""
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the tool with the given parameters"""
        if not self.server_name:
            return ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=self.name,
                result=None,
                is_success=False,
                error="Tool server not found"
            )
        
        # Validate parameters
        is_valid, error = self.validate_parameters(kwargs)
        if not is_valid:
            return ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=self.name,
                result=None,
                is_success=False,
                error=error
            )
        
        # Execute the tool
        return await self.client.execute_tool(self.server_name, self.name, kwargs)


class MCPStreamingTool(MCPToolBase):
    """Base class for streaming MCP tools"""
    
    async def execute_streaming(self, **kwargs):
        """Execute the tool with streaming results"""
        if not self.server_name:
            yield ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=self.name,
                result=None,
                is_success=False,
                error="Tool server not found",
                is_streaming=True,
                is_complete=True
            )
            return
        
        # Validate parameters
        is_valid, error = self.validate_parameters(kwargs)
        if not is_valid:
            yield ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=self.name,
                result=None,
                is_success=False,
                error=error,
                is_streaming=True,
                is_complete=True
            )
            return
        
        # Execute the streaming tool
        async for response in self.client.execute_streaming_tool(self.server_name, self.name, kwargs):
            yield response

    async def execute(self, **kwargs) -> ToolResponse:
        """Non-streaming execution (collects all streaming responses)"""
        last_response = None
        combined_result = []
        
        async for response in self.execute_streaming(**kwargs):
            last_response = response
            if response.result is not None:
                combined_result.append(response.result)
        
        if last_response:
            # Modify the last response to contain the combined result
            last_response.result = combined_result
            return last_response
        
        # If we got no responses, return an error
        return ToolResponse(
            id=str(uuid.uuid4()),
            tool_name=self.name,
            result=None,
            is_success=False,
            error="No response from streaming tool",
            is_streaming=False,
            is_complete=True
        )


class MCPUITool(MCPExecuteTool):
    """Base class for UI-related tools (e.g., browser tools)"""
    
    def __init__(self, name: str, client: MCPClient, server_name: Optional[str] = None):
        super().__init__(name, client, server_name)
        self.ui_element_type = "generic"  # Can be 'browser', 'form', 'button', etc.
    
    async def get_ui_state(self) -> Dict[str, Any]:
        """Get the current UI state (to be implemented by subclasses)"""
        return {}
    
    async def execute_with_ui_state(self, ui_state: Dict[str, Any], **kwargs) -> ToolResponse:
        """Execute the tool with UI state information"""
        # Merge UI state with kwargs if needed
        return await self.execute(**kwargs)


class MCPDevOpsTool(MCPExecuteTool):
    """Base class for DevOps-related tools"""
    
    def __init__(self, name: str, client: MCPClient, server_name: Optional[str] = None):
        super().__init__(name, client, server_name)
        self.resource_type = "generic"  # Can be 'workitem', 'project', 'repository', etc.
    
    async def format_result(self, response: ToolResponse) -> ToolResponse:
        """Format the result in a more user-friendly way"""
        # Subclasses can override this to provide better formatting
        return response


class MCPFileSystemTool(MCPExecuteTool):
    """Base class for file system tools"""
    
    def __init__(self, name: str, client: MCPClient, server_name: Optional[str] = None):
        super().__init__(name, client, server_name)
        self.file_operation = "generic"  # Can be 'read', 'write', 'list', etc.


class MCPSearchTool(MCPExecuteTool):
    """Base class for search tools"""
    
    def __init__(self, name: str, client: MCPClient, server_name: Optional[str] = None):
        super().__init__(name, client, server_name)
        self.search_type = "generic"  # Can be 'web', 'code', 'document', etc.
