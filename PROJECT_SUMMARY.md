# Conversation Bot - Project Summary

## Overview
A voice-controlled AI conversation bot with dynamic MCP (Model Context Protocol) integration, featuring automatic agent specialization and protocol-aware tool discovery.

## Architecture Evolution

### Phase 1: Tool Router Agent Pattern ✅
**Goal**: Separate tool management from conversation logic
- Created `ToolManager` for centralized tool discovery
- Built `DynamicToolHandler` for universal tool execution  
- Added intent detection to route tool requests to MCP agent
- Extracted tool logic from UI into service layer

### Phase 2: Protocol Implementation ✅
**Goal**: Fix core SSE/WebSocket client issues for real tool functionality
- Implemented `MCPSSEClient` for Azure DevOps server communication
- Built `MCPWebSocketClient` for full MCP protocol support
- Created `MCPProtocolClient` for automatic protocol detection
- Updated `ToolManager` to use protocol-specific clients
- **Result**: 3/3 Azure DevOps tools fully functional with SSE protocol

### Phase 3: Dynamic Specialized Agents ✅
**Goal**: Create intelligent, self-specializing agent ecosystem
- Built `DynamicSpecializedAgent` that adapts to any tool domain automatically
- Implemented `DomainExpertiseInjector` for enhancing existing agents
- Created `IntelligentAgentDelegator` with automatic specialization detection
- Added learning and optimization across agent interactions
- **Result**: Fully dynamic agent ecosystem that specializes based on available tools

## Current System Status

### ✅ Working Components
- **MCP Servers**: Azure DevOps (SSE), Playwright (Process-based)
- **Tool Discovery**: 3 Azure DevOps tools discovered and executable
- **Protocol Support**: SSE, WebSocket, HTTP JSON-RPC auto-detection
- **Agent Specialization**: Dynamic domain expertise creation
- **Tool Execution**: End-to-end tool execution with real results

### 🔧 Available Tools
1. **get_work_items**: Get list of work items from Azure DevOps
2. **create_work_item**: Create a new work item in Azure DevOps  
3. **update_work_item**: Update an existing work item

### 🏗️ Core Architecture

```
User Input → Primary Agent → Intent Detection → MCP Agent → Tool Router → Protocol Client → MCP Server
                 ↓              ↓                ↓           ↓              ↓                ↓
            [Conversation]  [Tool Detection]  [Dynamic]   [Universal]   [SSE/WS/HTTP]   [Azure DevOps]
                                                [Routing]   [Handler]     [Auto-detect]    [Tools]
```

### 🧠 Agent System

```
Base Agent
    ↓
├── Primary Agent (Gemini) - Conversation + Intent Detection
├── MCP Agent - Tool Discovery + Execution  
└── Dynamic Specialized Agent - Auto-specialization
    ↓
    Domain Expertise Injector - Enhances any agent
    ↓
    Intelligent Agent Delegator - Routes to best agent
```

## Key Files

### Core Agents
- `agents/base_agent.py` - Base agent interface with MCP support
- `agents/dynamic_specialized_agent.py` - Self-specializing agent
- `agents/mcp_agent.py` - MCP-aware agent with dynamic routing
- `agents/gemini_agent.py` - Primary conversational agent

### MCP Infrastructure  
- `utils/tool_manager.py` - Centralized tool discovery and management
- `utils/mcp_protocol_client.py` - Universal protocol client (SSE/WebSocket/HTTP)
- `utils/mcp_sse_client.py` - SSE client for Azure DevOps
- `utils/mcp_websocket_client.py` - WebSocket client for MCP servers
- `utils/dynamic_tool_handler.py` - Universal tool execution

### Agent Intelligence
- `utils/domain_expertise_injector.py` - Inject domain knowledge into agents
- `utils/intelligent_agent_delegator.py` - Smart agent routing and delegation
- `services/tool_service.py` - Clean UI-agent separation

### Configuration
- `config/mcp_servers.json` - MCP server definitions
- `utils/constants.py` - System constants
- `CLAUDE.md` - Development instructions and architecture notes

## Testing
All tests moved to `tests/` folder:
- `test_phase3_simple.py` - Core Phase 3 functionality
- `test_mcp_protocols.py` - Protocol-aware MCP system
- `test_mcp_integration.py` - End-to-end integration tests

## Environment Requirements
```
GEMINI_KEY=your-gemini-api-key
PRORCUPINE_KEY=your-picovoice-access-key
OPENAI_KEY=your-openai-api-key
PHONEMIZER_ESPEAK_LIBRARY=path-to-espeak-library
PHONEMIZER_ESPEAK_PATH=path-to-espeak
```

## Key Achievements

### 🎯 Dynamic Everything
- **No hard-coded tool handlers** - Works with any MCP server/tool
- **Automatic protocol detection** - SSE, WebSocket, HTTP support
- **Self-specializing agents** - Create expertise from available tools
- **Universal tool execution** - Any tool from any server

### 🧠 Intelligence Features  
- **Intent detection** - Routes tool requests automatically
- **Domain expertise injection** - Enhance any agent with specialized knowledge
- **Learning system** - Improves with usage and interaction patterns
- **Multi-agent delegation** - Intelligent agent selection and routing

### 🔧 Real Functionality
- **Working SSE connection** to Azure DevOps server
- **3 fully functional tools** with real execution results
- **Protocol-aware communication** with proper MCP compliance
- **End-to-end tool workflows** from user input to tool execution

## Future Expansion
The architecture is designed to be completely extensible:
- Add any MCP server to `mcp_servers.json` → Automatic tool discovery
- New tools → Automatic agent specialization  
- New protocols → Add protocol client to system
- New agent types → Automatic expertise injection

The system transforms from a static tool-calling bot into a dynamic, self-optimizing, protocol-aware MCP agent ecosystem that adapts to any available tools without code changes.