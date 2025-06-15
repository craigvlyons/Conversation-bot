# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a voice-controlled AI conversation bot that integrates wake word detection, speech-to-text (STT), text-to-speech (TTS), and multiple AI models (Gemini, GPT-4) to provide intelligent conversational responses. The system also includes MCP (Model Context Protocol) server integration for dynamic tool support.

## Development Commands

### Setup
```bash
# Virtual environment setup
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or 
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Universal Python launcher (recommended)
python start_agent.py

# Platform-specific scripts:
# Windows:
start_agent.bat

# Mac/Linux:
./start_agent.sh

# Direct execution:
python main.py
```

### Testing
```bash
# Run MCP tools tests
python -m pytest tests/test_mcp_tools.py

# Test MCP integration end-to-end
python test_mcp_integration.py

# Test FastMCP SSE client directly
python -c "
import asyncio
from utils.mcp_sse_client import MCPSSEClient

async def test():
    client = MCPSSEClient('http://localhost:8000/sse')
    await client.initialize_mcp()
    tools = await client.discover_tools()
    print(f'Found {len(tools)} tools')
    await client.disconnect()

asyncio.run(test())
"

# Test MCP agent with live server discovery
python -c "
import asyncio
from agents.mcp_agent import MCPAgent

async def test():
    agent = MCPAgent()
    await agent.initialize()
    response = await agent.get_response('what tools do you have?')
    print(response)

asyncio.run(test())
"

# Run all tests
python -m pytest tests/
```

## Architecture Overview

### Agent System
The application uses a multi-agent architecture managed by `AgentRegistry`:
- **Primary Agent**: GeminiAIAgent (cost-effective for basic tasks)
- **Secondary Agent**: GeminiAIAgent2 (advanced Gemini model for complex tasks)  
- **Fallback Agent**: GPT4oAgent (OpenAI GPT-4 for code-related tasks)
- **MCP Agent**: MCPAgent (handles MCP tool integration)

Agents are initialized in `setup/initialize_agents.py` and registered globally for access throughout the application.

### MCP Integration
The system supports Model Context Protocol (MCP) servers for dynamic tool integration with full FastMCP support:

#### Core MCP Components
- **Server Manager**: `utils/mcp_server_manager.py` handles server lifecycle and connection management
- **SSE Client**: `utils/mcp_sse_client.py` implements FastMCP Server-Sent Events protocol
- **Protocol Client**: `utils/mcp_protocol_client.py` auto-detects and connects to different MCP transports
- **Tool Manager**: `utils/tool_manager.py` manages tool discovery across all connected servers
- **Dynamic Tool Handler**: `utils/dynamic_tool_handler.py` executes tools using dynamic routing
- **Tool Registry**: `utils/mcp_tool_registry.py` caches discovered tools for performance

#### FastMCP SSE Protocol Support
- **Complete MCP Initialization**: Implements proper `initialize` → `notifications/initialized` → `tools/list` sequence
- **Session Management**: Extracts and uses server-provided session IDs for FastMCP communication
- **Persistent SSE Connections**: Maintains bidirectional communication with FastMCP servers
- **Async Response Handling**: Processes server responses via SSE stream with proper request/response matching

#### Azure DevOps Integration
- **Real-time Tool Discovery**: Dynamically discovers 9+ Azure DevOps tools from live FastMCP server
- **Work Item Management**: Full CRUD operations (create, read, update, search work items)
- **Project Operations**: List projects, manage work item relationships, add tasks
- **Advanced Features**: Comments, linking, state management, search capabilities

#### Configuration and Setup
- MCP servers configured in `config/mcp_servers.json`
- Supports multiple transport types: SSE, WebSocket, HTTP, STDIO
- Background initialization prevents UI blocking
- Graceful fallback when servers are unavailable

#### Tool Execution Flow
User input → Agent detects tool trigger → Protocol client connects → Tool discovery → Dynamic execution → Results returned

### Core Components
- **Main UI**: PyQt6-based chat interface (`ui/chatwindow.py`)
- **Speech Processing**: 
  - Wake word detection using Picovoice (`speech/wake_word/`)
  - STT via OpenAI Whisper (`speech/stt/stt.py`)
  - TTS via Kokoro (`speech/tts/KokoroTTS.py`)
- **Audio**: Recording and playback (`recording/AutoRecorder.py`)

## Required Environment Variables

Create a `.env` file with:
```
GEMINI_KEY=your-gemini-api-key
PRORCUPINE_KEY=your-picovoice-access-key
OPENAI_KEY=your-openai-api-key
PHONEMIZER_ESPEAK_LIBRARY=C:\Program Files\eSpeak NG\libespeak-ng.dll
PHONEMIZER_ESPEAK_PATH=C:\Program Files\eSpeak NG\espeak-ng.exe
```

Required for Azure DevOps FastMCP integration:
```
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/yourorg
AZURE_DEVOPS_PAT=your-personal-access-token
AZURE_DEVOPS_PROJECT=your-default-project-name  # Optional
AZURE_USERNAME=your-email@domain.com            # Optional
```

Optional for legacy Azure integrations:
```
AZURE_FUNCTION_URL=your-azure-function-url
AZURE_FUNCTION_APP_KEY=your-azure-function-key
```

## Key Patterns

### Agent Selection
Agents are selected based on task complexity:
- Use "primary" for general conversation
- Use "fallback" for code/technical tasks
- Use "mcp" when MCP tools are needed

### MCP Tool Development
New MCP tools should follow the base patterns in `utils/mcp_tool_base.py`. Tools are dynamically discovered and registered at runtime.

### Async Operations
MCP operations are async and run in background threads to prevent UI blocking. The main application uses QEventLoop for async/await support with PyQt6.

## Cross-Platform Compatibility

The codebase now supports both Windows and Mac/Linux through:

- **Dynamic Path Resolution**: `utils/platform_config.py` handles platform-specific paths
- **Command Detection**: Automatic `npx` vs `npx.cmd` resolution for MCP servers
- **Multiple Launchers**: Platform-specific startup scripts and universal Python launcher
- **Wake Word Models**: Platform-specific `.ppn` file detection
- **Environment Setup**: Automated virtual environment and dependency management

### Platform-Specific Notes

**Windows:**
- Requires eSpeak NG installation and environment variables
- Uses `npx.cmd` for Node.js MCP servers
- Paths use Windows-style separators automatically

**Mac/Linux:**
- Uses `espeak` (install via package manager)
- Standard `npx` for Node.js MCP servers  
- Follows XDG directory specifications on Linux

## Development Notes

### MCP Server Integration
- The application starts the UI immediately while MCP servers initialize in the background
- MCP server failures are handled gracefully without blocking core functionality
- FastMCP SSE protocol is fully implemented with proper session management and async response handling
- Dynamic tool discovery replaces static tool caching for real-time server integration
- Azure DevOps FastMCP server provides 9+ live tools for work item and project management

### Architecture & Performance
- All constants are centralized in `utils/constants.py` with platform-aware paths
- Message history is cached in the UI layer for context
- Wake word detection runs in a separate thread
- Platform detection is automatic and transparent to the application logic
- Async/await patterns used throughout for non-blocking operations

### FastMCP Protocol Implementation
- **Session Management**: Automatically extracts and uses server-provided session IDs
- **Bidirectional Communication**: Maintains persistent SSE connections for real-time communication
- **Proper Initialization**: Implements complete MCP handshake: `initialize` → `notifications/initialized` → `tools/list`
- **Error Handling**: Graceful fallback when servers are unavailable or timeout occurs
- **Dynamic Discovery**: Tools are discovered at runtime from live servers, not cached files