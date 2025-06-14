# When I Come Back - MCP Agent Architecture Refactor

## What to Say to Get Started

**"I want to implement the Tool Router Agent Pattern we discussed. We need to refactor the current monolithic agent architecture into specialized agents with proper MCP tool routing. Start with Phase 1 - create ToolManager class and specialized ToolHandler classes for different domains (DevOps, Browser, Search) while keeping the primary agent for conversation. The goal is to separate tool management from conversation and follow MCP best practices for agent specialization."**

---

## Key Context Files to Reference

- `AGENT_ARCHITECTURE_ANALYSIS.md` - Full analysis and recommendations
- `MCP_TODO.md` - Current status and issues  
- `utils/mcp_server_manager.py` - Current tool discovery logic
- `agents/base_agent.py` - Agent inheritance structure
- `ui/chatwindow.py` - Current UI-agent coupling that needs separation

---

## Current Status Summary

### ✅ Working:
- SSE server detection working
- No crashes when asking about tools  
- Dynamic server type detection
- MCP connections established (Azure DevOps SSE + Playwright)
- Thread-safe UI updates via Qt signals

### ❌ Issues:
- 0 tools discovered (SSE client not implemented)
- Monolithic agent handling everything
- UI directly coupled to agent tool logic
- Mixed protocol handling (SSE + HTTP + fallback)

---

## Architecture Problem

**Current (Problematic):**
```
User → Primary Agent → Everything (Conversation + Tools + Discovery)
         ↓
    [Handles Chat AND DevOps AND Browser AND Tool Discovery]
```

**Target (Tool Router Pattern):**
```
User → Router Agent → Specialized Agents → MCP Tools
         ↓              ↓                   ↓
    [Intent Analysis] [DevOps Agent]    [Azure DevOps]
    [Tool Detection]  [Browser Agent]   [Playwright]
    [Response Routing][Search Agent]    [Search APIs]
```

---

## Phase 1 Implementation Plan (Start Here)

### 1. Create ToolManager Class
- Centralized tool discovery for all MCP servers
- Protocol-specific clients (SSE, HTTP, WebSocket)
- Clean separation from conversation logic

### 2. Create Domain-Specific ToolHandlers
- `DevOpsToolHandler` - Azure DevOps work items, tasks
- `BrowserToolHandler` - Playwright navigation, screenshots
- `SearchToolHandler` - Search APIs and web queries

### 3. Add Routing Logic to Primary Agent
- Intent detection (is this a tool request?)
- Domain classification (DevOps vs Browser vs Search)
- Handler delegation with fallback to conversation

### 4. Extract Tool Logic from UI
- Remove tool info methods from `ui/chatwindow.py`
- Create proper service layer for tool information
- Maintain clean UI-agent separation

---

## Files That Need Changes

### Priority 1 (Create New):
- `utils/tool_manager.py` - Centralized tool discovery
- `utils/tool_handlers/devops_handler.py` - DevOps-specific logic
- `utils/tool_handlers/browser_handler.py` - Browser-specific logic
- `utils/tool_handlers/base_handler.py` - Handler interface

### Priority 2 (Modify Existing):
- `agents/gemini_agent.py` - Add routing logic
- `ui/chatwindow.py` - Remove tool-specific code
- `utils/mcp_server_manager.py` - Simplify to focus on connections

### Priority 3 (Future Phases):
- Create specialized agent classes
- Implement proper MCP protocol clients
- Add server-of-servers orchestration

---

## Key Benefits Expected

1. **Clear Separation of Concerns** - Each component has single responsibility
2. **MCP Specification Compliance** - Follows industry best practices
3. **Scalability** - Easy to add new tool domains and MCP servers
4. **Maintainability** - Modular design with clear interfaces
5. **Proper Protocol Handling** - SSE, HTTP, WebSocket clients separated

---

## Success Criteria for Phase 1

- ✅ User can ask "what DevOps tools are available?" → routed to DevOps handler
- ✅ User can ask "take a screenshot" → routed to Browser handler  
- ✅ User can have normal conversation → handled by conversation logic
- ✅ Tool discovery separated from agent conversation logic
- ✅ UI no longer directly handles tool information requests

---

## Current MCP Status

**Azure DevOps Server:**
- ✅ Connected via SSE (http://127.0.0.1:8000/sse)
- ❌ Tools not discovered (need SSE client)
- ✅ Server running and responding

**Playwright Server:**
- ✅ Process started successfully  
- ❌ Tool discovery failing (protocol mismatch)
- ⚠️ Takes 20+ seconds to fully initialize

**Overall:**
- 2/2 servers connected
- 0/2 servers providing tools
- System stable, no crashes

---

This refactor will transform the current monolithic approach into a clean, scalable, MCP-compliant architecture!