"""
WebSocket MCP Client
Handles communication with MCP servers that use WebSocket transport protocol.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PendingRequest:
    """Represents a pending JSON-RPC request."""
    id: int
    future: asyncio.Future
    method: str
    timestamp: float

class MCPWebSocketClient:
    """
    MCP client that communicates using WebSocket transport.
    Implements the full MCP protocol over WebSocket connections.
    """
    
    def __init__(self, url: str):
        self.url = url
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        self.request_id = 1
        self.pending_requests: Dict[int, PendingRequest] = {}
        self.event_handlers: Dict[str, Callable] = {}
        self._listen_task: Optional[asyncio.Task] = None
        
    async def connect(self) -> bool:
        """Establish WebSocket connection to the MCP server."""
        try:
            logger.info(f"🔌 Connecting to WebSocket MCP server: {self.url}")
            
            # Convert HTTP URL to WebSocket URL if needed
            ws_url = self.url
            if ws_url.startswith('http://'):
                ws_url = ws_url.replace('http://', 'ws://')
            elif ws_url.startswith('https://'):
                ws_url = ws_url.replace('https://', 'wss://')
            elif not ws_url.startswith(('ws://', 'wss://')):
                ws_url = f"ws://{ws_url}"
            
            # Establish connection
            self.websocket = await websockets.connect(
                ws_url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.connected = True
            logger.info(f"✅ WebSocket connected to {ws_url}")
            
            # Start listening for messages
            self._listen_task = asyncio.create_task(self._listen_for_messages())
            
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Close the WebSocket connection."""
        try:
            self.connected = False
            
            # Cancel listening task
            if self._listen_task:
                self._listen_task.cancel()
                try:
                    await self._listen_task
                except asyncio.CancelledError:
                    pass
            
            # Close WebSocket
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            
            # Cancel pending requests
            for request in self.pending_requests.values():
                if not request.future.done():
                    request.future.cancel()
            
            self.pending_requests.clear()
            logger.info("🔌 WebSocket disconnected")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def initialize_mcp(self) -> Dict[str, Any]:
        """Initialize MCP session with the server."""
        try:
            logger.info("🔧 Initializing MCP session via WebSocket...")
            
            init_request = {
                "jsonrpc": "2.0",
                "id": self._get_request_id(),
                "method": "initialize",
                "params": {
                    "capabilities": {
                        "experimental": {},
                        "sampling": {},
                        "tools": {"listChanged": True}
                    },
                    "clientInfo": {
                        "name": "conversation-bot",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await self._send_request(init_request)
            
            if response and "result" in response:
                logger.info("✅ MCP initialization successful")
                
                # Send initialized notification
                await self._send_notification({
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {}
                })
                
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
            logger.info("🔍 Discovering tools via WebSocket...")
            
            tools_request = {
                "jsonrpc": "2.0",
                "id": self._get_request_id(),
                "method": "tools/list",
                "params": {}
            }
            
            response = await self._send_request(tools_request)
            
            if response and "result" in response:
                tools = response["result"].get("tools", [])
                logger.info(f"✅ Discovered {len(tools)} tools via WebSocket")
                return tools
            else:
                logger.warning(f"⚠️ No tools found in WebSocket response: {response}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Tool discovery error: {e}")
            return []
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on the MCP server."""
        try:
            logger.info(f"🔧 Executing tool '{tool_name}' via WebSocket...")
            
            tool_request = {
                "jsonrpc": "2.0",
                "id": self._get_request_id(),
                "method": "tools/call",
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
    
    async def _send_request(self, request: Dict[str, Any], timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Send a JSON-RPC request and wait for response."""
        if not self.connected or not self.websocket:
            logger.error("WebSocket not connected")
            return None
        
        request_id = request.get("id")
        if request_id is None:
            logger.error("Request missing ID")
            return None
        
        try:
            # Create future for response
            future = asyncio.Future()
            pending_request = PendingRequest(
                id=request_id,
                future=future,
                method=request.get("method", "unknown"),
                timestamp=time.time()
            )
            
            self.pending_requests[request_id] = pending_request
            
            # Send request
            message = json.dumps(request)
            await self.websocket.send(message)
            logger.debug(f"📤 Sent WebSocket request: {request}")
            
            # Wait for response
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Request {request_id} timed out after {timeout}s")
            self.pending_requests.pop(request_id, None)
            return None
        except Exception as e:
            logger.error(f"Request {request_id} failed: {e}")
            self.pending_requests.pop(request_id, None)
            return None
    
    async def _send_notification(self, notification: Dict[str, Any]):
        """Send a JSON-RPC notification (no response expected)."""
        if not self.connected or not self.websocket:
            logger.error("WebSocket not connected")
            return
        
        try:
            message = json.dumps(notification)
            await self.websocket.send(message)
            logger.debug(f"📤 Sent WebSocket notification: {notification}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    async def _listen_for_messages(self):
        """Listen for incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    
        except ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.connected = False
        except WebSocketException as e:
            logger.error(f"WebSocket error: {e}")
            self.connected = False
        except Exception as e:
            logger.error(f"Unexpected error in message listener: {e}")
            self.connected = False
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket message."""
        try:
            logger.debug(f"📥 Received WebSocket message: {data}")
            
            # Handle responses to requests
            if "id" in data:
                request_id = data["id"]
                pending_request = self.pending_requests.pop(request_id, None)
                
                if pending_request and not pending_request.future.done():
                    pending_request.future.set_result(data)
                elif pending_request is None:
                    logger.warning(f"Received response for unknown request ID: {request_id}")
            
            # Handle notifications
            elif "method" in data:
                method = data["method"]
                params = data.get("params", {})
                
                # Call registered event handler if available
                handler = self.event_handlers.get(method)
                if handler:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(params)
                        else:
                            handler(params)
                    except Exception as e:
                        logger.error(f"Error in event handler for {method}: {e}")
                else:
                    logger.debug(f"No handler for notification: {method}")
            
            else:
                logger.warning(f"Unknown message format: {data}")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    def register_event_handler(self, method: str, handler: Callable):
        """Register a handler for server notifications."""
        self.event_handlers[method] = handler
    
    def _get_request_id(self) -> int:
        """Get a unique request ID."""
        request_id = self.request_id
        self.request_id += 1
        return request_id
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the WebSocket connection and return status information."""
        try:
            start_time = time.time()
            
            # Test connection
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
                "tools": [tool.get("name", "unknown") for tool in tools],
                "server_capabilities": init_result.get("capabilities", {})
            }
            
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "total_test_time": time.time() - start_time
            }
        finally:
            await self.disconnect()
    
    async def ping(self) -> bool:
        """Send a ping to test connection health."""
        try:
            if not self.connected or not self.websocket:
                return False
            
            await self.websocket.ping()
            return True
        except Exception:
            return False