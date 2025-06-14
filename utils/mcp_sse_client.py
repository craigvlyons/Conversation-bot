"""
SSE (Server-Sent Events) MCP Client
Handles communication with MCP servers that use SSE transport protocol.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, AsyncGenerator
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SSEMessage:
    """Represents a Server-Sent Event message."""
    event: Optional[str] = None
    data: Optional[str] = None
    id: Optional[str] = None
    retry: Optional[int] = None

class MCPSSEClient:
    """
    MCP client that communicates using Server-Sent Events (SSE).
    Handles the SSE transport layer for MCP communication.
    """
    
    def __init__(self, base_url: str):
        # Handle URLs that end with /sse
        if base_url.endswith('/sse'):
            self.sse_url = base_url
            self.base_url = base_url[:-4]  # Remove /sse for JSON-RPC endpoint
        else:
            self.base_url = base_url.rstrip('/')
            self.sse_url = f"{self.base_url}/sse"
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.connected = False
        self.request_id = 1
        
    async def connect(self) -> bool:
        """Establish connection to the SSE endpoint."""
        try:
            if self.session is None:
                timeout = aiohttp.ClientTimeout(total=30, sock_read=30)
                self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Test basic connectivity
            logger.info(f"Testing SSE connection to {self.sse_url}")
            async with self.session.get(self.sse_url) as response:
                if response.status == 200:
                    self.connected = True
                    logger.info(f"✅ SSE connection established to {self.sse_url}")
                    return True
                else:
                    logger.error(f"❌ SSE connection failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ SSE connection error: {e}")
            return False
    
    async def disconnect(self):
        """Close the SSE connection."""
        if self.session:
            await self.session.close()
            self.session = None
        self.connected = False
        
    async def initialize_mcp(self) -> Dict[str, Any]:
        """Initialize MCP session with the server."""
        try:
            logger.info("🔧 Initializing MCP session via SSE...")
            
            init_request = {
                "jsonrpc": "2.0",
                "id": self._get_request_id(),
                "method": "initialize",
                "params": {
                    "capabilities": {
                        "experimental": {},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "conversation-bot",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send initialization request
            response = await self._send_request(init_request)
            
            if response and "result" in response:
                logger.info("✅ MCP initialization successful")
                return response["result"]
            else:
                logger.error(f"❌ MCP initialization failed: {response}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ MCP initialization error: {e}")
            return {}
    
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools from the MCP server."""
        try:
            logger.info("🔍 Discovering tools via SSE...")
            
            tools_request = {
                "jsonrpc": "2.0",
                "id": self._get_request_id(),
                "method": "getTools",  # Correct method name for this Azure DevOps server
                "params": {}
            }
            
            response = await self._send_request(tools_request)
            
            if response and "result" in response:
                # Handle different response formats
                result = response["result"]
                if isinstance(result, list):
                    # Direct array of tools
                    tools = result
                else:
                    # Tools nested in result.tools
                    tools = result.get("tools", [])
                
                logger.info(f"✅ Discovered {len(tools)} tools via SSE")
                return tools
            else:
                logger.warning(f"⚠️ No tools found in SSE response: {response}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Tool discovery error: {e}")
            return []
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on the MCP server."""
        try:
            logger.info(f"🔧 Executing tool '{tool_name}' via SSE...")
            
            tool_request = {
                "jsonrpc": "2.0",
                "id": self._get_request_id(),
                "method": "callTool",  # Correct method name for this Azure DevOps server
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = await self._send_request(tool_request)
            
            if response and "result" in response:
                logger.info(f"✅ Tool '{tool_name}' executed successfully")
                return response["result"]
            elif response and "error" in response:
                error_msg = response["error"].get("message", "Unknown error")
                logger.error(f"❌ Tool execution failed: {error_msg}")
                return {"error": error_msg}
            else:
                logger.error(f"❌ Unexpected tool response: {response}")
                return {"error": "Unexpected response format"}
                
        except Exception as e:
            logger.error(f"❌ Tool execution error: {e}")
            return {"error": str(e)}
    
    async def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a JSON-RPC request to the SSE server and wait for response.
        Uses a hybrid approach: POST for requests, SSE for responses.
        """
        try:
            if not self.session:
                await self.connect()
            
            if not self.connected:
                logger.error("Not connected to SSE server")
                return None
            
            # Try the hybrid approach: POST request to /jsonrpc endpoint
            jsonrpc_url = f"{self.base_url}/jsonrpc"
            headers = {"Content-Type": "application/json"}
            
            logger.debug(f"📤 Sending request to {jsonrpc_url}: {request}")
            
            async with self.session.post(jsonrpc_url, json=request, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.debug(f"📥 Received response: {result}")
                    return result
                else:
                    logger.error(f"❌ Request failed: HTTP {response.status}")
                    response_text = await response.text()
                    logger.error(f"Response body: {response_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return None
    
    async def _listen_to_sse_stream(self) -> AsyncGenerator[SSEMessage, None]:
        """
        Listen to the SSE stream for real-time events.
        This is useful for notifications and streaming responses.
        """
        try:
            if not self.session:
                await self.connect()
            
            async with self.session.get(self.sse_url) as response:
                if response.status != 200:
                    logger.error(f"SSE stream failed: HTTP {response.status}")
                    return
                
                logger.info("📡 Listening to SSE stream...")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if not line or line.startswith(':'):
                        continue  # Skip empty lines and comments
                    
                    message = self._parse_sse_line(line)
                    if message:
                        yield message
                        
        except Exception as e:
            logger.error(f"SSE stream error: {e}")
    
    def _parse_sse_line(self, line: str) -> Optional[SSEMessage]:
        """Parse a single SSE line into an SSEMessage."""
        try:
            if ':' not in line:
                return None
            
            field, value = line.split(':', 1)
            value = value.lstrip()
            
            message = SSEMessage()
            
            if field == 'event':
                message.event = value
            elif field == 'data':
                message.data = value
            elif field == 'id':
                message.id = value
            elif field == 'retry':
                message.retry = int(value)
            
            return message
            
        except Exception as e:
            logger.warning(f"Failed to parse SSE line '{line}': {e}")
            return None
    
    def _get_request_id(self) -> int:
        """Get a unique request ID."""
        request_id = self.request_id
        self.request_id += 1
        return request_id
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the SSE connection and return status information."""
        try:
            start_time = time.time()
            
            # Test basic connection
            connected = await self.connect()
            connection_time = time.time() - start_time
            
            if not connected:
                return {
                    "connected": False,
                    "connection_time": connection_time,
                    "error": "Failed to establish connection"
                }
            
            # Test MCP initialization
            init_start = time.time()
            init_result = await self.initialize_mcp()
            init_time = time.time() - init_start
            
            # Test tool discovery
            tools_start = time.time()
            tools = await self.discover_tools()
            tools_time = time.time() - tools_start
            
            total_time = time.time() - start_time
            
            return {
                "connected": True,
                "connection_time": connection_time,
                "initialization_successful": bool(init_result),
                "initialization_time": init_time,
                "tools_discovered": len(tools),
                "tools_discovery_time": tools_time,
                "total_test_time": total_time,
                "tools": [tool.get("name", "unknown") for tool in tools]
            }
            
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "total_test_time": time.time() - start_time
            }
        finally:
            await self.disconnect()