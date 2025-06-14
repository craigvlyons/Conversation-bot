Starting Conversation Bot...
Activating virtual environment...
Warning: No AI API keys found in environment variables.
Please set GEMINI_KEY and/or OPENAI_KEY in your .env file or environment.
Warning: PRORCUPINE_KEY not found. Wake word detection may not work.
Launching Conversation Bot...
==================================================
pygame 2.6.1 (SDL 2.28.4, Python 3.12.1)
Hello from the pygame community. https://www.pygame.org/contribute.html
2025-06-14 13:57:44,620 - setup.initialize_agents - INFO - MCP setup started in background thread
Starting Conversation Bot...
2025-06-14 13:57:44,622 - setup.initialize_agents - INFO - Initializing MCP Server Manager
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
2025-06-14 13:57:44,629 - setup.initialize_agents - INFO - Connecting to MCP servers
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
Starting MCP server: npx.cmd @playwright/mcp@latest
✅ Connected to azure-devops via URL
Connection attempt for azure-devops completed, result: True
✅ azure-devops added to connected servers
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 21472)
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
2025-06-14 13:58:03,518 - setup.initialize_agents - INFO - Connected to 2 MCP servers
2025-06-14 13:58:03,521 - setup.initialize_agents - INFO -   ✅ azure-devops (URL: http://127.0.0.1:8000/sse, PID: None)
2025-06-14 13:58:03,522 - setup.initialize_agents - INFO -   ✅ playwright (URL: http://localhost:3000, PID: 21472)
2025-06-14 13:58:03,522 - setup.initialize_agents - INFO - Discovering server capabilities
🔍 Discovering capabilities for azure-devops...
Request failed: 404
  ❌ Failed to initialize azure-devops
  🔧 Discovering tools...
  📡 Sending JSON-RPC request to: http://127.0.0.1:8000/jsonrpc
  📤 Method: getTools
  📥 Response status: 404
  ❌ Request failed: 404
  📄 Error response: Not Found
    No tools found
✅ Connected to MCP server: azure-devops
   Tools: 0
🔍 Discovering capabilities for playwright...
Error sending MCP request: HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded with url: /jsonrpc (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x0000028447A8D0A0>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
  ❌ Failed to initialize playwright
  🔧 Discovering tools...
  📡 Sending JSON-RPC request to: http://localhost:3000/jsonrpc
  📤 Method: getTools
  ❌ Error sending MCP request: HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded with url: /jsonrpc (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x0000028447A0B9E0>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
    No tools found
✅ Connected to MCP server: playwright
   Tools: 0
2025-06-14 13:58:11,769 - setup.initialize_agents - INFO - Setting up MCP Client
2025-06-14 13:58:11,770 - setup.initialize_agents - INFO - Initializing MCP Tool Registry
✅ Loaded MCP tools config from config/mcp_tools.json
✅ Saved MCP tools config to config/mcp_tools.json
2025-06-14 13:58:11,774 - setup.initialize_agents - INFO - Registered 0 MCP tools
2025-06-14 13:58:11,777 - setup.initialize_agents - INFO - Creating MCP-aware agent
2025-06-14 13:58:11,778 - setup.initialize_agents - INFO - Registered MCP agent
2025-06-14 13:58:11,779 - setup.initialize_agents - INFO - Setting up MCP integration with agents
2025-06-14 13:58:11,779 - setup.initialize_agents - INFO - Registering 0 MCP tools with agents
2025-06-14 13:58:11,780 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-14 13:58:11,780 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-14 13:58:11,781 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-14 13:58:11,781 - setup.initialize_agents - INFO - MCP tools registered with all agents
2025-06-14 13:58:11,781 - setup.initialize_agents - INFO - MCP setup completed in background thread
Traceback (most recent call last):
  File "C:\convo_bot\ui\chatwindow.py", line 331, in eventFilter
    self.send_message()
  File "C:\convo_bot\ui\chatwindow.py", line 250, in send_message
    asyncio.create_task(self.get_agent_response(text))
  File "C:\Python312\Lib\asyncio\tasks.py", line 417, in create_task
    loop = events.get_running_loop()
           ^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: no running event loop
Press any key to continue . . .


(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_tool_discovery_simple.py
[2025-06-14 13:56:26,021] INFO - Simple MCP Tool Discovery Test
[2025-06-14 13:56:26,021] INFO - This test uses our custom server on port 8001
[2025-06-14 13:56:26,021] INFO - This test uses our custom server on port 8001
[2025-06-14 13:56:26,021] INFO - Your production server on port 8000 will not be affected
[2025-06-14 13:56:26,022] INFO -
[2025-06-14 13:56:26,022] INFO - === Testing Custom MCP Server ===
[2025-06-14 13:56:30,120] INFO - Starting custom Azure DevOps MCP server on port 8001...
[2025-06-14 13:56:33,137] ERROR - Server failed to start:
[2025-06-14 13:56:33,138] ERROR - STDOUT:
[2025-06-14 13:56:33,138] ERROR - STDERR: Traceback (most recent call last):
  File "C:\convo_bot\azure_devops_server.py", line 14, in <module>
    import aiohttp_cors
ModuleNotFoundError: No module named 'aiohttp_cors'

[2025-06-14 13:56:33,138] INFO - Stopping test server...
[2025-06-14 13:56:33,138] INFO - ✅ Test server stopped

Test Result: FAIL

❌ Test failed. Check the logs above for details.
(py312) PS C:\convo_bot>
