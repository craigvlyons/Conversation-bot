"""
ConvoBot MCP Tool System

This package utilizes the Model Context Protocol (MCP) for dynamic tool discovery and registration.
Tools are no longer statically defined but are dynamically loaded from MCP servers
via the MCPToolRegistry and MCPToolFactory system.

Key components:
- MCPToolRegistry: Central registry of available tools
- MCPToolFactory: Creates tool instances from metadata
- MCPCategoryHandlers: Specialized handlers for different tool categories

See the tasks/mcp_dynamic_tool_plan.md for the complete implementation approach.
"""

# No static TOOLS_LIST is needed as tools are discovered dynamically
