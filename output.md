Starting Conversation Bot...
Activating virtual environment...
Warning: No AI API keys found in environment variables.
Please set GEMINI_KEY and/or OPENAI_KEY in your .env file or environment.
Warning: PRORCUPINE_KEY not found. Wake word detection may not work.
Launching Conversation Bot...
==================================================
pygame 2.6.1 (SDL 2.28.4, Python 3.12.1)
Hello from the pygame community. https://www.pygame.org/contribute.html
2025-06-15 06:47:49,927 - setup.initialize_agents - INFO - ✅ Found API keys: GEMINI_KEY, OPENAI_KEY
2025-06-15 06:47:50,231 - setup.initialize_agents - INFO - ✅ Gemini agents initialized successfully
2025-06-15 06:47:50,232 - setup.initialize_agents - INFO - ✅ OpenAI agent initialized successfully
2025-06-15 06:47:50,232 - setup.initialize_agents - INFO - Agent registration completed
2025-06-15 06:47:50,245 - setup.initialize_agents - INFO - MCP setup started in background thread
Starting Conversation Bot...
2025-06-15 06:47:50,246 - setup.initialize_agents - INFO - Initializing MCP Server Manager
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
2025-06-15 06:47:50,247 - setup.initialize_agents - INFO - Connecting to MCP servers
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
✅ Connected to azure-devops via URL
Connection attempt for azure-devops completed, result: True
✅ azure-devops added to connected servers
  ✅ Process started (PID: 44992)
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
2025-06-15 06:48:08,956 - setup.initialize_agents - INFO - Connected to 2 MCP servers
2025-06-15 06:48:08,958 - setup.initialize_agents - INFO -   ✅ azure-devops (URL: http://127.0.0.1:8000/sse, PID: None)
2025-06-15 06:48:08,958 - setup.initialize_agents - INFO -   ✅ playwright (URL: http://localhost:3000, PID: 44992)
2025-06-15 06:48:08,959 - setup.initialize_agents - INFO - Discovering server capabilities
🔍 Discovering capabilities for azure-devops...
  📡 Detected server type: sse
  💡 SSE-based MCP server detected
    🔍 Attempting SSE tool discovery...
    📡 Connecting to SSE server...
2025-06-15 06:48:08,971 - utils.mcp_sse_client - INFO - Testing SSE connection to http://127.0.0.1:8000/sse
2025-06-15 06:48:08,978 - utils.mcp_sse_client - INFO - ✅ SSE connection established to http://127.0.0.1:8000/sse
    🔧 Initializing MCP session...
2025-06-15 06:48:08,978 - utils.mcp_sse_client - INFO - 🔧 Initializing MCP session via SSE...
2025-06-15 06:48:39,602 - utils.mcp_sse_client - ERROR - ❌ Error waiting for SSE response:
2025-06-15 06:48:39,603 - utils.mcp_sse_client - ERROR - ❌ MCP initialization failed: None
    🔍 Discovering tools...
2025-06-15 06:48:39,604 - utils.mcp_sse_client - INFO - 🔍 Discovering tools via SSE...
2025-06-15 06:49:10,606 - utils.mcp_sse_client - ERROR - ❌ Error waiting for SSE response:
2025-06-15 06:49:10,607 - utils.mcp_sse_client - WARNING - ⚠️ No tools found in SSE response: None
    ⚠️ No tools returned from SSE discovery
2025-06-15 06:49:10,619 - asyncio - ERROR - Unclosed client session
client_session: <aiohttp.client.ClientSession object at 0x00000250DE495CD0>
  ⚠️ SSE tool discovery failed
✅ Server azure-devops ready - 0 tools available
🔍 Discovering capabilities for playwright...
  📡 Detected server type: stdio
  💬 Stdio-based MCP server detected
    🔍 Attempting stdio tool discovery...
    🔧 Initializing MCP session...
    ❌ Stdio discovery error: 'NoneType' object has no attribute 'write'
  ⚠️ Stdio tool discovery failed
✅ Server playwright ready - 0 tools available
2025-06-15 06:49:14,623 - setup.initialize_agents - INFO - Setting up MCP Client
2025-06-15 06:49:14,623 - setup.initialize_agents - INFO - Initializing MCP Tool Registry
✅ Loaded MCP tools config from config/mcp_tools.json
✅ Saved MCP tools config to config/mcp_tools.json
2025-06-15 06:49:14,626 - setup.initialize_agents - INFO - Registered 0 MCP tools
2025-06-15 06:49:14,626 - setup.initialize_agents - INFO - Creating MCP-aware agent
2025-06-15 06:49:14,626 - setup.initialize_agents - INFO - Registered MCP agent
2025-06-15 06:49:14,626 - setup.initialize_agents - INFO - Setting up MCP integration with agents
2025-06-15 06:49:14,626 - setup.initialize_agents - INFO - Registering 0 MCP tools with agents
2025-06-15 06:49:14,627 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-15 06:49:14,627 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-15 06:49:14,627 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-15 06:49:14,627 - setup.initialize_agents - INFO - MCP tools registered with all agents
2025-06-15 06:49:14,627 - setup.initialize_agents - INFO - MCP setup completed in background thread
