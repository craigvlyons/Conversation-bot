Starting Conversation Bot...
Activating virtual environment...
Warning: No AI API keys found in environment variables.
Please set GEMINI_KEY and/or OPENAI_KEY in your .env file or environment.
Warning: PRORCUPINE_KEY not found. Wake word detection may not work.
Launching Conversation Bot...
==================================================
pygame 2.6.1 (SDL 2.28.4, Python 3.12.1)
Hello from the pygame community. https://www.pygame.org/contribute.html
2025-06-14 17:36:43,982 - setup.initialize_agents - INFO - MCP setup started in background thread
Starting Conversation Bot...
2025-06-14 17:36:43,984 - setup.initialize_agents - INFO - Initializing MCP Server Manager
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
2025-06-14 17:36:43,985 - setup.initialize_agents - INFO - Connecting to MCP servers
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 14180)
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
2025-06-14 17:37:03,036 - setup.initialize_agents - INFO - Connected to 2 MCP servers
2025-06-14 17:37:03,036 - setup.initialize_agents - INFO -   ✅ azure-devops (URL: http://127.0.0.1:8000/sse, PID: None)
2025-06-14 17:37:03,036 - setup.initialize_agents - INFO -   ✅ playwright (URL: http://localhost:3000, PID: 14180)
2025-06-14 17:37:03,036 - setup.initialize_agents - INFO - Discovering server capabilities
🔍 Discovering capabilities for azure-devops...
  📡 Detected server type: sse
  💡 SSE-based MCP server detected
  ⚠️ SSE tool discovery not yet implemented
  💡 Tools will be available when proper SSE client is added
✅ Server azure-devops ready - 0 tools available
🔍 Discovering capabilities for playwright...
  📡 Detected server type: http
  🌐 HTTP-based MCP server detected
Error sending MCP request: HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded with url: /jsonrpc (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001A7FC390E00>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
    ❌ HTTP initialization failed
  ⚠️ HTTP tool discovery failed, server may use different protocol
✅ Server playwright ready - 0 tools available
2025-06-14 17:37:07,139 - setup.initialize_agents - INFO - Setting up MCP Client
2025-06-14 17:37:07,139 - setup.initialize_agents - INFO - Initializing MCP Tool Registry
✅ Loaded MCP tools config from config/mcp_tools.json
✅ Saved MCP tools config to config/mcp_tools.json
2025-06-14 17:37:07,141 - setup.initialize_agents - INFO - Registered 0 MCP tools
2025-06-14 17:37:07,141 - setup.initialize_agents - INFO - Creating MCP-aware agent
2025-06-14 17:37:07,142 - setup.initialize_agents - ERROR - Error in MCP setup thread: MCPAgent.__init__() takes from 1 to 3 positional arguments but 4 were given
2025-06-14 17:37:07,142 - setup.initialize_agents - ERROR - Traceback (most recent call last):
  File "C:\convo_bot\setup\initialize_agents.py", line 90, in run_mcp_setup_thread
    mcp_agent = MCPAgent("mcp_agent", server_manager, tool_registry)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: MCPAgent.__init__() takes from 1 to 3 positional arguments but 4 were given

