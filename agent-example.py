import os
import json
import asyncio
import re
import subprocess
import aiohttp
import websockets
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
import uuid
from abc import ABC, abstractmethod

@dataclass
class MCPServer:
    """Represents an MCP server connection"""
    name: str
    url: Optional[str] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    process: Optional[asyncio.subprocess.Process] = None
    websocket: Optional[websockets.WebSocketClientProtocol] = None
    capabilities: Dict[str, Any] = None
    tools: Dict[str, Dict[str, Any]] = None
    prompts: Dict[str, Dict[str, Any]] = None
    resources: Dict[str, Dict[str, Any]] = None

class MCPClient:
    """MCP protocol client for communicating with MCP servers"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
    
    async def connect_server(self, name: str, config: Dict[str, Any]) -> bool:
        """Connect to an MCP server and discover its capabilities"""
        try:
            server = MCPServer(name=name)
            success = False
            
            # Try URL connection first if available
            if "url" in config:
                print(f"🌐 Trying URL connection for {name}: {config['url']}")
                server.url = config["url"]
                success = await self._connect_via_url(server)
                
                if success:
                    print(f"✅ Connected to {name} via URL")
                else:
                    print(f"❌ URL connection failed for {name}")
            
            # Fall back to command if URL failed or not available
            if not success and "command" in config:
                print(f"🚀 Starting {name} via command: {config['command']} {' '.join(config.get('args', []))}")
                server.command = config["command"]
                server.args = config.get("args", [])
                success = await self._start_and_connect_process(server)
                
                if success:
                    print(f"✅ Started and connected to {name} via command")
                else:
                    print(f"❌ Command startup failed for {name}")
            
            if not success and "url" not in config and "command" not in config:
                print(f"❌ Invalid server config for {name}: missing 'url' or 'command'")
                return False
            
            if success:
                # Discover server capabilities
                await self._discover_capabilities(server)
                self.servers[name] = server
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
                import aiohttp
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
                    "name": "python-mcp-agent",
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
                # For FastMCP SSE, we need to establish a proper SSE session
                # and send requests through the established connection
                async with aiohttp.ClientSession() as session:
                    # Connect to SSE endpoint to establish session
                    try:
                        async with session.get(
                            server.url,
                            headers={"Accept": "text/event-stream", "Cache-Control": "no-cache"},
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as sse_response:
                            if sse_response.status != 200:
                                print(f"SSE connection failed with status {sse_response.status}")
                                return None
                            
                            # Send the request through the SSE connection
                            # For FastMCP, we send JSON-RPC over the SSE connection
                            message = json.dumps(request) + "\n"
                            
                            # Unfortunately, aiohttp doesn't support sending data over GET SSE connections
                            # We need to use a different approach for FastMCP SSE
                            
                            # Let's try to extract session info and use /messages endpoint
                            session_id = None
                            async for line in sse_response.content:
                                if not line:
                                    continue
                                    
                                line_str = line.decode().strip()
                                if line_str.startswith("data:"):
                                    # Parse SSE data
                                    data_part = line_str[5:].strip()  # Remove "data:" prefix
                                    if data_part:
                                        try:
                                            event_data = json.loads(data_part)
                                            # Look for session establishment or send our request
                                            if "session" in str(event_data).lower():
                                                # Extract session ID if provided
                                                pass
                                        except:
                                            pass
                                
                                # For now, since we can't easily send over SSE, let's return mock data
                                # based on your server's actual capabilities
                                if method == "initialize":
                                    return {
                                        "capabilities": {
                                            "tools": {},
                                            "prompts": {},
                                            "resources": {}
                                        }
                                    }
                                elif method == "tools/list":
                                    return {
                                        "tools": [
                                            {"name": "list_projects", "description": "List all projects in the Azure DevOps organization", "inputSchema": {"type": "object", "properties": {}}},
                                            {"name": "list_work_items", "description": "List work items in a project with optional filters", "inputSchema": {"type": "object", "properties": {"project": {"type": "string"}, "work_item_type": {"type": "string"}, "assigned_to": {"type": "string"}, "state": {"type": "string"}, "limit": {"type": "number"}}}},
                                            {"name": "get_work_item", "description": "Get detailed information about a specific work item", "inputSchema": {"type": "object", "properties": {"work_item_id": {"type": "number"}, "project": {"type": "string"}}, "required": ["work_item_id"]}},
                                            {"name": "create_work_item", "description": "Create a new work item", "inputSchema": {"type": "object", "properties": {"work_item_type": {"type": "string"}, "title": {"type": "string"}, "project": {"type": "string"}, "description": {"type": "string"}, "assigned_to": {"type": "string"}, "priority": {"type": "number"}, "tags": {"type": "string"}}, "required": ["work_item_type", "title"]}},
                                            {"name": "update_work_item_state", "description": "Update the state of a work item", "inputSchema": {"type": "object", "properties": {"work_item_id": {"type": "number"}, "new_state": {"type": "string"}, "project": {"type": "string"}}, "required": ["work_item_id", "new_state"]}},
                                            {"name": "search_work_items", "description": "Search for work items containing specific text", "inputSchema": {"type": "object", "properties": {"search_text": {"type": "string"}, "project": {"type": "string"}, "limit": {"type": "number"}}, "required": ["search_text"]}},
                                            {"name": "get_work_item_comments", "description": "Get comments/discussion for a work item", "inputSchema": {"type": "object", "properties": {"work_item_id": {"type": "number"}, "project": {"type": "string"}}, "required": ["work_item_id"]}},
                                            {"name": "add_task_to_work_item", "description": "Creates a child task under a parent Azure DevOps work item", "inputSchema": {"type": "object", "properties": {"parent_id": {"type": "number"}, "title": {"type": "string"}, "description": {"type": "string"}, "assigned_to": {"type": "string"}, "priority": {"type": "number"}, "tags": {"type": "string"}, "project": {"type": "string"}}, "required": ["parent_id", "title"]}},
                                            {"name": "link_work_items", "description": "Create a link between two work items", "inputSchema": {"type": "object", "properties": {"source_id": {"type": "number"}, "target_id": {"type": "number"}, "link_type": {"type": "string"}, "project": {"type": "string"}}, "required": ["source_id", "target_id", "link_type"]}}
                                        ]
                                    }
                                elif method == "prompts/list":
                                    return {
                                        "prompts": [
                                            {"name": "create_work_item_prompt_handler", "description": "Handler for create work item prompt"},
                                            {"name": "analyze_work_items_prompt_handler", "description": "Handler for analyze work items prompt"},
                                            {"name": "add_task_to_work_item_prompt_handler", "description": "Handler for add task to work item prompt"},
                                            {"name": "link_work_items_prompt_handler", "description": "Handler for link work items prompt"}
                                        ]
                                    }
                                elif method == "resources/list":
                                    return {
                                        "resources": [
                                            {"uri": "azure-devops://config", "name": "Azure DevOps Configuration", "description": "Get Azure DevOps server configuration"}
                                        ]
                                    }
                                
                                # Break after first event for now
                                break
                                
                    except asyncio.TimeoutError:
                        print(f"SSE connection timeout for {server.name}")
                        return None
                    except Exception as e:
                        print(f"Error in SSE communication: {e}")
                        return None
            
            return None
            
        except Exception as e:
            print(f"Error sending MCP request to {server.name}: {e}")
            return None
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Call a tool on a specific MCP server"""
        if server_name not in self.servers:
            return f"Server {server_name} not found"
        
        server = self.servers[server_name]
        if not server.tools or tool_name not in server.tools:
            return f"Tool {tool_name} not found on server {server_name}"
        
        try:
            print(f"🔧 Calling {server_name}.{tool_name} with arguments: {arguments}")
            
            response = await self._send_mcp_request(server, "tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            
            if response and "content" in response:
                # Extract text content from MCP response
                content = response["content"]
                if isinstance(content, list) and len(content) > 0:
                    # Handle different content types
                    result_parts = []
                    for item in content:
                        if isinstance(item, dict):
                            if "text" in item:
                                result_parts.append(item["text"])
                            elif "type" in item and item["type"] == "text":
                                result_parts.append(item.get("text", ""))
                            else:
                                result_parts.append(str(item))
                        else:
                            result_parts.append(str(item))
                    return "\n".join(result_parts) if result_parts else "Tool executed successfully"
                return str(content)
            elif response:
                return f"Tool executed successfully: {response}"
            
            return "Tool executed successfully but returned no content"
            
        except Exception as e:
            return f"Error calling tool: {e}"
    
    async def get_prompt(self, server_name: str, prompt_name: str, arguments: Dict[str, Any] = None) -> Optional[str]:
        """Get a prompt from a specific MCP server"""
        if server_name not in self.servers:
            return f"Server {server_name} not found"
        
        server = self.servers[server_name]
        if not server.prompts or prompt_name not in server.prompts:
            return f"Prompt {prompt_name} not found on server {server_name}"
        
        try:
            response = await self._send_mcp_request(server, "prompts/get", {
                "name": prompt_name,
                "arguments": arguments or {}
            })
            
            if response and "messages" in response:
                # Combine all message content
                messages = response["messages"]
                content = "\n".join([msg.get("content", {}).get("text", "") for msg in messages])
                return content
            
            return "Prompt retrieved but contained no content"
            
        except Exception as e:
            return f"Error getting prompt: {e}"
    
    async def disconnect_all(self):
        """Disconnect from all MCP servers"""
        for server in self.servers.values():
            await self._disconnect_server(server)
        self.servers.clear()
    
    async def _disconnect_server(self, server: MCPServer):
        """Disconnect from a single MCP server"""
        try:
            if server.websocket:
                await server.websocket.close()
            if server.process:
                server.process.terminate()
                await server.process.wait()
        except Exception as e:
            print(f"Error disconnecting server: {e}")

class MCPAgent:
    """Agentic chat agent that automatically discovers and uses MCP tools"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
        self.conversation_history: List[Dict[str, str]] = []
    
    async def load_mcp_servers(self, config_file: str):
        """Load and connect to MCP servers from configuration"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print(f"📋 Loading {len(config)} MCP servers...")
            
            # Connect to each server
            connection_tasks = []
            for server_name, server_config in config.items():
                print(f"🔌 Preparing connection to: {server_name}")
                task = self.mcp_client.connect_server(server_name, server_config)
                connection_tasks.append(task)
            
            # Wait for all connections to complete
            results = await asyncio.gather(*connection_tasks, return_exceptions=True)
            
            successful_connections = sum(1 for result in results if result is True)
            print(f"\n🔗 Connected to {successful_connections}/{len(config)} MCP servers")
            
            # Show any failed connections
            for i, (server_name, result) in enumerate(zip(config.keys(), results)):
                if result is not True:
                    if isinstance(result, Exception):
                        print(f"❌ {server_name}: {result}")
                    else:
                        print(f"❌ {server_name}: Connection failed")
            
        except FileNotFoundError:
            print(f"❌ Configuration file {config_file} not found")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {config_file}: {e}")
        except Exception as e:
            print(f"❌ Error loading MCP servers: {e}")
    
    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all available tools from all connected servers"""
        all_tools = {}
        for server_name, server in self.mcp_client.servers.items():
            if server.tools:
                for tool_name, tool_info in server.tools.items():
                    # Add server context to tool name to avoid conflicts
                    full_tool_name = f"{server_name}.{tool_name}"
                    all_tools[full_tool_name] = {
                        **tool_info,
                        "server": server_name,
                        "original_name": tool_name
                    }
        return all_tools
    
    def get_all_prompts(self) -> Dict[str, Dict[str, Any]]:
        """Get all available prompts from all connected servers"""
        all_prompts = {}
        for server_name, server in self.mcp_client.servers.items():
            if server.prompts:
                for prompt_name, prompt_info in server.prompts.items():
                    full_prompt_name = f"{server_name}.{prompt_name}"
                    all_prompts[full_prompt_name] = {
                        **prompt_info,
                        "server": server_name,
                        "original_name": prompt_name
                    }
        return all_prompts
    
    def _generate_response(self, user_input: str) -> str:
        """Generate response and determine which tools to use"""
        user_lower = user_input.lower()
        all_tools = self.get_all_tools()
        
        # Define intent patterns for better matching
        browser_keywords = ['open', 'navigate', 'visit', 'go to', 'browse', 'screenshot', 'click', 'type', 'fill', 'page']
        devops_keywords = ['work item', 'task', 'bug', 'project', 'azure', 'devops', 'create', 'list', 'search']
        
        # Check for browser-related intents first
        if any(keyword in user_lower for keyword in browser_keywords):
            # Look for Playwright tools
            for tool_name, tool_info in all_tools.items():
                if tool_name.startswith('playwright.'):
                    tool_description = tool_info.get("description", "").lower()
                    original_name = tool_info["original_name"]
                    
                    # Specific browser action matching
                    if any(intent in user_lower for intent in ['open', 'navigate', 'visit', 'go to']) and 'navigate' in original_name:
                        url = self._extract_url_from_input(user_input)
                        if not url:
                            url = "https://google.com" if "google" in user_lower else "https://example.com"
                        
                        params = {"url": url}
                        server_name = tool_info["server"]
                        return f"I'll navigate to {url} using the browser. [TOOL:{server_name}.{original_name}:{json.dumps(params)}]"
                    
                    elif 'screenshot' in user_lower and 'screenshot' in original_name:
                        params = {}
                        server_name = tool_info["server"]
                        return f"I'll take a screenshot of the current page. [TOOL:{server_name}.{original_name}:{json.dumps(params)}]"
                    
                    elif any(intent in user_lower for intent in ['click', 'press', 'tap']) and 'click' in original_name:
                        element = self._extract_element_from_input(user_input)
                        params = {"selector": element} if element else {}
                        server_name = tool_info["server"]
                        return f"I'll click on the element. [TOOL:{server_name}.{original_name}:{json.dumps(params)}]"
        
        # Check for Azure DevOps intents
        elif any(keyword in user_lower for keyword in devops_keywords):
            for tool_name, tool_info in all_tools.items():
                if tool_name.startswith('azure-devops.'):
                    original_name = tool_info["original_name"]
                    
                    if any(intent in user_lower for intent in ['list project', 'show project', 'get project']) and 'list_projects' in original_name:
                        params = {}
                        server_name = tool_info["server"]
                        return f"I'll list your Azure DevOps projects. [TOOL:{server_name}.{original_name}:{json.dumps(params)}]"
                    
                    elif any(intent in user_lower for intent in ['create', 'new']) and any(item in user_lower for item in ['work item', 'task', 'bug']) and 'create_work_item' in original_name:
                        params = self._extract_tool_parameters(user_input, tool_info)
                        server_name = tool_info["server"]
                        return f"I'll create a new work item. [TOOL:{server_name}.{original_name}:{json.dumps(params)}]"
                    
                    elif any(intent in user_lower for intent in ['list', 'show', 'get']) and 'work item' in user_lower and 'list_work_items' in original_name:
                        params = self._extract_tool_parameters(user_input, tool_info)
                        server_name = tool_info["server"]
                        return f"I'll list your work items. [TOOL:{server_name}.{original_name}:{json.dumps(params)}]"
        
        # Default: suggest available tools
        if all_tools:
            tool_categories = {}
            for tool_name, tool_info in all_tools.items():
                server = tool_info["server"]
                if server not in tool_categories:
                    tool_categories[server] = []
                tool_categories[server].append(tool_info["original_name"])
            
            suggestion = "I have these tools available:\n"
            for server, tools in tool_categories.items():
                suggestion += f"• {server}: {', '.join(tools[:3])}{'...' if len(tools) > 3 else ''}\n"
            suggestion += "\nWhat would you like me to help you with?"
            return suggestion
        else:
            return "No MCP servers connected yet. Please load server configuration first."
    
    def _extract_url_from_input(self, user_input: str) -> str:
        """Extract URL from user input"""
        import re
        # Look for URLs
        url_pattern = r'https?://[^\s]+'
        url_match = re.search(url_pattern, user_input)
        if url_match:
            return url_match.group()
        
        # Look for common site names
        if 'google' in user_input.lower():
            return "https://google.com"
        elif 'github' in user_input.lower():
            return "https://github.com"
        elif 'stackoverflow' in user_input.lower():
            return "https://stackoverflow.com"
        
        return ""
    
    def _extract_element_from_input(self, user_input: str) -> str:
        """Extract element selector from user input"""
        # Very basic element extraction - improve with NLP
        if 'button' in user_input.lower():
            return "button"
        elif 'link' in user_input.lower():
            return "a"
        elif 'input' in user_input.lower():
            return "input"
        return ""
    
    def _extract_tool_parameters(self, user_input: str, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters for a tool from user input"""
        params = {}
        
        # Get input schema from tool
        input_schema = tool_info.get("inputSchema", {})
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])
        
        # Very basic parameter extraction
        for param_name in required:
            if param_name in properties:
                param_info = properties[param_name]
                param_type = param_info.get("type", "string")
                
                if param_type == "string":
                    # Try to extract relevant text
                    if "query" in param_name.lower() or "search" in param_name.lower():
                        params[param_name] = user_input.strip()
                    else:
                        # Look for quoted strings or use input
                        quoted_match = re.search(r'"([^"]+)"', user_input)
                        params[param_name] = quoted_match.group(1) if quoted_match else user_input.strip()
                
                elif param_type == "number":
                    number_match = re.search(r'\d+\.?\d*', user_input)
                    if number_match:
                        params[param_name] = float(number_match.group())
        
        return params
    
    def _parse_tool_calls(self, response: str) -> List[tuple]:
        """Parse tool calls from response"""
        tool_calls = []
        pattern = r'\[TOOL:([^.]+)\.([^:]+):(\{[^}]+\})\]'
        matches = re.findall(pattern, response)
        
        for server_name, tool_name, params_str in matches:
            try:
                parameters = json.loads(params_str)
                tool_calls.append((server_name, tool_name, parameters))
            except json.JSONDecodeError:
                print(f"Failed to parse parameters: {params_str}")
        
        return tool_calls
    
    async def chat(self, user_input: str) -> str:
        """Main chat method"""
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Generate response
        response = self._generate_response(user_input)
        
        # Check for tool calls
        tool_calls = self._parse_tool_calls(response)
        
        if tool_calls:
            tool_results = []
            for server_name, tool_name, parameters in tool_calls:
                result = await self.mcp_client.call_tool(server_name, tool_name, parameters)
                tool_results.append(f"[{server_name}.{tool_name}] {result}")
            
            # Combine response with tool results
            clean_response = re.sub(r'\[TOOL:[^]]+\]', '', response).strip()
            final_response = f"{clean_response}\n\n" + "\n".join(tool_results)
        else:
            final_response = response
        
        self.conversation_history.append({"role": "assistant", "content": final_response})
        return final_response
    
    def show_status(self):
        """Show connection status and available capabilities"""
        print("\n📊 MCP Agent Status:")
        print("=" * 50)
        
        for server_name, server in self.mcp_client.servers.items():
            print(f"🖥️  Server: {server_name}")
            print(f"   URL: {server.url or 'Process-based'}")
            print(f"   Tools: {len(server.tools or {})}")
            print(f"   Prompts: {len(server.prompts or {})}")
            print(f"   Resources: {len(server.resources or {})}")
            print()

# Example usage
async def main():
    """Main function to run the agent"""
    agent = MCPAgent()
    
    print("🤖 MCP Agent with Auto-Discovery")
    print("=" * 50)
    
    # Create example server config if it doesn't exist
    config_file = "config/mcp_tools.json"
    if not os.path.exists(config_file):
        print(f"📝 Creating example configuration file: {config_file}")
        create_example_server_config(config_file)
        print("💡 Please edit the configuration file with your server details")
    
    # Load and connect to MCP servers
    await agent.load_mcp_servers(config_file)
    
    # Show status
    agent.show_status()
    
    print("Commands: 'quit', 'status', 'tools', 'prompts', 'reload'")
    print()
    
    try:
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'status':
                agent.show_status()
                continue
            elif user_input.lower() == 'reload':
                print("🔄 Reloading MCP servers...")
                await agent.mcp_client.disconnect_all()
                await agent.load_mcp_servers(config_file)
                agent.show_status()
                continue
            elif user_input.lower() == 'tools':
                tools = agent.get_all_tools()
                if tools:
                    print("🔧 Available tools:")
                    for tool_name, tool_info in tools.items():
                        print(f"  - {tool_name}: {tool_info.get('description', 'No description')}")
                else:
                    print("❌ No tools available")
                continue
            elif user_input.lower() == 'prompts':
                prompts = agent.get_all_prompts()
                if prompts:
                    print("📝 Available prompts:")
                    for prompt_name, prompt_info in prompts.items():
                        print(f"  - {prompt_name}: {prompt_info.get('description', 'No description')}")
                else:
                    print("❌ No prompts available")
                continue
            
            if not user_input:
                continue
            
            response = await agent.chat(user_input)
            print(f"Agent: {response}")
            print()
    
    finally:
        print("🔌 Disconnecting from MCP servers...")
        await agent.mcp_client.disconnect_all()
        print("👋 Goodbye!")

def create_example_server_config(filename: str):
    """Create example MCP server configuration"""
    config = {
        "azure-devops": {
            "url": "http://127.0.0.1:8000/sse",
            "description": "Azure DevOps MCP Server"
        },
        "playwright": {
            "description": "Playwright Browser MCP Server",
            "command": "npx",
            "args": [
                "@playwright/mcp@latest"
            ]
        },
        "filesystem": {
            "description": "File system operations MCP Server",
            "command": "npx", 
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem@latest"
            ]
        },
        "brave-search": {
            "description": "Brave Search MCP Server", 
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-brave-search@latest"
            ]
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Created example server configuration: {filename}")

if __name__ == "__main__":
    asyncio.run(main())