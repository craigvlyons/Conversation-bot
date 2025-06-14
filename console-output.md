(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_mcp_integration.py
[2025-06-14 13:02:11,993] __main__ - INFO - Starting MCP Integration Tests
[2025-06-14 13:02:11,993] __main__ - INFO - === Testing MCP Integration ===
[2025-06-14 13:02:11,994] __main__ - INFO - 1. Testing MCP server connection...
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
[2025-06-14 13:02:11,994] __main__ - INFO - Loaded 2 servers from config
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
[2025-06-14 13:02:11,997] utils.platform_config - INFO - Platform detected: windows
[2025-06-14 13:02:12,000] utils.platform_config - INFO - Project root: c:\convo_bot
[2025-06-14 13:02:12,001] utils.platform_config - INFO - Base directory: c:\convo_bot
✅ Connected to azure-devops via URL
Connection attempt for azure-devops completed, result: True
✅ azure-devops added to connected servers
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 25684)
  Waiting for Playwright MCP to start...
  No responsive URL found for Playwright, using default
✅ Found server URL: http://localhost:3000
⚠️ URL not responding yet, but process is running
✅ Started playwright via command (process running)
Connection attempt for playwright completed, result: True
✅ playwright added to connected servers
📊 Final connection summary: 2/2 servers connected
  ✅ azure-devops
  ✅ playwright
Moving on with 2 connected servers
[2025-06-14 13:02:30,727] __main__ - INFO - Connected to 2 MCP servers
[2025-06-14 13:02:30,727] __main__ - INFO -   Connected: azure-devops (URL: http://127.0.0.1:8000/sse, Process: None)
[2025-06-14 13:02:30,728] __main__ - INFO -   Connected: playwright (URL: http://localhost:3000, Process: 25684)
[2025-06-14 13:02:30,733] __main__ - INFO - 2. Testing tool discovery...
✅ Loaded MCP tools config from config/mcp_tools.json
✅ Saved MCP tools config to config/mcp_tools.json
[2025-06-14 13:02:30,743] __main__ - INFO - Discovered 0 tools
[2025-06-14 13:02:30,743] __main__ - INFO - Available tools: []
[2025-06-14 13:02:30,744] __main__ - WARNING - No tools discovered from MCP servers
[2025-06-14 13:02:30,745] __main__ - WARNING - This is unexpected since servers did connect
[2025-06-14 13:02:30,747] __main__ - INFO - 3. Testing MCP agent creation...
[2025-06-14 13:02:30,748] __main__ - INFO - MCP agent has 0 tools
[2025-06-14 13:02:30,749] __main__ - INFO - 4. Testing integration setup...
[2025-06-14 13:02:30,749] __main__ - INFO - MCP integration configured
[2025-06-14 13:02:30,751] __main__ - INFO - 6. Testing agent registration...
[2025-06-14 13:02:30,751] __main__ - INFO - Agent registration successful
[2025-06-14 13:02:30,751] __main__ - INFO - === MCP Integration Test Completed ===
[2025-06-14 13:02:30,751] __main__ - INFO - ✅ Test PASSED: Servers connected successfully
Shutting down MCP server: playwright
  ✅ Server playwright terminated
[2025-06-14 13:02:30,869] __main__ - INFO - Cleaned up MCP servers
[2025-06-14 13:02:30,871] __main__ - INFO - === Testing Agent Tool Integration ===
[2025-06-14 13:02:31,547] __main__ - INFO - Agent MCP enabled: True
[2025-06-14 13:02:31,548] __main__ - INFO - Agent MCP tools: ['browser_navigate', 'browser_screenshot', 'test_automation_tool']
[2025-06-14 13:02:31,549] __main__ - INFO -   browser_navigate: Navigate to a URL using browser automation
[2025-06-14 13:02:31,549] __main__ - INFO -   browser_screenshot: Take a screenshot of the current browser page
[2025-06-14 13:02:31,550] __main__ - INFO -   test_automation_tool: Test tool for browser automation and testing
[2025-06-14 13:02:31,550] __main__ - INFO - Input: 'open google.com' -> Tool trigger: browser_navigate
[2025-06-14 13:02:31,552] __main__ - INFO - Input: 'take a screenshot' -> Tool trigger: browser_screenshot
[2025-06-14 13:02:31,552] __main__ - INFO - Input: 'navigate to example.com' -> Tool trigger: browser_navigate
[2025-06-14 13:02:31,552] __main__ - INFO - Input: 'browser automation test' -> Tool trigger: browser_navigate
[2025-06-14 13:02:31,552] __main__ - INFO - Input: 'what tools are available' -> Tool trigger: None   
[2025-06-14 13:02:31,553] __main__ - INFO - Input: 'hello world' -> Tool trigger: None
[2025-06-14 13:02:31,553] __main__ - INFO - Agent tool integration test completed
[2025-06-14 13:02:31,559] __main__ - INFO - === Test Summary ===
[2025-06-14 13:02:31,565] __main__ - INFO - MCP Integration Test: PASS
[2025-06-14 13:02:31,566] __main__ - INFO - Agent Tool Integration Test: PASS
[2025-06-14 13:02:31,567] __main__ - INFO - Overall Result: PASS
(py312) PS C:\convo_bot> 

Starting Conversation Bot...
Activating virtual environment...
Warning: No AI API keys found in environment variables.
Please set GEMINI_KEY and/or OPENAI_KEY in your .env file or environment.
Warning: PRORCUPINE_KEY not found. Wake word detection may not work.
Launching Conversation Bot...
==================================================
pygame 2.6.1 (SDL 2.28.4, Python 3.12.1)
Hello from the pygame community. https://www.pygame.org/contribute.html
2025-06-14 13:04:06,980 - setup.initialize_agents - INFO - MCP setup started in background thread
Starting Conversation Bot...
2025-06-14 13:04:06,981 - setup.initialize_agents - INFO - Initializing MCP Server Manager
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
2025-06-14 13:04:06,985 - setup.initialize_agents - INFO - Connecting to MCP servers
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
✅ Connected to azure-devops via URL
Connection attempt for azure-devops completed, result: True
✅ azure-devops added to connected servers
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 40640)
C:\convo_bot\.venv\Lib\site-packages\torch\nn\utils\weight_norm.py:143: FutureWarning: `torch.nn.utils.weight_norm` is deprecated in favor of `torch.nn.utils.parametrizations.weight_norm`.
  WeightNorm.apply(module, name, dim)
  Waiting for Playwright MCP to start...
C:\convo_bot\.venv\Lib\site-packages\torch\nn\modules\rnn.py:123: UserWarning: dropout option adds dropout after all but last recurrent layer, so non-zero dropout expects num_layers greater than 1, but got dropout=0.2 and num_layers=1
  warnings.warn(
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
2025-06-14 13:04:25,827 - setup.initialize_agents - INFO - Connected to 2 MCP servers
2025-06-14 13:04:25,828 - setup.initialize_agents - INFO -   ✅ azure-devops (URL: http://127.0.0.1:8000/sse, PID: None)
2025-06-14 13:04:25,828 - setup.initialize_agents - INFO -   ✅ playwright (URL: http://localhost:3000, PID: 40640)
2025-06-14 13:04:25,828 - setup.initialize_agents - INFO - Discovering server capabilities
❌ Failed to get capabilities for azure-devops: 404
❌ Error discovering capabilities for playwright: HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded with url: /capabilities (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002AA691C1F40>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
2025-06-14 13:04:29,953 - setup.initialize_agents - INFO - Setting up MCP Client
2025-06-14 13:04:29,955 - setup.initialize_agents - INFO - Initializing MCP Tool Registry
✅ Loaded MCP tools config from config/mcp_tools.json
✅ Saved MCP tools config to config/mcp_tools.json
2025-06-14 13:04:29,961 - setup.initialize_agents - INFO - Registered 0 MCP tools
2025-06-14 13:04:29,961 - setup.initialize_agents - INFO - Creating MCP-aware agent
2025-06-14 13:04:29,963 - setup.initialize_agents - INFO - Registered MCP agent
2025-06-14 13:04:29,964 - setup.initialize_agents - INFO - Setting up MCP integration with agents
2025-06-14 13:04:29,964 - setup.initialize_agents - INFO - Registering 0 MCP tools with agents
2025-06-14 13:04:29,965 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-14 13:04:29,969 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-14 13:04:29,970 - utils.mcp_agent_integration - INFO - No MCP tools to register
2025-06-14 13:04:29,970 - setup.initialize_agents - INFO - MCP tools registered with all agents
2025-06-14 13:04:29,971 - setup.initialize_agents - INFO - MCP setup completed in background thread
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