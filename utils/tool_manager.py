import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from utils.mcp_server_manager import MCPServerManager, MCPServer
from utils.mcp_protocol_client import MCPProtocolClient

logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """Represents a tool discovered from an MCP server."""
    name: str
    description: str
    server_id: str
    schema: Dict[str, Any]
    metadata: Dict[str, Any]

class ToolManager:
    """
    Centralized tool discovery and management for all MCP servers.
    Uses protocol-specific clients for optimal communication with each server type.
    """
    
    def __init__(self, mcp_server_manager: MCPServerManager):
        self.mcp_server_manager = mcp_server_manager
        self.discovered_tools: Dict[str, MCPTool] = {}
        self.tools_by_server: Dict[str, List[MCPTool]] = {}
        self.protocol_clients: Dict[str, MCPProtocolClient] = {}
        self._discovery_complete = False
        
    async def discover_all_tools(self) -> Dict[str, MCPTool]:
        """
        Discover tools from all connected MCP servers.
        Returns a dictionary mapping tool names to MCPTool objects.
        """
        logger.info("Starting comprehensive tool discovery across all MCP servers...")
        
        self.discovered_tools.clear()
        self.tools_by_server.clear()
        
        # Wait for servers to be connected
        if not self.mcp_server_manager.connected_servers:
            logger.warning("No connected MCP servers found")
            return self.discovered_tools
        
        # Discover tools from each connected server
        for server_id, server in self.mcp_server_manager.connected_servers.items():
            logger.info(f"Discovering tools from server: {server_id}")
            
            try:
                server_tools = await self._discover_tools_from_server(server)
                
                if server_tools:
                    self.tools_by_server[server_id] = server_tools
                    
                    # Add to global tool registry
                    for tool in server_tools:
                        if tool.name in self.discovered_tools:
                            logger.warning(f"Tool name collision: {tool.name} from {server_id} conflicts with existing tool")
                            # Prefix with server ID to avoid conflicts
                            prefixed_name = f"{server_id}_{tool.name}"
                            tool.name = prefixed_name
                        
                        self.discovered_tools[tool.name] = tool
                    
                    logger.info(f"Discovered {len(server_tools)} tools from {server_id}: {[t.name for t in server_tools]}")
                else:
                    logger.info(f"No tools found for server: {server_id}")
                    self.tools_by_server[server_id] = []
                    
            except Exception as e:
                logger.error(f"Error discovering tools from {server_id}: {e}")
                self.tools_by_server[server_id] = []
        
        self._discovery_complete = True
        total_tools = len(self.discovered_tools)
        logger.info(f"Tool discovery complete: {total_tools} tools from {len(self.tools_by_server)} servers")
        
        return self.discovered_tools
    
    async def _discover_tools_from_server(self, server: MCPServer) -> List[MCPTool]:
        """
        Discover tools from a specific MCP server using the appropriate protocol client.
        """
        tools = []
        
        try:
            # Create or get protocol client for this server
            if server.id not in self.protocol_clients:
                self.protocol_clients[server.id] = MCPProtocolClient(server)
            
            client = self.protocol_clients[server.id]
            
            # Connect and discover tools using protocol-specific client
            logger.info(f"🔧 Discovering tools from {server.id} using protocol client...")
            
            if not client.initialized:
                connected = await client.auto_detect_and_connect()
                if not connected:
                    logger.error(f"❌ Failed to connect to {server.id}")
                    return []
            
            # Discover tools using the appropriate protocol
            raw_tools = await client.discover_tools()
            
            if raw_tools:
                for raw_tool in raw_tools:
                    try:
                        tool = self._parse_tool_from_raw(raw_tool, server.id)
                        if tool:
                            tools.append(tool)
                    except Exception as e:
                        logger.warning(f"Failed to parse tool from {server.id}: {e}")
                        
                logger.info(f"✅ Successfully discovered {len(tools)} tools from {server.id}")
            else:
                logger.warning(f"⚠️ No tools found for {server.id}")
                        
        except Exception as e:
            logger.error(f"❌ Failed to discover tools from {server.id}: {e}")
        
        return tools
    
    def _parse_tool_from_raw(self, raw_tool: Dict[str, Any], server_id: str) -> Optional[MCPTool]:
        """
        Parse a raw tool response into an MCPTool object.
        Handles different MCP server response formats dynamically.
        """
        try:
            # Extract tool name (required)
            name = raw_tool.get('name')
            if not name:
                logger.warning(f"Tool missing name field: {raw_tool}")
                return None
            
            # Extract description (optional)
            description = raw_tool.get('description', 'No description available')
            
            # Extract schema (optional, but important for execution)
            schema = raw_tool.get('inputSchema', raw_tool.get('schema', {}))
            
            # Store all metadata for future use
            metadata = {
                'raw_tool': raw_tool,
                'server_id': server_id,
                'tool_type': raw_tool.get('type', 'unknown'),
                'version': raw_tool.get('version', '1.0')
            }
            
            return MCPTool(
                name=name,
                description=description,
                server_id=server_id,
                schema=schema,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing tool from {server_id}: {e}")
            return None
    
    def get_tool_by_name(self, tool_name: str) -> Optional[MCPTool]:
        """Get a specific tool by name."""
        return self.discovered_tools.get(tool_name)
    
    def get_tools_by_server(self, server_id: str) -> List[MCPTool]:
        """Get all tools from a specific server."""
        return self.tools_by_server.get(server_id, [])
    
    def get_all_tools(self) -> Dict[str, MCPTool]:
        """Get all discovered tools."""
        return self.discovered_tools
    
    def find_tools_by_keywords(self, keywords: List[str]) -> List[MCPTool]:
        """
        Find tools that match any of the provided keywords.
        Searches both tool names and descriptions.
        """
        matching_tools = []
        keywords_lower = [k.lower() for k in keywords]
        
        for tool in self.discovered_tools.values():
            tool_text = f"{tool.name} {tool.description}".lower()
            
            if any(keyword in tool_text for keyword in keywords_lower):
                matching_tools.append(tool)
        
        return matching_tools
    
    def get_tool_info_summary(self) -> str:
        """
        Get a formatted summary of all available tools for display or prompts.
        """
        if not self.discovered_tools:
            return "No tools available."
        
        summary_lines = []
        summary_lines.append(f"Available Tools ({len(self.discovered_tools)} total):")
        
        # Group by server for better organization
        for server_id, server_tools in self.tools_by_server.items():
            if server_tools:
                summary_lines.append(f"\n{server_id.upper()} Server:")
                for tool in server_tools:
                    summary_lines.append(f"  • {tool.name}: {tool.description}")
        
        return "\n".join(summary_lines)
    
    def is_discovery_complete(self) -> bool:
        """Check if tool discovery has been completed."""
        return self._discovery_complete
    
    def get_protocol_client(self, server_id: str) -> Optional[MCPProtocolClient]:
        """Get the protocol client for a specific server."""
        return self.protocol_clients.get(server_id)
    
    async def cleanup_clients(self):
        """Clean up all protocol clients."""
        for client in self.protocol_clients.values():
            try:
                await client.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting client: {e}")
        self.protocol_clients.clear()
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get statistics about the tool discovery process."""
        return {
            'total_tools': len(self.discovered_tools),
            'servers_with_tools': len([s for s in self.tools_by_server.values() if s]),
            'total_servers': len(self.tools_by_server),
            'discovery_complete': self._discovery_complete,
            'protocol_clients': len(self.protocol_clients),
            'tools_by_server': {
                server_id: len(tools) 
                for server_id, tools in self.tools_by_server.items()
            },
            'client_protocols': {
                server_id: client.protocol_type.value 
                for server_id, client in self.protocol_clients.items()
            }
        }