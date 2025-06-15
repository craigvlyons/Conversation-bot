"""
Unified MCP Protocol Client
Automatically detects server protocol and uses the appropriate client (SSE, WebSocket, HTTP).
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from utils.mcp_sse_client import MCPSSEClient
from utils.mcp_websocket_client import MCPWebSocketClient
from utils.mcp_server_manager import MCPServer

logger = logging.getLogger(__name__)

class ProtocolType(Enum):
    SSE = "sse"
    WEBSOCKET = "websocket" 
    HTTP = "http"
    STDIO = "stdio"
    UNKNOWN = "unknown"

class MCPProtocolClient:
    """
    Unified MCP client that automatically detects the server protocol
    and uses the appropriate transport (SSE, WebSocket, or HTTP JSON-RPC).
    """
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.protocol_type = ProtocolType.UNKNOWN
        self.client: Optional[Union[MCPSSEClient, MCPWebSocketClient]] = None
        self.initialized = False
        
    async def auto_detect_and_connect(self) -> bool:
        """
        Automatically detect the server protocol and establish connection.
        """
        try:
            logger.info(f"🔍 Auto-detecting protocol for server: {self.server.id}")
            
            # Detect protocol type
            self.protocol_type = await self._detect_protocol()
            logger.info(f"📡 Detected protocol: {self.protocol_type.value}")
            
            # Create appropriate client
            if self.protocol_type == ProtocolType.SSE:
                self.client = MCPSSEClient(self.server.url)
            elif self.protocol_type == ProtocolType.WEBSOCKET:
                self.client = MCPWebSocketClient(self.server.url)
            elif self.protocol_type == ProtocolType.HTTP:
                # Use existing HTTP JSON-RPC approach via server manager
                logger.info("Using existing HTTP JSON-RPC client")
                return True
            else:
                logger.error(f"❌ Unsupported protocol type: {self.protocol_type}")
                return False
            
            # Connect using the appropriate client
            if self.client:
                connected = await self.client.connect()
                if connected:
                    # Initialize MCP session
                    init_result = await self.client.initialize_mcp()
                    self.initialized = bool(init_result)
                    
                    if self.initialized:
                        logger.info(f"✅ Successfully connected and initialized {self.server.id}")
                    else:
                        logger.warning(f"⚠️ Connected but initialization failed for {self.server.id}")
                    
                    return connected
                else:
                    logger.error(f"❌ Failed to connect to {self.server.id}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Auto-detection failed for {self.server.id}: {e}")
            return False
    
    async def _detect_protocol(self) -> ProtocolType:
        """
        Detect the MCP protocol type based on URL and server characteristics.
        """
        try:
            if not self.server.url:
                logger.warning(f"No URL provided for server {self.server.id}")
                return ProtocolType.UNKNOWN
            
            url = self.server.url.lower()
            
            # Check for SSE indicators
            if '/sse' in url or 'events' in url:
                logger.debug(f"SSE protocol detected from URL pattern: {url}")
                return ProtocolType.SSE
            
            # Check for WebSocket indicators
            if url.startswith(('ws://', 'wss://')):
                logger.debug(f"WebSocket protocol detected from URL scheme: {url}")
                return ProtocolType.WEBSOCKET
            
            # For process-based servers, try to detect from common patterns
            if self.server.process or self.server.command:
                # Most MCP servers launched via process use stdio for communication
                if 'playwright' in self.server.id.lower():
                    # Playwright MCP uses stdio (stdin/stdout) for communication
                    logger.debug("Playwright server detected, using stdio")
                    return ProtocolType.STDIO
                
                # Other npm-based MCP servers also typically use stdio
                if self.server.command and 'npx' in self.server.command:
                    logger.debug("NPX-based server detected, trying stdio first")
                    return ProtocolType.STDIO
            
            # Try to probe the server to determine protocol
            protocol = await self._probe_server_protocol()
            if protocol != ProtocolType.UNKNOWN:
                return protocol
            
            # Default fallback
            logger.debug(f"Using HTTP as default protocol for {self.server.id}")
            return ProtocolType.HTTP
            
        except Exception as e:
            logger.error(f"Protocol detection error: {e}")
            return ProtocolType.UNKNOWN
    
    async def _probe_server_protocol(self) -> ProtocolType:
        """
        Actively probe the server to determine its protocol.
        """
        if not self.server.url:
            return ProtocolType.UNKNOWN
        
        import aiohttp
        
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                
                # Test for SSE by looking for text/event-stream content type
                try:
                    async with session.get(self.server.url, headers={'Accept': 'text/event-stream'}) as response:
                        content_type = response.headers.get('content-type', '').lower()
                        if 'text/event-stream' in content_type or response.status == 200:
                            logger.debug("SSE protocol confirmed by probe")
                            return ProtocolType.SSE
                except:
                    pass
                
                # Test for standard HTTP JSON-RPC endpoint
                try:
                    base_url = self.server.url.rstrip('/')
                    jsonrpc_url = f"{base_url}/jsonrpc" if not base_url.endswith('/jsonrpc') else base_url
                    
                    test_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {"capabilities": {}}
                    }
                    
                    async with session.post(jsonrpc_url, json=test_request) as response:
                        if response.status in [200, 400, 404]:  # Any response indicates HTTP support
                            logger.debug("HTTP JSON-RPC protocol confirmed by probe")
                            return ProtocolType.HTTP
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"Server probe failed: {e}")
        
        return ProtocolType.UNKNOWN
    
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover tools using the appropriate protocol client."""
        try:
            if self.protocol_type == ProtocolType.HTTP:
                # Use server manager's HTTP discovery
                from utils.mcp_server_manager import MCPServerManager
                manager = MCPServerManager()
                return manager._discover_tools(self.server)
            
            elif self.client:
                return await self.client.discover_tools()
            
            else:
                logger.error(f"No client available for tool discovery on {self.server.id}")
                return []
                
        except Exception as e:
            logger.error(f"Tool discovery failed for {self.server.id}: {e}")
            return []
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool using the appropriate protocol client."""
        try:
            if self.protocol_type == ProtocolType.HTTP:
                # Use server manager's HTTP execution
                logger.warning("HTTP tool execution not yet implemented via server manager")
                return {"error": "HTTP tool execution not implemented"}
            
            elif self.client:
                return await self.client.execute_tool(tool_name, arguments)
            
            else:
                logger.error(f"No client available for tool execution on {self.server.id}")
                return {"error": "No client available"}
                
        except Exception as e:
            logger.error(f"Tool execution failed for {self.server.id}: {e}")
            return {"error": str(e)}
    
    async def disconnect(self):
        """Disconnect from the server."""
        try:
            if self.client:
                await self.client.disconnect()
                self.client = None
            self.initialized = False
            logger.debug(f"Disconnected from {self.server.id}")
        except Exception as e:
            logger.error(f"Disconnect error for {self.server.id}: {e}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection and return detailed status."""
        try:
            start_time = time.time()
            
            # Test auto-detection and connection
            connected = await self.auto_detect_and_connect()
            
            if not connected:
                return {
                    "server_id": self.server.id,
                    "connected": False,
                    "protocol": self.protocol_type.value,
                    "error": "Failed to connect",
                    "test_time": time.time() - start_time
                }
            
            # Test tool discovery
            tools_start = time.time()
            tools = await self.discover_tools()
            tools_time = time.time() - tools_start
            
            total_time = time.time() - start_time
            
            result = {
                "server_id": self.server.id,
                "connected": True,
                "protocol": self.protocol_type.value,
                "initialized": self.initialized,
                "tools_discovered": len(tools),
                "tools_discovery_time": tools_time,
                "total_test_time": total_time,
                "tools": [tool.get("name", "unknown") for tool in tools]
            }
            
            # Add protocol-specific details
            if self.client and hasattr(self.client, 'test_connection'):
                client_result = await self.client.test_connection()
                result.update(client_result)
            
            return result
            
        except Exception as e:
            return {
                "server_id": self.server.id,
                "connected": False,
                "protocol": self.protocol_type.value,
                "error": str(e),
                "test_time": time.time() - start_time
            }
        finally:
            await self.disconnect()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection information."""
        return {
            "server_id": self.server.id,
            "protocol": self.protocol_type.value,
            "connected": self.client is not None and getattr(self.client, 'connected', False),
            "initialized": self.initialized,
            "client_type": type(self.client).__name__ if self.client else None
        }