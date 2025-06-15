import asyncio
import json
import logging
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union, Any

import aiohttp
import requests
from aiohttp import ClientTimeout
from utils.platform_config import get_platform_config
from utils.mcp_sse_client import MCPSSEClient

logger = logging.getLogger(__name__)

@dataclass
class MCPServer:
    id: str
    url: Optional[str] = None
    command: Optional[str] = None
    process: Optional[subprocess.Popen] = None
    enabled: bool = True
    environment: Dict[str, str] = field(default_factory=dict)
    directory: Optional[str] = None
    server_args: List[str] = field(default_factory=list)
    tools: Dict[str, Dict[str, Any]] = field(default_factory=dict)

class MCPServerManager:
    def __init__(self, config_path: str = "./config/mcp_servers.json"):
        self.config_path = config_path
        self.servers: Dict[str, MCPServer] = {}
        self.connected_servers: Dict[str, MCPServer] = {}
        self._load_config()
    
    def _load_config(self):
        try:
            with open(self.config_path, "r") as f:
                servers_config = json.load(f)
                
            self.servers = {}
            for server_id, config in servers_config.items():
                enabled = config.get("enabled", True)
                if not enabled:
                    print(f"⏭️ Skipping disabled server: {server_id}")
                    continue
                url = config.get("url")
                command = config.get("command")
                # Handle both env and environment keys
                environment = config.get("environment", config.get("env", {}))
                directory = config.get("directory")                # Handle both args and server_args keys
                server_args = config.get("server_args", config.get("args", []))
                
                self.servers[server_id] = MCPServer(
                    id=server_id,
                    url=url,
                    command=command,
                    enabled=enabled,
                    environment=environment,
                    directory=directory,
                    server_args=server_args
                )
                
            print(f"✅ Loaded {len(self.servers)} MCP servers from config")
        except FileNotFoundError:
            print(f"❌ MCP servers config not found: {self.config_path}")
    
    def connect_to_servers(self, timeout=20):
        """Connect to MCP servers with timeout to avoid blocking indefinitely"""
        import threading
        
        # Create a dictionary to store connection results
        results = {}
        
        def connect_to_single_server(server_id, server):
            print(f"Connecting to MCP server: {server_id}")
            try:
                result = self._connect_to_server(server)
                results[server_id] = result
                print(f"Connection attempt for {server_id} completed, result: {result}")
                
                # If successful, immediately add to connected_servers
                if result:
                    self.connected_servers[server_id] = server
                    print(f"✅ {server_id} added to connected servers")
                
            except Exception as e:
                print(f"❌ Error connecting to {server_id}: {e}")
                results[server_id] = False
            
        # Connect to each server in a separate thread to prevent blocking
        threads = []
        for server_id, server in self.servers.items():
            thread = threading.Thread(
                target=connect_to_single_server, 
                args=(server_id, server),
                name=f"connect-{server_id}"
            )
            thread.daemon = True  # Mark as daemon so it doesn't block program exit
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete or timeout
        start_time = time.time()
        while time.time() - start_time < timeout and any(t.is_alive() for t in threads):
            time.sleep(0.1)
            
        # Give any remaining threads a bit more time
        still_running = [t for t in threads if t.is_alive()]
        if still_running:
            print(f"⚠️ {len(still_running)} servers still connecting, giving extra time...")
            extra_wait = 10  # Give extra time for slow connections like Playwright
            extra_start = time.time()
            
            while time.time() - extra_start < extra_wait and any(t.is_alive() for t in threads):
                time.sleep(0.2)
            
            # Final check for any servers that finished during extra time
            for thread in threads:
                if thread.is_alive():
                    server_id = thread.name.replace("connect-", "")
                    print(f"⚠️ Connection to {server_id} still in progress after {timeout + extra_wait}s")
                else:
                    # Thread finished, check if it was successful
                    server_id = thread.name.replace("connect-", "")
                    if server_id in results and results[server_id]:
                        print(f"✅ {server_id} connected during extra time")
                
        # Report final connection status
        connected_count = len(self.connected_servers)
        print(f"📊 Final connection summary: {connected_count}/{len(self.servers)} servers connected")
        
        if self.connected_servers:
            for server_id in self.connected_servers:
                print(f"  ✅ {server_id}")
            print(f"Moving on with {connected_count} connected servers")
        else:
            print("❌ No servers successfully connected")
    def _connect_to_server(self, server: MCPServer) -> bool:
        if server.url:
            print(f"🌐 Trying URL connection for {server.id}: {server.url}")
            if self._test_url_connection(server):
                print(f"✅ Connected to {server.id} via URL")
                return True
            print(f"❌ URL connection failed for {server.id}")
        
        if server.command:
            print(f"🚀 Starting {server.id} via command: {server.command}")
            if self._start_server_process(server):
                # Give the server a moment to start
                time.sleep(2)
                
                # For Playwright and similar MCP servers, if process is running, consider it connected
                if server.process and server.process.poll() is None:
                    # Try to extract URL from process output
                    url = self._extract_url_from_process(server)
                    if url:
                        server.url = url
                        print(f"✅ Found server URL: {url}")
                        
                        # Test URL connection but don't fail if it doesn't respond
                        if self._test_url_connection(server):
                            print(f"✅ Verified connection to {server.id} via URL")
                        else:
                            print(f"⚠️ URL not responding yet, but process is running")
                    else:
                        # No URL found, but process is running - assume it's working
                        server.url = f"http://localhost:3000"  # Default for MCP servers
                        print(f"⚠️ No URL found in output, using default: {server.url}")
                    
                    print(f"✅ Started {server.id} via command (process running)")
                    return True
                else:
                    print(f"❌ Process failed to start or exited early for {server.id}")
                    return False
            print(f"❌ Command startup failed for {server.id}")
        
        print(f"❌ Failed to connect to MCP server: {server.id}")
        return False
        
    def _extract_url_from_process(self, server: MCPServer, timeout=2) -> Optional[str]:
        """Extract URL from server process output with timeout."""
        if not server.process:
            return None
        
        # Common URL patterns for MCP servers
        patterns = [
            r'Server running at (https?://[^\s]+)',
            r'MCP server listening on (https?://[^\s]+)',
            r'listening on (https?://[^\s]+)',
            r'Server started at (https?://[^\s]+)',
            r'Listening on: (https?://[^\s]+)',
            r'Running at (https?://[^\s]+)',
            # Additional patterns for Playwright MCP
            r'Started server on (https?://[^\s]+)',
            r'Server available at (https?://[^\s]+)',
            r'MCP Server listening on (https?://[^\s]+)',
            r'.*server.*on.*(https?://[^\s]+)',
            r'.*listening.*(https?://localhost:\d+)',
            r'.*running.*(https?://127\.0\.0\.1:\d+)'
        ]
        
        # Check if we can read stdout from the process
        if hasattr(server.process, 'stdout') and server.process.stdout:
            import io
            
            # Try to read with timeout
            try:
                start_time = time.time()
                
                # For Playwright MCP, use a more patient approach
                if server.id == "playwright":
                    print(f"  Waiting for Playwright MCP to start...")
                    # Give Playwright more time to start and capture output
                    max_wait = 10
                    start_wait = time.time()
                    
                    while time.time() - start_wait < max_wait:
                        # Check if process is still running
                        if server.process.poll() is not None:
                            print(f"  Playwright process exited early")
                            break
                        
                        # Try to read output
                        try:
                            # Use a non-blocking approach to read available output
                            import select
                            if hasattr(select, 'select'):
                                ready, _, _ = select.select([server.process.stdout], [], [], 0.5)
                                if ready:
                                    line = server.process.stdout.readline()
                                    if line:
                                        decoded_line = line.decode('utf-8', errors='ignore').strip()
                                        if decoded_line:
                                            print(f"  Playwright output: {decoded_line}")
                                            # Look for URL in output
                                            url_match = re.search(r'https?://[^\s]+', decoded_line)
                                            if url_match:
                                                found_url = url_match.group(0)
                                                print(f"  Found URL in Playwright output: {found_url}")
                                                return found_url
                        except:
                            # If select doesn't work (Windows), fall back to polling
                            pass
                        
                        # Try common ports every few seconds
                        if (time.time() - start_wait) % 2 < 0.5:
                            possible_urls = [
                                "http://localhost:3000",
                                "http://localhost:8080", 
                                "http://127.0.0.1:3000",
                                "http://127.0.0.1:8080"
                            ]
                            
                            for url in possible_urls:
                                if self._test_url_basic(url):
                                    print(f"  Found working Playwright URL: {url}")
                                    return url
                        
                        time.sleep(0.5)
                    
                    # If we still haven't found a URL, return default but warn
                    print(f"  No responsive URL found for Playwright, using default")
                    return "http://localhost:3000"
                
                # Read for up to timeout seconds for other servers
                output_lines = []
                while time.time() - start_time < timeout:
                    # Windows-compatible approach - just try to read a line without select
                    try:
                        # Non-blocking readline is tricky on Windows
                        # Just read with timeout and wait between attempts
                        line = server.process.stdout.readline()
                        if not line:
                            time.sleep(0.1)
                            continue
                            
                        decoded_line = line.decode('utf-8', errors='ignore').strip()
                        if decoded_line:
                            print(f"  Server output: {decoded_line}")
                            output_lines.append(decoded_line)
                            
                            # Check for URL in this line
                            for pattern in patterns:
                                match = re.search(pattern, decoded_line, re.IGNORECASE)
                                if match:
                                    found_url = match.group(1) if match.groups() else match.group(0)
                                    # Clean up the URL
                                    found_url = re.search(r'https?://[^\s]+', found_url)
                                    if found_url:
                                        return found_url.group(0)
                    except Exception as e:
                        print(f"  Error reading line: {e}")
                        time.sleep(0.1)
                
                # If no URL found in patterns, try to extract any URL from all output
                if output_lines:
                    all_output = ' '.join(output_lines)
                    url_match = re.search(r'https?://[^\s]+', all_output)
                    if url_match:
                        print(f"  Found URL in output: {url_match.group(0)}")
                        return url_match.group(0)
                
                # If we got here, we timed out without finding URL
                print(f"  No URL found in process output after {timeout} seconds")
                
                # For Playwright MCP, we'll use a default URL if none is found
                if server.id == "playwright":
                    default_url = "http://localhost:3000"
                    print(f"  Using default URL for Playwright MCP: {default_url}")
                    return default_url
                
                return None
                
            except Exception as e:
                # Handle the case where stdout might not support non-blocking read
                print(f"  Error reading process output: {e}")
                
                # For Playwright MCP, we'll use a default URL if there's an error
                if server.id == "playwright":
                    default_url = "http://localhost:3000"
                    print(f"  Using default URL for Playwright MCP: {default_url}")
                    return default_url
                
                return None
        
        return None
    
    def _start_server_process(self, server: MCPServer) -> bool:
        if not server.command:
            return False
            
        cmd_parts = server.command.split()
        
        # Use platform-aware command resolution
        platform_config = get_platform_config()
        if cmd_parts:
            cmd_parts[0] = platform_config.get_command_executable(cmd_parts[0])
            
        # Prepare environment variables
        env = os.environ.copy()
        for key, value in server.environment.items():
            env[key] = value
    
        # Add any server args
        if server.server_args:
            cmd_parts.extend(server.server_args)
            
        try:
            print(f"Starting MCP server: {' '.join(cmd_parts)}")
            
            # Use server directory if specified
            cwd = os.path.abspath(server.directory) if server.directory else None
            if cwd:
                print(f"  Using directory: {cwd}")
                
            # Start the process with stdout and stderr pipes
            process = subprocess.Popen(
                cmd_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=cwd,
                text=False,  # We'll handle decoding manually
                bufsize=1,   # Line buffered
                shell=False  # Don't use shell to avoid process management issues
            )
            
            # Check if process started successfully
            if process.poll() is not None:
                # Process has already terminated
                stderr = process.stderr.read().decode('utf-8', errors='ignore') if process.stderr else ""
                print(f"Server process failed to start: {stderr}")
                return False
            
            print(f"  ✅ Process started (PID: {process.pid})")
            server.process = process
            return True
        except Exception as e:
            print(f"  ❌ Error starting server process: {str(e)}")
            return False
    
    def _test_url_connection(self, server: MCPServer) -> bool:
        if not server.url:
            return False
        
        try:
            # Check if URL already ends with /sse, if not add it
            if server.url.endswith('/sse'):
                sse_url = server.url
            else:
                sse_url = f"{server.url.rstrip('/')}/sse"
            response = requests.get(sse_url, stream=True, timeout=3)
            return response.status_code == 200
        except Exception:
            return False
    
    def _test_url_basic(self, url: str) -> bool:
        """Test basic URL connectivity without requiring specific endpoints"""
        try:
            # Try base URL first
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
            
            # Try common MCP endpoints
            endpoints = ['/sse', '/health', '/status', '/']
            for endpoint in endpoints:
                try:
                    test_url = f"{url.rstrip('/')}{endpoint}"
                    response = requests.get(test_url, timeout=1)
                    if response.status_code == 200:
                        return True
                except:
                    continue
            
            return False
        except Exception:
            return False
    
    def verify_server_connections(self):
        """Verify that all connected servers are still responsive."""
        print("🔍 Verifying server connections...")
        
        for server_id, server in self.connected_servers.items():
            print(f"  📡 Checking {server_id}...")
            
            try:
                # For process-based servers, check if process is still running
                if server.process:
                    if server.process.poll() is None:
                        print(f"    ✅ Process running (PID: {server.process.pid})")
                    else:
                        print(f"    ❌ Process has terminated")
                        continue
                
                # For URL-based servers, test connectivity
                if server.url:
                    if self._test_url_connection(server):
                        print(f"    ✅ URL responsive ({server.url})")
                    else:
                        print(f"    ⚠️ URL not responding ({server.url})")
                
            except Exception as e:
                print(f"    ❌ Error checking {server_id}: {e}")
        
        print("✅ Server connection verification complete")
    
    def _init_server(self, server: MCPServer) -> bool:
        """
        Initialize an MCP server.
        NOTE: This method is used by the ToolManager for tool discovery.
        """
        if not server.url:
            print(f"No URL available for server")
            return False
        
        try:
            # For URLs ending with /sse, use the base URL for JSON-RPC
            if server.url.endswith('/sse'):
                base_url = server.url[:-4]  # Remove '/sse'
            else:
                base_url = server.url.rstrip('/')
            
            jsonrpc_url = f"{base_url}/jsonrpc"
            headers = {"Content-Type": "application/json"}
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "capabilities": {
                        "experimental": {}
                    }
                }
            }
            
            response = requests.post(jsonrpc_url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                return True
            else:
                print(f"Request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error sending MCP request: {str(e)}")
            return False
    
    def _discover_tools(self, server: MCPServer) -> List[Dict]:
        """
        Discover tools from an MCP server.
        NOTE: This method is used by the ToolManager for dynamic tool discovery.
        """
        return self._send_jsonrpc_request(server, "getTools", {})
    
    def _discover_prompts(self, server: MCPServer) -> List[Dict]:
        """Discover prompts from an MCP server."""
        return self._send_jsonrpc_request(server, "getPrompts", {})
    
    def _discover_resources(self, server: MCPServer) -> List[Dict]:
        """Discover resources from an MCP server."""
        return self._send_jsonrpc_request(server, "getResources", {})
    
    def _send_jsonrpc_request(self, server: MCPServer, method: str, params: Dict) -> List[Dict]:
        """Send a JSON-RPC request to an MCP server."""
        if not server.url:
            return []
        
        try:
            # For URLs ending with /sse, use the base URL for JSON-RPC
            if server.url.endswith('/sse'):
                base_url = server.url[:-4]  # Remove '/sse'
            else:
                base_url = server.url.rstrip('/')
            
            jsonrpc_url = f"{base_url}/jsonrpc"
            headers = {"Content-Type": "application/json"}
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params
            }
            
            print(f"  📡 Sending JSON-RPC request to: {jsonrpc_url}")
            print(f"  📤 Method: {method}")
            response = requests.post(jsonrpc_url, json=payload, headers=headers, timeout=5)
            print(f"  📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  📋 Response: {result}")
                if "result" in result:
                    tools_result = result["result"]
                    print(f"  🔧 Tools in result: {len(tools_result) if isinstance(tools_result, list) else 'not a list'}")
                    return tools_result
                else:
                    print(f"  ⚠️ No 'result' field in response")
                    return []
            else:
                print(f"  ❌ Request failed: {response.status_code}")
                try:
                    error_text = response.text
                    print(f"  📄 Error response: {error_text}")
                except:
                    pass
        except Exception as e:
            print(f"  ❌ Error sending MCP request: {str(e)}")
        
        return []
    
    def shutdown(self):
        """Shutdown all MCP server processes."""
        for server_id, server in self.connected_servers.items():
            if server.process:
                try:
                    print(f"Shutting down MCP server: {server_id}")
                    server.process.terminate()
                    server.process.wait(timeout=5)
                    print(f"  ✅ Server {server_id} terminated")
                except Exception as e:
                    print(f"  ❌ Error shutting down server {server_id}: {str(e)}")
                    try:
                        server.process.kill()
                    except:
                        pass
    
    async def stop_all_servers(self):
        """Asynchronously shutdown all MCP server processes."""
        for server_id, server in self.connected_servers.items():
            if server.process:
                try:
                    print(f"Shutting down MCP server: {server_id}")
                    server.process.terminate()
                    
                    # Give it a moment to terminate gracefully
                    for _ in range(50):  # 5 seconds timeout
                        if server.process.poll() is not None:
                            break
                        await asyncio.sleep(0.1)
                    
                    if server.process.poll() is None:
                        print(f"  ⚠️ Server {server_id} not responding, forcing kill")
                        server.process.kill()
                        await asyncio.sleep(0.5)
                    
                    print(f"  ✅ Server {server_id} terminated")
                except Exception as e:
                    print(f"  ❌ Error shutting down server {server_id}: {str(e)}")
                    try:
                        server.process.kill()
                    except:
                        pass
    
    def get_tools(self) -> List[Dict]:
        """Get all tools from all connected MCP servers."""
        all_tools = []
        for server_id, server in self.connected_servers.items():
            tools = self._discover_tools(server)
            if tools:
                # Add server_id to each tool for identification
                for tool in tools:
                    tool["server_id"] = server_id
                all_tools.extend(tools)
        
        return all_tools
    
    def discover_capabilities(self):
        """Discover capabilities of connected servers - dynamic approach for any MCP server"""
        for server_id, server in self.connected_servers.items():
            print(f"🔍 Discovering capabilities for {server_id}...")
            
            # Dynamic server type detection
            server_type = self._detect_server_type(server)
            print(f"  📡 Detected server type: {server_type}")
            
            if server_type == "sse":
                print(f"  💡 SSE-based MCP server detected")
                success = self._discover_tools_via_sse(server)
                if not success:
                    print(f"  ⚠️ SSE tool discovery failed")
                    server.tools = {}
                
            elif server_type == "http":
                print(f"  🌐 HTTP-based MCP server detected")
                success = self._discover_tools_via_http(server)
                if not success:
                    print(f"  ⚠️ HTTP tool discovery failed, server may use different protocol")
                    server.tools = {}
                    
            elif server_type == "stdio":
                print(f"  💬 Stdio-based MCP server detected")
                success = self._discover_tools_via_stdio(server)
                if not success:
                    print(f"  ⚠️ Stdio tool discovery failed")
                    server.tools = {}
                    
            elif server_type == "websocket":
                print(f"  🔌 WebSocket-based MCP server detected")
                print(f"  ⚠️ WebSocket tool discovery not yet implemented")
                server.tools = {}
                
            else:
                print(f"  ❓ Unknown server type, attempting multiple protocols...")
                # Try different approaches dynamically
                success = self._try_multiple_discovery_methods(server)
                if not success:
                    print(f"  ⚠️ All discovery methods failed")
                    server.tools = {}
            
            tools_count = len(server.tools) if server.tools else 0
            print(f"✅ Server {server_id} ready - {tools_count} tools available")
            
    def _detect_server_type(self, server: MCPServer) -> str:
        """Dynamically detect MCP server transport type"""
        # Check URL patterns first (explicit URLs take precedence)
        if server.url:
            if '/sse' in server.url and not server.process:
                return "sse"
            elif 'ws://' in server.url or 'wss://' in server.url:
                return "websocket"
            elif 'http://' in server.url or 'https://' in server.url:
                # Check if this is a real HTTP URL or a fallback for stdio server
                if server.process and ('localhost:3000' in server.url or '127.0.0.1:3000' in server.url):
                    # This is likely a stdio server with fallback URL - test if HTTP actually works
                    if not self._test_url_basic(server.url):
                        return "stdio"
                return "http"
        elif server.process:
            # Process-based server without specific URL - likely stdio
            return "stdio"
        else:
            return "unknown"
            
    def _discover_tools_via_http(self, server: MCPServer) -> bool:
        """Attempt tool discovery via HTTP JSON-RPC"""
        try:
            # Try to initialize the server
            initialized = self._init_server(server)
            if not initialized:
                print(f"    ❌ HTTP initialization failed")
                return False
                
            print(f"    ✅ HTTP initialization successful")
            
            # Discover tools
            tools = self._discover_tools(server)
            if tools:
                server.tools = {}
                for tool in tools:
                    tool_name = tool.get('name')
                    if tool_name:
                        server.tools[tool_name] = tool
                print(f"    ✅ Discovered {len(tools)} tools via HTTP: {list(server.tools.keys())}")
                return True
            else:
                print(f"    ⚠️ No tools returned from HTTP discovery")
                return False
                
        except Exception as e:
            print(f"    ❌ HTTP discovery error: {e}")
            return False

    def _discover_tools_via_sse(self, server: MCPServer) -> bool:
        """Discover tools from SSE-based MCP server"""
        try:
            print(f"    🔍 Attempting SSE tool discovery...")
            
            # Create SSE client
            sse_client = MCPSSEClient(server.url)
            
            # Run async discovery in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Connect and initialize
                print(f"    📡 Connecting to SSE server...")
                loop.run_until_complete(sse_client.connect())
                
                print(f"    🔧 Initializing MCP session...")
                loop.run_until_complete(sse_client.initialize_mcp())
                
                print(f"    🔍 Discovering tools...")
                tools = loop.run_until_complete(sse_client.discover_tools())
                
                if tools:
                    server.tools = {}
                    for tool in tools:
                        tool_name = tool.get('name')
                        if tool_name:
                            server.tools[tool_name] = tool
                    print(f"    ✅ Discovered {len(tools)} tools via SSE: {list(server.tools.keys())}")
                    return True
                else:
                    print(f"    ⚠️ No tools returned from SSE discovery")
                    return False
                    
            finally:
                # Clean up SSE client
                if hasattr(sse_client, 'close'):
                    loop.run_until_complete(sse_client.close())
                loop.close()
                
        except Exception as e:
            print(f"    ❌ SSE discovery error: {e}")
            return False

    def _discover_tools_via_stdio(self, server: MCPServer) -> bool:
        """Discover tools from stdio-based MCP server"""
        try:
            print(f"    🔍 Attempting stdio tool discovery...")
            
            if not server.process or not hasattr(server.process, "stdin") or not hasattr(server.process, "stdout"):
                print(f"    ❌ No valid stdio process available")
                return False
            
            # Check if process is still running
            if server.process.poll() is not None:
                print(f"    ❌ Process is not running")
                return False
            
            # First, send initialize request
            print(f"    🔧 Initializing MCP session...")
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "mcp-server-manager",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send init request
            init_json = json.dumps(init_request) + "\n"
            server.process.stdin.write(init_json.encode())
            server.process.stdin.flush()
            
            # Read init response
            init_response_line = server.process.stdout.readline()
            if init_response_line:
                init_response = json.loads(init_response_line.decode().strip())
                if "error" in init_response:
                    print(f"    ❌ Initialize failed: {init_response['error']}")
                    return False
                print(f"    ✅ MCP session initialized")
            
            # Now send tools/list request
            print(f"    🔍 Requesting tools list...")
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            tools_json = json.dumps(tools_request) + "\n"
            server.process.stdin.write(tools_json.encode())
            server.process.stdin.flush()
            
            # Read tools response
            tools_response_line = server.process.stdout.readline()
            if tools_response_line:
                tools_response = json.loads(tools_response_line.decode().strip())
                if "error" in tools_response:
                    print(f"    ❌ Tools list failed: {tools_response['error']}")
                    return False
                
                # Extract tools from response
                result = tools_response.get("result", {})
                tools = result.get("tools", [])
                
                if tools:
                    server.tools = {}
                    for tool in tools:
                        tool_name = tool.get('name')
                        if tool_name:
                            server.tools[tool_name] = tool
                    print(f"    ✅ Discovered {len(tools)} tools via stdio: {list(server.tools.keys())}")
                    return True
                else:
                    print(f"    ⚠️ No tools returned from stdio discovery")
                    return False
            else:
                print(f"    ❌ No response from stdio tools request")
                return False
                
        except Exception as e:
            print(f"    ❌ Stdio discovery error: {e}")
            return False
            
    def _try_multiple_discovery_methods(self, server: MCPServer) -> bool:
        """Try multiple discovery protocols for unknown servers"""
        print(f"    🔄 Trying HTTP JSON-RPC...")
        if self._discover_tools_via_http(server):
            return True
            
        print(f"    🔄 HTTP failed, server may require SSE/WebSocket client")
        print(f"    💡 This server is connected but tool discovery needs implementation")
        return False
                
