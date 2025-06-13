import os
import json
import asyncio
import aiohttp
import websockets
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import uuid

@dataclass
class MCPServer:
    """Represents an MCP server connection"""
    name: str
    url: Optional[str] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    description: Optional[str] = None
    process: Optional[asyncio.subprocess.Process] = None
    websocket: Optional[websockets.WebSocketClientProtocol] = None
    capabilities: Dict[str, Any] = None
    tools: Dict[str, Dict[str, Any]] = None
    prompts: Dict[str, Dict[str, Any]] = None
    resources: Dict[str, Dict[str, Any]] = None
    
    @property
    def is_running(self) -> bool:
        """Check if the server process is running"""
        if self.process is not None:
            return self.process.returncode is None
        return False
    
    @property
    def is_connected(self) -> bool:
        """Check if the server is connected"""
        if self.websocket is not None:
            return not self.websocket.closed
        return self.is_running


class MCPServerManager:
    """Manager class for MCP servers - handles loading, connecting, and managing MCP servers"""
    
    CONFIG_PATH = "mcp_servers.json"
    
    def __init__(self, config_path: Optional[str] = None):
        self.servers: Dict[str, MCPServer] = {}
        self.config_path = config_path or self.CONFIG_PATH
    
    async def load_servers_config(self) -> bool:
        """Load server configurations from file"""
        try:
            if not os.path.exists(self.config_path):
                print(f"❌ MCP servers config file not found: {self.config_path}")
                return False
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            for name, server_config in config.items():
                server = MCPServer(
                    name=name,
                    url=server_config.get("url"),
                    command=server_config.get("command"),
                    args=server_config.get("args"),
                    description=server_config.get("description")
                )
                self.servers[name] = server
            
            print(f"✅ Loaded {len(self.servers)} MCP servers from config")
            return True
            
        except Exception as e:
            print(f"❌ Error loading MCP servers config: {e}")
            return False
    
    async def connect_all_servers(self) -> Dict[str, bool]:
        """Connect to all configured servers"""
        results = {}
        
        for name, server in self.servers.items():
            print(f"Connecting to MCP server: {name}")
            success = await self.connect_server(name)
            results[name] = success
        
        return results
    
    async def connect_server(self, name: str) -> bool:
        """Connect to specific server by name"""
        if name not in self.servers:
            print(f"❌ Server not found: {name}")
            return False
        
        server = self.servers[name]
        try:
            success = False
            
            # Try URL connection first if available
            if server.url:
                print(f"🌐 Trying URL connection for {name}: {server.url}")
                success = await self._connect_via_url(server)
                
                if success:
                    print(f"✅ Connected to {name} via URL")
                else:
                    print(f"❌ URL connection failed for {name}")
            
            # Fall back to command if URL failed or not available
            if not success and server.command:
                print(f"🚀 Starting {name} via command: {server.command} {' '.join(server.args or [])}")
                success = await self._start_and_connect_process(server)
                
                if success:
                    print(f"✅ Started and connected to {name} via command")
                else:
                    print(f"❌ Command startup failed for {name}")
            
            if not success and not server.url and not server.command:
                print(f"❌ Invalid server config for {name}: missing 'url' or 'command'")
                return False
            
            if success:
                # Discover server capabilities
                await self._discover_capabilities(server)
                print(f"✅ Connected to MCP server: {name}")
                print(f"   Tools: {len(server.tools or {})}")
                print(f"   Prompts: {len(server.prompts or {})}")
                print(f"   Resources: {len(server.resources or {})}")
                return True
            else:
                print(f"❌ Failed to connect to MCP server: {name}")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to server {name}: {e}")
            return False
    
    async def _connect_via_url(self, server: MCPServer) -> bool:
        """Connect to MCP server via URL (WebSocket or HTTP SSE)"""
        try:
            if server.url.startswith("ws://") or server.url.startswith("wss://"):
                # WebSocket connection
                server.websocket = await websockets.connect(server.url)
                return True
            elif "/sse" in server.url:
                # HTTP SSE connection - establish session first
                async with aiohttp.ClientSession() as session:
                    # For FastMCP SSE, we need to establish a session by connecting to the SSE endpoint
                    try:
                        # First, try to establish SSE connection to create a session
                        async with session.get(
                            server.url, 
                            timeout=aiohttp.ClientTimeout(total=5),
                            headers={"Accept": "text/event-stream"}
                        ) as response:
                            if response.status == 200:
                                # SSE connection established, server should create a session
                                # Read the first few events to see if we get session info
                                async for line in response.content:
                                    if line:
                                        line_str = line.decode().strip()
                                        if line_str.startswith("data:"):
                                            # We got SSE data, connection is working
                                            return True
                                        elif len(line_str) > 0:
                                            # Got some response
                                            return True
                                    # Don't wait forever, just check if SSE is responsive
                                    break
                                return True
                    except asyncio.TimeoutError:
                        # Timeout is expected for SSE connections, means it's working
                        return True
                    except Exception as e:
                        print(f"SSE connection test failed: {e}")
                        return False
            else:
                print(f"Unsupported URL format: {server.url}")
                return False
        except Exception as e:
            print(f"Failed to connect via URL: {e}")
            return False
    
    async def _start_and_connect_process(self, server: MCPServer) -> bool:
        """Start MCP server process and connect to it"""
        try:
            # Start the server process
            cmd = [server.command] + (server.args or [])
            
            # Handle Windows npx command
            import platform
            if platform.system() == "Windows" and server.command == "npx":
                # On Windows, npx might be npx.cmd
                cmd[0] = "npx.cmd"
            
            print(f"Starting MCP server: {' '.join(cmd)}")
            
            server.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            
            # Give the server time to start
            await asyncio.sleep(3)
            
            # Check if process is running
            if server.process.returncode is not None:
                stderr = await server.process.stderr.read()
                stdout = await server.process.stdout.read()
                print(f"Server process failed to start:")
                print(f"  STDERR: {stderr.decode()}")
                print(f"  STDOUT: {stdout.decode()}")
                return False
            
            print(f"  ✅ Process started (PID: {server.process.pid})")
            return True
            
        except FileNotFoundError as e:
            print(f"Command not found: {server.command}")
            print(f"  Make sure Node.js and npm are installed for npx commands")
            print(f"  Error: {e}")
            return False
        except Exception as e:
            print(f"Failed to start server process: {e}")
            return False
    
    async def _discover_capabilities(self, server: MCPServer):
        """Discover tools, prompts, and resources from MCP server"""
        try:
            print(f"🔍 Discovering capabilities for {server.name}...")
            
            # Send initialize request
            init_response = await self._send_mcp_request(server, "initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "prompts": {},
                    "resources": {}
                },
                "clientInfo": {
                    "name": "convo-bot-mcp-client",
                    "version": "1.0.0"
                }
            })
            
            if init_response:
                server.capabilities = init_response.get("capabilities", {})
                print(f"  ✅ Initialized {server.name}")
            else:
                print(f"  ❌ Failed to initialize {server.name}")
                server.capabilities = {}
            
            # Discover tools - try even if capabilities is empty
            print(f"  🔧 Discovering tools...")
            tools_response = await self._send_mcp_request(server, "tools/list", {})
            if tools_response and "tools" in tools_response:
                server.tools = {tool["name"]: tool for tool in tools_response["tools"]}
                print(f"    Found {len(server.tools)} tools")
            else:
                print(f"    No tools found")
                server.tools = {}
            
            # Discover prompts
            print(f"  📝 Discovering prompts...")
            prompts_response = await self._send_mcp_request(server, "prompts/list", {})
            if prompts_response and "prompts" in prompts_response:
                server.prompts = {prompt["name"]: prompt for prompt in prompts_response["prompts"]}
                print(f"    Found {len(server.prompts)} prompts")
            else:
                print(f"    No prompts found")
                server.prompts = {}
            
            # Discover resources
            print(f"  📁 Discovering resources...")
            resources_response = await self._send_mcp_request(server, "resources/list", {})
            if resources_response and "resources" in resources_response:
                server.resources = {resource["uri"]: resource for resource in resources_response["resources"]}
                print(f"    Found {len(server.resources)} resources")
            else:
                print(f"    No resources found")
                server.resources = {}
                    
        except Exception as e:
            print(f"  ❌ Error discovering capabilities for {server.name}: {e}")
            # Set empty defaults
            server.tools = {}
            server.prompts = {}
            server.resources = {}
    
    async def _send_mcp_request(self, server: MCPServer, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send MCP request to server and get response"""
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params
        }
        
        try:
            if server.websocket:
                # WebSocket communication
                await server.websocket.send(json.dumps(request))
                response = await server.websocket.recv()
                return json.loads(response).get("result")
            
            elif server.process:
                # Process stdin/stdout communication
                request_json = json.dumps(request) + "\n"
                server.process.stdin.write(request_json.encode())
                await server.process.stdin.drain()
                
                # Read response
                response_line = await server.process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.decode().strip())
                    return response.get("result")
            
            elif server.url and "/sse" in server.url:
                # For FastMCP SSE, we need to send HTTP requests
                async with aiohttp.ClientSession() as session:
                    endpoint = server.url.replace("/sse", "/jsonrpc")
                    async with session.post(
                        endpoint, 
                        json=request,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status != 200:
                            print(f"Request failed: {response.status}")
                            return None
                        response_data = await response.json()
                        return response_data.get("result")
                
            return None
            
        except Exception as e:
            print(f"Error sending MCP request: {e}")
            return None
    
    async def stop_server(self, name: str) -> bool:
        """Stop a specific server by name"""
        if name not in self.servers:
            print(f"Server not found: {name}")
            return False
        
        server = self.servers[name]
        
        try:
            if server.websocket and not server.websocket.closed:
                await server.websocket.close()
            
            if server.process and server.process.returncode is None:
                try:
                    server.process.terminate()
                    # Give it a moment to terminate gracefully
                    await asyncio.sleep(2)
                    
                    # Force kill if still running
                    if server.process.returncode is None:
                        server.process.kill()
                except Exception as e:
                    print(f"Error stopping server process: {e}")
                    return False
            
            print(f"✅ Stopped server: {name}")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping server: {e}")
            return False
    
    async def stop_all_servers(self):
        """Stop all running MCP servers"""
        for name in self.servers:
            await self.stop_server(name)
    
    async def restart_server(self, name: str) -> bool:
        """Restart a specific server by name"""
        await self.stop_server(name)
        return await self.connect_server(name)
    
    async def get_server_health(self, name: str) -> Dict[str, Any]:
        """Get health status of a specific server"""
        if name not in self.servers:
            return {"status": "not_found"}
        
        server = self.servers[name]
        
        if not server.is_running and not server.is_connected:
            return {"status": "stopped"}
        
        try:
            # Try to ping the server
            response = await self._send_mcp_request(server, "ping", {})
            if response and response.get("pong"):
                return {
                    "status": "healthy",
                    "details": {
                        "tools": len(server.tools or {}),
                        "prompts": len(server.prompts or {}),
                        "resources": len(server.resources or {})
                    }
                }
            else:
                return {"status": "unhealthy", "reason": "no_response"}
                
        except Exception as e:
            return {"status": "unhealthy", "reason": str(e)}
    
    async def get_all_servers_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all servers"""
        results = {}
        for name in self.servers:
            results[name] = await self.get_server_health(name)
        return results
