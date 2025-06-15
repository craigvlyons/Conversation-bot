Starting Conversation Bot...
Activating virtual environment...
Warning: No AI API keys found in environment variables.
Please set GEMINI_KEY and/or OPENAI_KEY in your .env file or environment.
Warning: PRORCUPINE_KEY not found. Wake word detection may not work.
Launching Conversation Bot...
==================================================
pygame 2.6.1 (SDL 2.28.4, Python 3.12.1)
Hello from the pygame community. https://www.pygame.org/contribute.html
2025-06-14 18:29:23,282 - setup.initialize_agents - INFO - MCP setup started in background thread
Starting Conversation Bot...
2025-06-14 18:29:23,283 - setup.initialize_agents - INFO - Initializing MCP Server Manager
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
2025-06-14 18:29:23,284 - setup.initialize_agents - INFO - Connecting to MCP servers
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 12932)
✅ Connected to azure-devops via URL
Connection attempt for azure-devops completed, result: True
✅ azure-devops added to connected servers
C:\convo_bot\.venv\Lib\site-packages\torch\nn\utils\weight_norm.py:143: FutureWarning: `torch.nn.utils.weight_norm` is deprecated in favor of `torch.nn.utils.parametrizations.weight_norm`.
  WeightNorm.apply(module, name, dim)
C:\convo_bot\.venv\Lib\site-packages\torch\nn\modules\rnn.py:123: UserWarning: dropout option adds dropout after all but last recurrent layer, so non-zero dropout expects num_layers greater than 1, but got dropout=0.2 and num_layers=1
  warnings.warn(
  Waiting for Playwright MCP to start...
⚠️ 1 servers still connecting, giving extra time...
  No responsive URL found for Playwright, using default
✅ Found server URL: http://localhost:3000
⚠️ URL not responding yet, but process is running
✅ Started playwright via command (process running)
Connection attempt for playwright completed, result: True
✅ playwright added to connected servers
✅ azure-devops connected during extra time
✅ playwright connected during extra time
📊 Final connection summary: 2/2 servers connected
  ✅ azure-devops
  ✅ playwright
Moving on with 2 connected servers
2025-06-14 18:29:41,949 - setup.initialize_agents - INFO - Connected to 2 MCP servers
2025-06-14 18:29:41,951 - setup.initialize_agents - INFO -   ✅ azure-devops (URL: http://127.0.0.1:8000/sse, PID: None)
2025-06-14 18:29:41,951 - setup.initialize_agents - INFO -   ✅ playwright (URL: http://localhost:3000, PID: 12932)
2025-06-14 18:29:41,951 - setup.initialize_agents - INFO - Discovering server capabilities
🔍 Discovering capabilities for azure-devops...
  📡 Detected server type: sse
  💡 SSE-based MCP server detected
  🔧 Attempting SSE tool discovery...
2025-06-14 18:29:41,953 - utils.mcp_sse_client - INFO - Testing SSE connection to http://127.0.0.1:8000/sse
2025-06-14 18:29:41,957 - utils.mcp_sse_client - INFO - ✅ SSE connection established to http://127.0.0.1:8000/sse
2025-06-14 18:29:41,957 - utils.mcp_sse_client - INFO - 🔧 Initializing MCP session via SSE...
2025-06-14 18:29:41,960 - utils.mcp_sse_client - ERROR - ❌ SSE request failed: HTTP 405
2025-06-14 18:29:41,960 - utils.mcp_sse_client - ERROR - Response body: Method Not Allowed
2025-06-14 18:29:41,960 - utils.mcp_sse_client - ERROR - ❌ MCP initialization failed: None
    ❌ Failed to initialize MCP session
  ⚠️ SSE tool discovery failed
✅ Server azure-devops ready - 0 tools available
🔍 Discovering capabilities for playwright...
  📡 Detected server type: http
  🌐 HTTP-based MCP server detected
Error sending MCP request: HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded with url: /jsonrpc (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002124875EF60>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
    ❌ HTTP initialization failed
  ⚠️ HTTP tool discovery failed, server may use different protocol
✅ Server playwright ready - 0 tools available
2025-06-14 18:29:46,032 - setup.initialize_agents - INFO - Setting up MCP Client
2025-06-14 18:29:46,033 - setup.initialize_agents - INFO - Initializing MCP Tool Registry
✅ Loaded MCP tools config from config/mcp_tools.json
✅ Saved MCP tools config to config/mcp_tools.json
2025-06-14 18:29:46,035 - setup.initialize_agents - INFO - Registered 0 MCP tools
2025-06-14 18:29:46,035 - setup.initialize_agents - INFO - Creating MCP-aware agent
2025-06-14 18:29:46,036 - setup.initialize_agents - INFO - Registered MCP agent
2025-06-14 18:29:46,036 - setup.initialize_agents - INFO - Setting up MCP integration with agents
2025-06-14 18:29:46,036 - setup.initialize_agents - INFO - Registering 0 MCP tools with agents
2025-06-14 18:29:46,037 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-14 18:29:46,037 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-14 18:29:46,037 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-14 18:29:46,037 - setup.initialize_agents - INFO - MCP tools registered with all agents
2025-06-14 18:29:46,038 - setup.initialize_agents - INFO - MCP setup completed in background thread
2025-06-14 18:29:54,111 - agents.gemini_agent - INFO - Routing to MCP agent for potential tool execution: what tools do you have?
🔧 Initializing MCP Agent with dynamic tool discovery...
2025-06-14 18:29:54,111 - utils.tool_manager - INFO - Starting comprehensive tool discovery across all MCP servers...
2025-06-14 18:29:54,111 - utils.tool_manager - INFO - Discovering tools from server: azure-devops
2025-06-14 18:29:54,112 - utils.tool_manager - INFO - 🔧 Discovering tools from azure-devops using protocol client...
2025-06-14 18:29:54,112 - utils.mcp_protocol_client - INFO - 🔍 Auto-detecting protocol for server: azure-devops
2025-06-14 18:29:54,112 - utils.mcp_protocol_client - INFO - 📡 Detected protocol: sse
2025-06-14 18:29:54,113 - utils.mcp_sse_client - INFO - Testing SSE connection to http://127.0.0.1:8000/sse
2025-06-14 18:29:54,117 - utils.mcp_sse_client - INFO - ✅ SSE connection established to http://127.0.0.1:8000/sse
2025-06-14 18:29:54,118 - utils.mcp_sse_client - INFO - 🔧 Initializing MCP session via SSE...
2025-06-14 18:29:54,120 - utils.mcp_sse_client - ERROR - ❌ SSE request failed: HTTP 405
2025-06-14 18:29:54,120 - utils.mcp_sse_client - ERROR - Response body: Method Not Allowed
2025-06-14 18:29:54,121 - utils.mcp_sse_client - ERROR - ❌ MCP initialization failed: None
2025-06-14 18:29:54,121 - utils.mcp_protocol_client - WARNING - ⚠️ Connected but initialization failed for azure-devops
2025-06-14 18:29:54,122 - utils.mcp_sse_client - INFO - 🔍 Discovering tools via SSE...
2025-06-14 18:29:54,123 - utils.mcp_sse_client - ERROR - ❌ SSE request failed: HTTP 405
2025-06-14 18:29:54,123 - utils.mcp_sse_client - ERROR - Response body: Method Not Allowed
2025-06-14 18:29:54,123 - utils.mcp_sse_client - WARNING - ⚠️ No tools found in SSE response: None
2025-06-14 18:29:54,124 - utils.tool_manager - WARNING - ⚠️ No tools found for azure-devops
2025-06-14 18:29:54,125 - utils.tool_manager - INFO - No tools found for server: azure-devops
2025-06-14 18:29:54,125 - utils.tool_manager - INFO - Discovering tools from server: playwright
2025-06-14 18:29:54,125 - utils.tool_manager - INFO - 🔧 Discovering tools from playwright using protocol client...
2025-06-14 18:29:54,126 - utils.mcp_protocol_client - INFO - 🔍 Auto-detecting protocol for server: playwright
2025-06-14 18:29:54,126 - utils.mcp_protocol_client - INFO - 📡 Detected protocol: websocket
2025-06-14 18:29:54,126 - utils.mcp_websocket_client - INFO - 🔌 Connecting to WebSocket MCP server: http://localhost:3000
2025-06-14 18:29:58,231 - utils.mcp_websocket_client - ERROR - ❌ WebSocket connection failed: [WinError 1225] The remote computer refused the network connection
2025-06-14 18:29:58,232 - utils.mcp_protocol_client - ERROR - ❌ Failed to connect to playwright
2025-06-14 18:29:58,232 - utils.tool_manager - ERROR - ❌ Failed to connect to playwright
2025-06-14 18:29:58,233 - utils.tool_manager - INFO - No tools found for server: playwright
2025-06-14 18:29:58,233 - utils.tool_manager - INFO - Tool discovery complete: 0 tools from 2 servers
⚠️ No tools discovered during MCP Agent initialization
