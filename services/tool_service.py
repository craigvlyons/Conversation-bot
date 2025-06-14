"""
Tool Service Layer - Provides clean interface for tool information and management.
Separates tool logic from UI concerns and provides unified access to both regular and MCP tools.
"""

from typing import Dict, List, Any, Optional
from agents.registry import AgentRegistry
import logging

logger = logging.getLogger(__name__)

class ToolService:
    """
    Service layer for tool management and information.
    Provides a clean interface for UI and other components to access tool functionality.
    """
    
    def __init__(self):
        self.agent_registry = AgentRegistry
    
    def get_tools_summary(self) -> str:
        """
        Get a comprehensive summary of all available tools across all agents.
        Returns a formatted string suitable for display.
        """
        try:
            info = ["🔧 Available Tools:"]
            total_tools = 0
            
            # Get primary agent
            primary_agent = self.agent_registry.get("primary")
            if primary_agent:
                regular_tools = self._get_regular_tools_info(primary_agent)
                if regular_tools:
                    info.extend(regular_tools)
                    total_tools += len([line for line in regular_tools if line.startswith("  -")])
            
            # Get MCP agent and tools
            mcp_agent = self.agent_registry.get("mcp")
            if mcp_agent:
                mcp_tools = self._get_mcp_tools_info(mcp_agent)
                if mcp_tools:
                    info.extend(mcp_tools)
                    total_tools += len([line for line in mcp_tools if line.startswith("  -")])
            
            if total_tools == 0:
                return "❌ No tools currently available.\n\nMCP servers may still be initializing..."
            
            # Add summary header
            info[0] = f"🔧 Available Tools ({total_tools} total):"
            
            return "\n".join(info)
            
        except Exception as e:
            logger.error(f"Error getting tools summary: {e}")
            return f"❌ Error retrieving tool information: {str(e)}"
    
    def _get_regular_tools_info(self, agent) -> List[str]:
        """Get information about regular (non-MCP) tools."""
        info = []
        
        try:
            if hasattr(agent, 'tools') and agent.tools:
                info.append(f"\n📦 Regular Tools ({len(agent.tools)}):")
                for tool in agent.tools[:5]:  # Show first 5
                    if hasattr(tool, 'name'):
                        tool_name = tool.name() if callable(tool.name) else tool.name
                        info.append(f"  • {tool_name}")
                
                if len(agent.tools) > 5:
                    info.append(f"  ... and {len(agent.tools) - 5} more")
                    
        except Exception as e:
            logger.warning(f"Error getting regular tools info: {e}")
            
        return info
    
    def _get_mcp_tools_info(self, mcp_agent) -> List[str]:
        """Get information about MCP tools."""
        info = []
        
        try:
            if hasattr(mcp_agent, 'get_all_mcp_tools'):
                mcp_tools = mcp_agent.get_all_mcp_tools()
                if mcp_tools:
                    info.append(f"\n🌐 MCP Tools ({len(mcp_tools)}):")
                    
                    # Group tools by server
                    tools_by_server = {}
                    for tool_name, tool_info in mcp_tools.items():
                        server_id = tool_info.get('server_id', 'unknown')
                        if server_id not in tools_by_server:
                            tools_by_server[server_id] = []
                        tools_by_server[server_id].append((tool_name, tool_info))
                    
                    # Display tools grouped by server
                    for server_id, server_tools in tools_by_server.items():
                        info.append(f"  📡 {server_id.upper()} Server:")
                        for tool_name, tool_info in server_tools[:3]:  # Show first 3 per server
                            description = tool_info.get('description', 'No description')
                            # Truncate long descriptions
                            if len(description) > 50:
                                description = description[:47] + "..."
                            info.append(f"    • {tool_name}: {description}")
                        
                        if len(server_tools) > 3:
                            info.append(f"    ... and {len(server_tools) - 3} more")
                else:
                    info.append("\n🌐 MCP Tools: 0 available")
                    info.append("  ⏳ Servers may still be initializing...")
                    
        except Exception as e:
            logger.warning(f"Error getting MCP tools info: {e}")
            info.append("\n🌐 MCP Tools: Error retrieving information")
            
        return info
    
    def get_mcp_server_status(self) -> str:
        """Get the status of MCP servers."""
        try:
            mcp_agent = self.agent_registry.get("mcp")
            if not mcp_agent:
                return "❌ MCP Agent not available"
            
            if hasattr(mcp_agent, 'tool_manager'):
                stats = mcp_agent.tool_manager.get_discovery_stats()
                
                status_lines = [
                    "📊 MCP Server Status:",
                    f"  🔧 Total Tools: {stats.get('total_tools', 0)}",
                    f"  🌐 Active Servers: {stats.get('servers_with_tools', 0)}/{stats.get('total_servers', 0)}",
                    f"  ✅ Discovery Complete: {'Yes' if stats.get('discovery_complete') else 'No'}"
                ]
                
                # Add per-server breakdown
                tools_by_server = stats.get('tools_by_server', {})
                if tools_by_server:
                    status_lines.append("  📋 Tools by Server:")
                    for server_id, tool_count in tools_by_server.items():
                        status_lines.append(f"    • {server_id}: {tool_count} tools")
                
                return "\n".join(status_lines)
            else:
                return "⚠️ MCP Agent not fully initialized"
                
        except Exception as e:
            logger.error(f"Error getting MCP server status: {e}")
            return f"❌ Error retrieving server status: {str(e)}"
    
    def is_tool_request(self, user_input: str) -> bool:
        """
        Determine if user input is asking for tool information.
        """
        user_lower = user_input.lower()
        tool_query_patterns = [
            'tool', 'tools', 'available', 'what can you do',
            'capabilities', 'functions', 'commands', 'help'
        ]
        
        return any(pattern in user_lower for pattern in tool_query_patterns)
    
    async def initialize_mcp_agent(self) -> bool:
        """
        Initialize the MCP agent if it hasn't been initialized yet.
        Returns True if successful, False otherwise.
        """
        try:
            mcp_agent = self.agent_registry.get("mcp")
            if mcp_agent and hasattr(mcp_agent, 'initialize'):
                if not mcp_agent.initialized:
                    await mcp_agent.initialize()
                return mcp_agent.initialized
            return False
        except Exception as e:
            logger.error(f"Error initializing MCP agent: {e}")
            return False
    
    def get_tool_execution_history(self) -> str:
        """Get recent tool execution history."""
        try:
            mcp_agent = self.agent_registry.get("mcp")
            if mcp_agent and hasattr(mcp_agent, 'tool_handler'):
                history = mcp_agent.tool_handler.get_execution_history()
                
                if not history:
                    return "📝 No tool executions yet."
                
                info = [f"📝 Recent Tool Executions ({len(history)}):\n"]
                
                # Show last 5 executions
                recent_executions = history[-5:]
                for execution in recent_executions:
                    status = "✅" if execution.success else "❌"
                    time_str = f"{execution.execution_time:.2f}s" if execution.execution_time else "N/A"
                    info.append(f"  {status} {execution.tool_name} ({time_str})")
                    
                    if not execution.success and execution.error:
                        # Truncate long error messages
                        error = execution.error
                        if len(error) > 100:
                            error = error[:97] + "..."
                        info.append(f"     Error: {error}")
                
                if len(history) > 5:
                    info.append(f"  ... and {len(history) - 5} more")
                
                return "\n".join(info)
            else:
                return "📝 Tool execution history not available."
                
        except Exception as e:
            logger.error(f"Error getting tool execution history: {e}")
            return f"❌ Error retrieving execution history: {str(e)}"