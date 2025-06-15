Starting Conversation Bot...
Activating virtual environment...
Warning: No AI API keys found in environment variables.
Please set GEMINI_KEY and/or OPENAI_KEY in your .env file or environment.
Warning: PRORCUPINE_KEY not found. Wake word detection may not work.
Launching Conversation Bot...
==================================================
pygame 2.6.1 (SDL 2.28.4, Python 3.12.1)
Hello from the pygame community. https://www.pygame.org/contribute.html
2025-06-15 07:09:41,673 - setup.initialize_agents - INFO - ✅ Found API keys: GEMINI_KEY, OPENAI_KEY
2025-06-15 07:09:41,951 - setup.initialize_agents - INFO - ✅ Gemini agents initialized successfully
2025-06-15 07:09:41,953 - setup.initialize_agents - INFO - ✅ OpenAI agent initialized successfully
2025-06-15 07:09:41,953 - setup.initialize_agents - INFO - Agent registration completed
2025-06-15 07:09:41,954 - setup.initialize_agents - INFO - MCP setup started in background thread
Starting Conversation Bot...
2025-06-15 07:09:41,955 - setup.initialize_agents - INFO - Initializing MCP Server Manager
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
2025-06-15 07:09:41,956 - setup.initialize_agents - INFO - Connecting to MCP servers
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1010: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdin = io.open(p2cwrite, 'wb', bufsize)
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 19736)
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
2025-06-15 07:10:00,819 - setup.initialize_agents - INFO - Connected to 2 MCP servers
2025-06-15 07:10:00,820 - setup.initialize_agents - INFO -   ✅ azure-devops (URL: http://127.0.0.1:8000/sse, PID: None)
2025-06-15 07:10:00,820 - setup.initialize_agents - INFO -   ✅ playwright (URL: http://localhost:3000, PID: 19736)
2025-06-15 07:10:00,827 - setup.initialize_agents - INFO - Discovering server capabilities
🔍 Discovering capabilities for azure-devops...
  📡 Detected server type: sse
  💡 SSE-based MCP server detected
    🔍 Attempting SSE tool discovery...
    📡 Connecting to SSE server...
2025-06-15 07:10:00,838 - utils.mcp_sse_client - INFO - Testing SSE connection to http://127.0.0.1:8000/sse
2025-06-15 07:10:00,844 - utils.mcp_sse_client - INFO - ✅ SSE connection established to http://127.0.0.1:8000/sse
    🔧 Initializing MCP session...
2025-06-15 07:10:00,845 - utils.mcp_sse_client - INFO - 🔧 Initializing MCP session via SSE...
2025-06-15 07:10:31,603 - utils.mcp_sse_client - ERROR - ❌ Error waiting for SSE response:
2025-06-15 07:10:31,604 - utils.mcp_sse_client - ERROR - ❌ MCP initialization failed: None
    🔍 Discovering tools...
2025-06-15 07:10:31,605 - utils.mcp_sse_client - INFO - 🔍 Discovering tools via SSE...
2025-06-15 07:11:02,602 - utils.mcp_sse_client - ERROR - ❌ Error waiting for SSE response:
2025-06-15 07:11:02,604 - utils.mcp_sse_client - WARNING - ⚠️ No tools found in SSE response: None
    ⚠️ No tools returned from SSE discovery
2025-06-15 07:11:02,606 - asyncio - ERROR - Unclosed client session
client_session: <aiohttp.client.ClientSession object at 0x0000025D7543D850>
  ⚠️ SSE tool discovery failed
✅ Server azure-devops ready - 0 tools available
🔍 Discovering capabilities for playwright...
  📡 Detected server type: stdio
  💬 Stdio-based MCP server detected
    🔍 Attempting stdio tool discovery...
    🔧 Initializing MCP session...
    ✅ MCP session initialized
    🔍 Requesting tools list...
    ✅ Discovered 25 tools via stdio: ['browser_close', 'browser_resize', 'browser_console_messages', 'browser_handle_dialog', 'browser_file_upload', 'browser_install', 'browser_press_key', 'browser_navigate', 'browser_navigate_back', 'browser_navigate_forward', 'browser_network_requests', 'browser_pdf_save', 'browser_take_screenshot', 'browser_snapshot', 'browser_click', 'browser_drag', 'browser_hover', 'browser_type', 'browser_select_option', 'browser_tab_list', 'browser_tab_new', 'browser_tab_select', 'browser_tab_close', 'browser_generate_playwright_test', 'browser_wait_for']
✅ Server playwright ready - 25 tools available
2025-06-15 07:11:06,618 - setup.initialize_agents - INFO - Setting up MCP Client
2025-06-15 07:11:06,618 - setup.initialize_agents - INFO - Initializing MCP Tool Registry
✅ Loaded MCP tools config from config/mcp_tools.json
✅ Saved MCP tools config to config/mcp_tools.json
2025-06-15 07:11:06,620 - setup.initialize_agents - INFO - Registered 25 MCP tools
2025-06-15 07:11:06,620 - setup.initialize_agents - INFO - Creating MCP-aware agent
2025-06-15 07:11:06,621 - setup.initialize_agents - INFO - Registered MCP agent
2025-06-15 07:11:06,621 - setup.initialize_agents - INFO - Setting up MCP integration with agents
2025-06-15 07:11:06,621 - setup.initialize_agents - INFO - Registering 0 MCP tools with agents
2025-06-15 07:11:06,621 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-15 07:11:06,621 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-15 07:11:06,622 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-15 07:11:06,622 - setup.initialize_agents - INFO - MCP tools registered with all agents
2025-06-15 07:11:06,622 - setup.initialize_agents - INFO - MCP setup completed in background thread
2025-06-15 07:15:31,694 - agents.gemini_agent - INFO - Routing to MCP agent for potential tool execution: what tools do you have?
🔧 Initializing MCP Agent with dynamic tool discovery...
2025-06-15 07:15:31,695 - utils.tool_manager - INFO - Starting comprehensive tool discovery across all MCP servers...
2025-06-15 07:15:31,695 - utils.tool_manager - INFO - Discovering tools from server: azure-devops
2025-06-15 07:15:31,695 - utils.tool_manager - INFO - 🔧 Discovering tools from azure-devops using protocol client...
2025-06-15 07:15:31,696 - utils.mcp_protocol_client - INFO - 🔍 Auto-detecting protocol for server: azure-devops
2025-06-15 07:15:31,696 - utils.mcp_protocol_client - INFO - 📡 Detected protocol: sse
2025-06-15 07:15:31,696 - utils.mcp_sse_client - INFO - Testing SSE connection to http://127.0.0.1:8000/sse
2025-06-15 07:15:31,700 - utils.mcp_sse_client - INFO - ✅ SSE connection established to http://127.0.0.1:8000/sse
2025-06-15 07:15:31,700 - utils.mcp_sse_client - INFO - 🔧 Initializing MCP session via SSE...
2025-06-15 07:16:02,597 - utils.mcp_sse_client - ERROR - ❌ Error waiting for SSE response:
2025-06-15 07:16:02,598 - utils.mcp_sse_client - ERROR - ❌ MCP initialization failed: None
2025-06-15 07:16:02,599 - utils.mcp_protocol_client - WARNING - ⚠️ Connected but initialization failed for azure-devops
2025-06-15 07:16:02,599 - utils.mcp_sse_client - INFO - 🔍 Discovering tools via SSE...
2025-06-15 07:16:33,595 - utils.mcp_sse_client - ERROR - ❌ Error waiting for SSE response:
2025-06-15 07:16:33,596 - utils.mcp_sse_client - WARNING - ⚠️ No tools found in SSE response: None
2025-06-15 07:16:33,597 - utils.tool_manager - WARNING - ⚠️ No tools found for azure-devops
2025-06-15 07:16:33,597 - utils.tool_manager - INFO - No tools found for server: azure-devops
2025-06-15 07:16:33,597 - utils.tool_manager - INFO - Discovering tools from server: playwright
2025-06-15 07:16:33,598 - utils.tool_manager - INFO - 🔧 Discovering tools from playwright using protocol client...
2025-06-15 07:16:33,598 - utils.mcp_protocol_client - INFO - 🔍 Auto-detecting protocol for server: playwright
2025-06-15 07:16:33,598 - utils.mcp_protocol_client - INFO - 📡 Detected protocol: websocket
2025-06-15 07:16:33,598 - utils.mcp_websocket_client - INFO - 🔌 Connecting to WebSocket MCP server: http://localhost:3000
2025-06-15 07:16:37,726 - utils.mcp_websocket_client - ERROR - ❌ WebSocket connection failed: [WinError 1225] The remote computer refused the network connection
2025-06-15 07:16:37,727 - utils.mcp_protocol_client - ERROR - ❌ Failed to connect to playwright
2025-06-15 07:16:37,728 - utils.tool_manager - ERROR - ❌ Failed to connect to playwright
2025-06-15 07:16:37,728 - utils.tool_manager - INFO - No tools found for server: playwright
2025-06-15 07:16:37,728 - utils.tool_manager - INFO - Tool discovery complete: 0 tools from 2 servers
⚠️ No tools discovered during MCP Agent initialization
