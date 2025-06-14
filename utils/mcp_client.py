import os
import json
import asyncio
import aiohttp
import websockets
from typing import Dict, List, Any, Optional, Union, Tuple
import uuid
import time
from dataclasses import dataclass, field

# Import the MCP Server Manager to use its MCPServer class
from utils.mcp_server_manager import MCPServer

@dataclass
class ToolResponse:
    """Class to represent a response from an MCP tool execution"""
    id: str
    tool_name: str
    result: Any
    is_success: bool = True
    error: Optional[str] = None
    server_name: Optional[str] = None
    execution_time: float = 0.0
    timestamp: float = field(default_factory=time.time)
    is_complete: bool = True
    is_streaming: bool = False
    stream_data: List[Any] = field(default_factory=list)

class MCPClient:
    """MCP protocol client for executing tools on MCP servers"""
    
    def __init__(self, servers: Optional[Dict[str, MCPServer]] = None):
        self.servers = servers or {}
    
    def set_servers(self, servers: Dict[str, MCPServer]):
        """Set the servers dictionary"""
        self.servers = servers
    
    def add_server(self, server: MCPServer):
        """Add a server to the client"""
        self.servers[server.name] = server
    
    def remove_server(self, name: str):
        """Remove a server from the client"""
        if name in self.servers:
            del self.servers[name]
    
    def get_server(self, name: str) -> Optional[MCPServer]:
        """Get a server by name"""
        return self.servers.get(name)
    
    def get_all_servers(self) -> Dict[str, MCPServer]:
        """Get all servers"""
        return self.servers
    
    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all tools from all servers"""
        tools = {}
        for server_name, server in self.servers.items():
            if server.tools:
                for tool_name, tool in server.tools.items():
                    # Add the server name to the tool info
                    tool_info = tool.copy()
                    tool_info["server"] = server_name
                    tools[tool_name] = tool_info
        return tools
    
    async def execute_tool(self, server_name: str, tool_name: str, params: Dict[str, Any]) -> ToolResponse:
        """Execute a tool on a specific server"""
        if server_name not in self.servers:
            return ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=tool_name,
                result=None,
                is_success=False,
                error=f"Server not found: {server_name}",
                server_name=server_name
            )
        
        server = self.servers[server_name]
        if not server.tools or tool_name not in server.tools:
            return ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=tool_name,
                result=None,
                is_success=False,
                error=f"Tool not found: {tool_name}",
                server_name=server_name
            )
        
        tool = server.tools[tool_name]
        request_id = str(uuid.uuid4())
        
        start_time = time.time()
        try:
            result = await self._send_tool_request(server, tool_name, params, request_id)
            execution_time = time.time() - start_time
            
            if result is None:
                return ToolResponse(
                    id=request_id,
                    tool_name=tool_name,
                    result=None,
                    is_success=False,
                    error="Failed to execute tool: No response",
                    server_name=server_name,
                    execution_time=execution_time
                )
            
            if "error" in result:
                return ToolResponse(
                    id=request_id,
                    tool_name=tool_name,
                    result=None,
                    is_success=False,
                    error=f"Tool execution failed: {result['error']}",
                    server_name=server_name,
                    execution_time=execution_time
                )
            
            return ToolResponse(
                id=request_id,
                tool_name=tool_name,
                result=result.get("result"),
                is_success=True,
                server_name=server_name,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResponse(
                id=request_id,
                tool_name=tool_name,
                result=None,
                is_success=False,
                error=f"Exception during tool execution: {str(e)}",
                server_name=server_name,
                execution_time=execution_time
            )
    
    async def _send_tool_request(self, server: MCPServer, tool_name: str, params: Dict[str, Any], request_id: str = None) -> Optional[Dict[str, Any]]:
        """Send a tool execution request to the server"""
        if request_id is None:
            request_id = str(uuid.uuid4())
            
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/execute",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        try:
            # If server has a URL, prefer HTTP communication
            if server.url:
                # For MCP servers, send to the JSON-RPC endpoint
                jsonrpc_url = f"{server.url.rstrip('/')}/jsonrpc"
                
                async with aiohttp.ClientSession() as session:
                    headers = {"Content-Type": "application/json"}
                    async with session.post(jsonrpc_url, json=request, headers=headers) as response:
                        if response.status != 200:
                            return {"error": f"HTTP request failed: {response.status}"}
                        
                        response_data = await response.json()
                        if "error" in response_data:
                            return {"error": response_data["error"]}
                        return {"result": response_data.get("result")}
            
            # If no URL but server has a process, try process communication
            elif server.process and hasattr(server.process, "stdin") and hasattr(server.process, "stdout"):
                # Process stdin/stdout communication requires async capabilities
                request_json = json.dumps(request) + "\n"
                
                # Check if we can write to stdin
                if hasattr(server.process.stdin, "write"):
                    # Write the request
                    server.process.stdin.write(request_json.encode())
                    if hasattr(server.process.stdin, "flush"):
                        server.process.stdin.flush()
                    
                    # Read response (this is not ideal for async but works for testing)
                    # We should use asyncio.StreamReader/StreamWriter in production
                    import io
                    try:
                        # Try to read all available output
                        response_line = server.process.stdout.readline()
                        if response_line:
                            response_data = json.loads(response_line.decode().strip())
                            if "error" in response_data:
                                return {"error": response_data["error"]}
                            return {"result": response_data.get("result")}
                    except (io.UnsupportedOperation, AttributeError, ValueError) as e:
                        return {"error": f"Process communication error: {str(e)}"}
            
            return {"error": "No valid communication method available"}
            
        except Exception as e:
            return {"error": f"Error sending tool request: {str(e)}"}
    
    async def execute_streaming_tool(self, server_name: str, tool_name: str, params: Dict[str, Any]):
        """Execute a tool that can stream responses"""
        # For streaming tools, we'll use the WebSocket connection if available
        # and implement a generator that yields results as they come
        if server_name not in self.servers:
            yield ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=tool_name,
                result=None,
                is_success=False,
                error=f"Server not found: {server_name}",
                server_name=server_name,
                is_streaming=True,
                is_complete=False
            )
            return
        
        server = self.servers[server_name]
        if not server.tools or tool_name not in server.tools:
            yield ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=tool_name,
                result=None,
                is_success=False,
                error=f"Tool not found: {tool_name}",
                server_name=server_name,
                is_streaming=True,
                is_complete=False
            )
            return
        
        # Only support WebSocket streaming for now
        if not server.websocket:
            yield ToolResponse(
                id=str(uuid.uuid4()),
                tool_name=tool_name,
                result=None,
                is_success=False,
                error="Streaming only supported for WebSocket connections",
                server_name=server_name,
                is_streaming=True,
                is_complete=False
            )
            return
        
        request_id = str(uuid.uuid4())
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/execute",
            "params": {
                "name": tool_name,
                "arguments": params,
                "stream": True  # Request streaming response
            }
        }
        
        start_time = time.time()
        stream_data = []
        
        try:
            await server.websocket.send(json.dumps(request))
            
            # Keep receiving messages until we get a completion message
            while True:
                response = await server.websocket.recv()
                response_data = json.loads(response)
                
                if "error" in response_data:
                    execution_time = time.time() - start_time
                    yield ToolResponse(
                        id=request_id,
                        tool_name=tool_name,
                        result=None,
                        is_success=False,
                        error=f"Tool execution failed: {response_data['error']}",
                        server_name=server_name,
                        execution_time=execution_time,
                        is_streaming=True,
                        is_complete=True,
                        stream_data=stream_data
                    )
                    break
                
                if "result" in response_data:
                    # This might be a partial or final result
                    partial_result = response_data["result"]
                    stream_data.append(partial_result)
                    
                    is_complete = response_data.get("complete", False)
                    execution_time = time.time() - start_time
                    
                    yield ToolResponse(
                        id=request_id,
                        tool_name=tool_name,
                        result=partial_result,
                        is_success=True,
                        server_name=server_name,
                        execution_time=execution_time,
                        is_streaming=True,
                        is_complete=is_complete,
                        stream_data=stream_data
                    )
                    
                    if is_complete:
                        break
        
        except Exception as e:
            execution_time = time.time() - start_time
            yield ToolResponse(
                id=request_id,
                tool_name=tool_name,
                result=None,
                is_success=False,
                error=f"Exception during streaming tool execution: {str(e)}",
                server_name=server_name,
                execution_time=execution_time,
                is_streaming=True,
                is_complete=True,
                stream_data=stream_data
            )
    
    def find_tool_by_name(self, tool_name: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Find a tool by name across all servers"""
        for server_name, server in self.servers.items():
            if server.tools and tool_name in server.tools:
                return server_name, server.tools[tool_name]
        return None, None
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get the schema for a tool"""
        server_name, tool = self.find_tool_by_name(tool_name)
        if tool:
            return tool.get("schema")
        return None
    
    def categorize_tools(self) -> Dict[str, List[str]]:
        """Categorize tools by type or functionality"""
        categories = {
            "browser": [],
            "devops": [],
            "filesystem": [],
            "search": [],
            "other": []
        }
        
        for tool_name, tool in self.get_all_tools().items():
            # Categorize based on name, description, or server
            if tool_name.startswith("browser_") or "playwright" in tool.get("server", ""):
                categories["browser"].append(tool_name)
            elif "devops" in tool_name.lower() or "azure-devops" in tool.get("server", ""):
                categories["devops"].append(tool_name)
            elif "file" in tool_name.lower() or "filesystem" in tool.get("server", ""):
                categories["filesystem"].append(tool_name)
            elif "search" in tool_name.lower() or "brave-search" in tool.get("server", ""):
                categories["search"].append(tool_name)
            else:
                categories["other"].append(tool_name)
        
        return categories
