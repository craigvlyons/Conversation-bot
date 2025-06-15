Starting Conversation Bot...
2025-06-15 10:48:20,144 - setup.initialize_agents - INFO - Initializing MCP Server Manager
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
2025-06-15 10:48:20,144 - setup.initialize_agents - INFO - Connecting to MCP servers
Connecting to MCP server: azure-devops
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
🌐 Trying URL connection for azure-devops: http://localhost:8000/sse
Starting MCP server: npx @playwright/mcp@latest
/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/subprocess.py:1010: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdin = io.open(p2cwrite, 'wb', bufsize)
/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
✅ Connected to azure-devops via URL
Connection attempt for azure-devops completed, result: True
✅ azure-devops added to connected servers
  ✅ Process started (PID: 89829)
⚠️ TTS not available - text responses only
⚠️ Wake word detection disabled or not available
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
2025-06-15 10:48:32,488 - setup.initialize_agents - INFO - Connected to 2 MCP servers
2025-06-15 10:48:32,488 - setup.initialize_agents - INFO -   ✅ azure-devops (URL: http://localhost:8000/sse, PID: None)
2025-06-15 10:48:32,488 - setup.initialize_agents - INFO -   ✅ playwright (URL: http://localhost:3000, PID: 89829)
2025-06-15 10:48:32,488 - setup.initialize_agents - INFO - Discovering server capabilities
🔍 Discovering capabilities for azure-devops...
  📡 Detected server type: sse
  💡 SSE-based MCP server detected
    🔍 Attempting SSE tool discovery...
    📡 Connecting to SSE server...
2025-06-15 10:48:32,490 - utils.mcp_sse_client - INFO - Testing SSE connection to http://localhost:8000/sse
2025-06-15 10:48:32,559 - utils.mcp_sse_client - INFO - ✅ SSE connection established to http://localhost:8000/sse
    🔧 Initializing MCP session...
2025-06-15 10:48:32,559 - utils.mcp_sse_client - INFO - 🔧 Initializing MCP session via SSE...
2025-06-15 10:48:32,560 - utils.mcp_sse_client - INFO - ✅ MCP initialization successful
    🔍 Discovering tools...
2025-06-15 10:48:32,560 - utils.mcp_sse_client - INFO - 🔍 Discovering tools via SSE...
2025-06-15 10:48:32,561 - utils.mcp_sse_client - INFO - ✅ Discovered 3 tools via SSE using method 'getTools'
    ✅ Discovered 3 tools via SSE: ['get_work_items', 'create_work_item', 'update_work_item']
✅ Server azure-devops ready - 3 tools available
🔍 Discovering capabilities for playwright...
  📡 Detected server type: stdio
  💬 Stdio-based MCP server detected
    🔍 Attempting stdio tool discovery...
    🔧 Initializing MCP session...
    ✅ MCP session initialized
    🔍 Requesting tools list...
    ✅ Discovered 25 tools via stdio: ['browser_close', 'browser_resize', 'browser_console_messages', 'browser_handle_dialog', 'browser_file_upload', 'browser_install', 'browser_press_key', 'browser_navigate', 'browser_navigate_back', 'browser_navigate_forward', 'browser_network_requests', 'browser_pdf_save', 'browser_take_screenshot', 'browser_snapshot', 'browser_click', 'browser_drag', 'browser_hover', 'browser_type', 'browser_select_option', 'browser_tab_list', 'browser_tab_new', 'browser_tab_select', 'browser_tab_close', 'browser_generate_playwright_test', 'browser_wait_for']
✅ Server playwright ready - 25 tools available
2025-06-15 10:48:32,566 - setup.initialize_agents - INFO - Setting up MCP Client
2025-06-15 10:48:32,567 - setup.initialize_agents - INFO - Initializing MCP Tool Registry
✅ Loaded MCP tools config from config/mcp_tools.json
✅ Saved MCP tools config to config/mcp_tools.json
2025-06-15 10:48:32,568 - setup.initialize_agents - INFO - Registered 28 MCP tools
2025-06-15 10:48:32,568 - setup.initialize_agents - INFO - Creating MCP-aware agent
2025-06-15 10:48:32,568 - setup.initialize_agents - INFO - Initializing MCP agent with tools
🔧 Initializing MCP Agent...
📋 Using cached tools from tool registry...
✅ MCP Agent initialized with 28 cached tools
2025-06-15 10:48:32,568 - setup.initialize_agents - INFO - Registered MCP agent
2025-06-15 10:48:32,569 - setup.initialize_agents - INFO - Setting up MCP integration with agents
2025-06-15 10:48:32,569 - setup.initialize_agents - INFO - Registering 28 MCP tools with agents
2025-06-15 10:48:32,569 - setup.initialize_agents - INFO - MCP routing enabled for all agents - 28 tools available via dynamic execution
2025-06-15 10:48:32,569 - setup.initialize_agents - INFO - MCP setup completed in background thread
2025-06-15 10:49:30,982 - asyncio - ERROR - Unclosed client session
client_session: <aiohttp.client.ClientSession object at 0x14db511f0>
2025-06-15 10:49:30,983 - asyncio - ERROR - Unclosed connector
connections: ['[(<aiohttp.client_proto.ResponseHandler object at 0x14db38530>, 42069.922860875)]']
connector: <aiohttp.connector.TCPConnector object at 0x16a5b08f0>
2025-06-15 10:49:40,303 - agents.gemini_agent - INFO - Routing to MCP agent for potential tool execution: get my azure work items
2025-06-15 10:49:52,513 - httpx - INFO - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent "HTTP/1.1 200 OK"