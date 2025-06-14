# AI Conversation Bot with Dynamic MCP Integration

**Advanced voice-controlled AI assistant with dynamic tool integration and self-specializing agents**

A sophisticated conversation bot that features wake word detection, speech processing, and a revolutionary **dynamic MCP (Model Context Protocol) integration system** that automatically discovers, integrates, and specializes with any MCP server without code changes.

---

## 🌟 Key Features

### Core Functionality
- **Wake Word Detection**: Activates with predefined wake words
- **Speech-to-Text**: OpenAI Whisper for accurate transcription  
- **Text-to-Speech**: Kokoro TTS for natural speech synthesis
- **Multi-Agent AI**: Gemini-powered conversation with fallback agents

### Revolutionary MCP Integration
- **🔧 Dynamic Tool Discovery**: Automatically finds and integrates tools from any MCP server
- **🧠 Self-Specializing Agents**: Creates domain expertise automatically based on available tools
- **📡 Protocol-Aware**: Supports SSE, WebSocket, and HTTP protocols automatically
- **🎯 Intelligent Routing**: Routes requests to specialized agents based on context
- **⚡ Universal Tool Execution**: Execute any MCP tool without hard-coded handlers

### Advanced Agent System
- **Dynamic Specialization**: Agents automatically become experts in discovered tool domains
- **Domain Expertise Injection**: Enhance any agent with specialized knowledge
- **Intelligent Delegation**: Multi-agent orchestration with automatic selection
- **Learning & Optimization**: Improves performance through usage patterns

---

## 🏗️ Architecture

```
User Voice → Wake Word → STT → Primary Agent → Intent Detection
                                      ↓
                               Tool Request Detected
                                      ↓
                              MCP Agent → Tool Router → Protocol Client → MCP Server
                                      ↓         ↓            ↓              ↓
                                [Specialized] [Dynamic]  [SSE/WS/HTTP]  [Real Tools]
                                 [Agents]     [Handler]   [Auto-detect]
```

### Agent Hierarchy
- **Primary Agent** (Gemini): Conversation + intent detection
- **MCP Agent**: Dynamic tool discovery and execution
- **Specialized Agents**: Auto-created domain experts
- **Fallback Agents**: GPT-4 for complex tasks

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <repository>
cd Conversation-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Create `.env` file:
```env
GEMINI_KEY=your-gemini-api-key
PRORCUPINE_KEY=your-picovoice-access-key
OPENAI_KEY=your-openai-api-key
PHONEMIZER_ESPEAK_LIBRARY=path-to-espeak-library
PHONEMIZER_ESPEAK_PATH=path-to-espeak-executable
```

### 3. Run the Application
```bash
# Universal launcher (recommended)
python start_agent.py

# Platform-specific
./start_agent.sh        # Mac/Linux  
start_agent.bat         # Windows

# Direct execution
python main.py
```

---

## 🔧 MCP Server Configuration

Add any MCP server to `config/mcp_servers.json`:

```json
{
  "your-server": {
    "description": "Your MCP Server",
    "enabled": true,
    "command": "npx",
    "args": ["@your/mcp-server@latest"]
  }
}
```

The system will automatically:
1. 🔍 **Discover** all tools from your server
2. 🧠 **Create** specialized agents for tool domains  
3. 🎯 **Route** user requests to appropriate agents
4. ⚡ **Execute** tools with the correct protocol

---

## 🧪 Testing

```bash
# Test core MCP functionality
python tests/test_mcp_protocols.py

# Test dynamic agent specialization  
python tests/test_phase3_simple.py

# Test specific integrations
python tests/test_mcp_integration.py
```

---

## 🎯 Current Tool Support

### Azure DevOps (Working)
- **get_work_items**: List work items
- **create_work_item**: Create new work items
- **update_work_item**: Update existing work items

### Auto-Discovery Ready
- **Playwright**: Browser automation (process-based)
- **Any MCP Server**: Automatic integration

---

## 📁 Project Structure

```
conversation-bot/
├── agents/                 # Agent implementations
│   ├── dynamic_specialized_agent.py    # Self-specializing agents
│   ├── mcp_agent.py                   # MCP-aware agent
│   └── base_agent.py                  # Agent interface
├── utils/                  # Core utilities
│   ├── tool_manager.py               # Tool discovery & management
│   ├── mcp_protocol_client.py        # Universal protocol client
│   ├── domain_expertise_injector.py  # Agent enhancement
│   └── intelligent_agent_delegator.py # Smart routing
├── config/                 # Configuration
│   └── mcp_servers.json             # MCP server definitions
├── tests/                  # All test files
└── PROJECT_SUMMARY.md      # Comprehensive project overview
```

---

## 🌟 What Makes This Special

### 🔮 **Dynamic Everything**
- No hard-coded tool handlers
- Automatic protocol detection  
- Self-creating specialized agents
- Universal tool execution

### 🧠 **Intelligent Agent System**
- Agents automatically specialize based on available tools
- Domain expertise injection for any agent
- Multi-agent delegation with learning
- Context-aware tool routing

### 📡 **Protocol Agnostic**
- SSE (Server-Sent Events) support
- WebSocket MCP communication
- HTTP JSON-RPC fallback
- Automatic protocol detection

### ⚡ **Real Functionality**
- Working SSE connection to Azure DevOps
- 3 fully functional DevOps tools
- End-to-end tool execution
- Production-ready MCP integration

---

## 🤝 Contributing

This project represents a breakthrough in dynamic MCP integration. The architecture is designed to be completely extensible - adding new MCP servers, tools, or agent types requires no code changes, only configuration updates.

For detailed technical documentation, see `PROJECT_SUMMARY.md`.

---

## 📄 License

This project is open source. Please check individual component licenses in their respective directories.

---

**Transform your conversation bot into a dynamic, tool-aware AI assistant that automatically adapts to any available capabilities!** 🚀