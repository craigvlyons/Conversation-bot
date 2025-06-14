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
    
    def connect_to_servers(self, timeout=5):
        """Connect to MCP servers with timeout to avoid blocking indefinitely"""
        import threading
        
        # Create a dictionary to store connection results
        results = {}
        
        def connect_to_single_server(server_id, server):
            print(f"Connecting to MCP server: {server_id}")
            results[server_id] = self._connect_to_server(server)
            print(f"Connection attempt for {server_id} completed, result: {results[server_id]}")
            
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
            
        # Check which servers were successfully connected
        for server_id, success in results.items():
            if success:
                self.connected_servers[server_id] = self.servers[server_id]
                
        # For any threads still running, give them a bit more time but don't fail completely
        still_running = [t for t in threads if t.is_alive()]
        if still_running:
            print(f"⚠️ {len(still_running)} servers still connecting, giving extra time...")
            time.sleep(2)  # Give extra time
            
            # Check results again
            for server_id, success in results.items():
                if success and server_id not in self.connected_servers:
                    self.connected_servers[server_id] = self.servers[server_id]
            
            # Log any servers that are still timing out
            for thread in threads:
                if thread.is_alive():
                    server_id = thread.name.replace("connect-", "")
                    print(f"⚠️ Connection to {server_id} still in progress, but continuing")
                
        # Try to discover capabilities for servers that connected
        if self.connected_servers:
            print(f"Moving on with {len(self.connected_servers)} connected servers")
    def _connect_to_server(self, server: MCPServer) -> bool:
        if server.url:
            print(f"🌐 Trying URL connection for {server.id}: {server.url}/sse")
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
    
    def discover_capabilities(self):
        """Discover capabilities for all connected servers."""
        for server_id, server in self.connected_servers.items():
            print(f"🔍 Discovering capabilities for {server_id}...")
            
            # Try to initialize the server
            initialized = self._init_server(server)
            if initialized:
                print(f"  ✅ Initialized {server_id}")
            else:
                print(f"  ❌ Failed to initialize {server_id}")
            
            # Discover tools
            print(f"  🔧 Discovering tools...")
            tools = self._discover_tools(server)
            if tools:
                print(f"    Found {len(tools)} tools")
            else:
                print(f"    No tools found")
            
            # Discover prompts
            print(f"  📝 Discovering prompts...")
            prompts = self._discover_prompts(server)
            if prompts:
                print(f"    Found {len(prompts)} prompts")
            else:
                print(f"    No prompts found")
            
            # Discover resources
            print(f"  📁 Discovering resources...")
            resources = self._discover_resources(server)
            if resources:
                print(f"    Found {len(resources)} resources")
            else:
                print(f"    No resources found")
            
            print(f"✅ Connected to MCP server: {server_id}")
            print(f"   Tools: {len(tools) if tools else 0}")
            print(f"   Prompts: {len(prompts) if prompts else 0}")
            print(f"   Resources: {len(resources) if resources else 0}")
    
    def _init_server(self, server: MCPServer) -> bool:
        """Initialize an MCP server."""
        if not server.url:
            print(f"No URL available for server")
            return False
        
        try:
            jsonrpc_url = f"{server.url.rstrip('/')}/jsonrpc"
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
        """Discover tools from an MCP server."""
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
            jsonrpc_url = f"{server.url.rstrip('/')}/jsonrpc"
            headers = {"Content-Type": "application/json"}
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params
            }
            
            response = requests.post(jsonrpc_url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return result["result"]
            else:
                print(f"Request failed: {response.status_code}")
        except Exception as e:
            print(f"Error sending MCP request: {str(e)}")
        
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
        """Discover capabilities of connected servers"""
        for server_id, server in self.connected_servers.items():
            if server.url:
                self._discover_server_capabilities(server)
                
    def _discover_server_capabilities(self, server: MCPServer):
        """Discover capabilities of a specific server using its API"""
        if not server.url:
            return
        
        try:
            # Make a GET request to the server's capabilities endpoint
            url = f"{server.url}/capabilities"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                capabilities = response.json()
                # Extract tools from the capabilities
                if "tools" in capabilities:
                    server.tools = capabilities["tools"]
                    print(f"✅ Discovered {len(server.tools)} tools for {server.id}")
                else:
                    print(f"⚠️ No tools found in capabilities for {server.id}")
            else:
                print(f"❌ Failed to get capabilities for {server.id}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error discovering capabilities for {server.id}: {e}")
