# MCP Integration TODO

## Current Issue
- **Problem**: Tool discovery failing because we're mixing SSE and HTTP JSON-RPC protocols
- **Impact**: 0 tools registered → agents crash when asked about tools
- **Root Cause**: SSE servers need SSE/WebSocket client, but we're using HTTP requests

## Goals
1. **Dynamic MCP Support**: Work with any MCP server (SSE, HTTP, WebSocket)
2. **No Hard-coding**: Detect server capabilities dynamically
3. **Production Stability**: Don't break existing SSE servers
4. **Agent Functionality**: Fix crash when asking about tools

## Current Approach (Temporary Fix)
- Detect server type (SSE vs HTTP) automatically
- For SSE servers: Use SSE client OR graceful fallback
- For HTTP servers: Use existing JSON-RPC
- Store discovered tools in `server.tools` for agents

## Long-term Solution Needed
- Implement proper SSE/WebSocket MCP client
- Use MCP specification for tool discovery over SSE
- Remove any hardcoded fallbacks

## Agent Crash Issue
- **Location**: `ui/chatwindow.py` line 91 - `RuntimeError: no running event loop`
- **Cause**: Trying to create async task without event loop
- **Fix Needed**: Check async context or use different approach

## Files Modified
- `utils/mcp_server_manager.py` - Tool discovery logic
- Need to check: `ui/chatwindow.py` - Agent response handling