(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_mcp_integration.py
[2025-06-14 13:26:00,178] __main__ - INFO - Starting MCP Integration Tests
[2025-06-14 13:26:00,179] __main__ - INFO - === Testing MCP Integration ===
[2025-06-14 13:26:00,180] __main__ - INFO - 1. Testing MCP server connection...
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
[2025-06-14 13:26:00,180] __main__ - INFO - Loaded 2 servers from config
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
[2025-06-14 13:26:00,185] utils.platform_config - INFO - Platform detected: windows
[2025-06-14 13:26:00,186] utils.platform_config - INFO - Project root: c:\convo_bot
[2025-06-14 13:26:00,186] utils.platform_config - INFO - Base directory: c:\convo_bot
✅ Connected to azure-devops via URL
Connection attempt for azure-devops completed, result: True
✅ azure-devops added to connected servers
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 3124)
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
[2025-06-14 13:26:19,010] __main__ - INFO - Connected to 2 MCP servers
[2025-06-14 13:26:19,011] __main__ - INFO -   Connected: azure-devops (URL: http://127.0.0.1:8000, Process: None)
[2025-06-14 13:26:19,012] __main__ - INFO -   Connected: playwright (URL: http://localhost:3000, Process: 3124)
[2025-06-14 13:26:19,019] __main__ - INFO - 2. Testing tool discovery...
✅ Loaded MCP tools config from config/mcp_tools.json
✅ Saved MCP tools config to config/mcp_tools.json
[2025-06-14 13:26:19,045] __main__ - INFO - Discovered 0 tools
[2025-06-14 13:26:19,046] __main__ - INFO - Available tools: []
[2025-06-14 13:26:19,047] __main__ - WARNING - No tools discovered from MCP servers
[2025-06-14 13:26:19,047] __main__ - WARNING - This is unexpected since servers did connect
[2025-06-14 13:26:19,049] __main__ - INFO - 3. Testing MCP agent creation...
[2025-06-14 13:26:19,053] __main__ - INFO - MCP agent has 0 tools
[2025-06-14 13:26:19,053] __main__ - INFO - 4. Testing integration setup...
[2025-06-14 13:26:19,054] __main__ - INFO - MCP integration configured
[2025-06-14 13:26:19,055] __main__ - INFO - 6. Testing agent registration...
[2025-06-14 13:26:19,055] __main__ - INFO - Agent registration successful
[2025-06-14 13:26:19,056] __main__ - INFO - === MCP Integration Test Completed ===
[2025-06-14 13:26:19,056] __main__ - INFO - ✅ Test PASSED: Servers connected successfully
Shutting down MCP server: playwright
  ✅ Server playwright terminated
[2025-06-14 13:26:19,170] __main__ - INFO - Cleaned up MCP servers
[2025-06-14 13:26:19,170] __main__ - INFO - === Testing Agent Tool Integration ===
[2025-06-14 13:26:19,895] __main__ - INFO - Agent MCP enabled: True
[2025-06-14 13:26:19,895] __main__ - INFO - Agent MCP tools: ['browser_navigate', 'browser_screenshot', 'test_automation_tool']
[2025-06-14 13:26:19,896] __main__ - INFO -   browser_navigate: Navigate to a URL using browser automation
[2025-06-14 13:26:19,896] __main__ - INFO -   browser_screenshot: Take a screenshot of the current browser page
[2025-06-14 13:26:19,896] __main__ - INFO -   test_automation_tool: Test tool for browser automation and testing
[2025-06-14 13:26:19,897] __main__ - INFO - Input: 'open google.com' -> Tool trigger: browser_navigate
[2025-06-14 13:26:19,897] __main__ - INFO - Input: 'take a screenshot' -> Tool trigger: browser_screenshot
[2025-06-14 13:26:19,898] __main__ - INFO - Input: 'navigate to example.com' -> Tool trigger: browser_navigate
[2025-06-14 13:26:19,898] __main__ - INFO - Input: 'browser automation test' -> Tool trigger: browser_navigate
[2025-06-14 13:26:19,899] __main__ - INFO - Input: 'what tools are available' -> Tool trigger: None   
[2025-06-14 13:26:19,899] __main__ - INFO - Input: 'hello world' -> Tool trigger: None
[2025-06-14 13:26:19,900] __main__ - INFO - Agent tool integration test completed
[2025-06-14 13:26:19,900] __main__ - INFO - === Test Summary ===
[2025-06-14 13:26:19,922] __main__ - INFO - MCP Integration Test: PASS
[2025-06-14 13:26:19,928] __main__ - INFO - Agent Tool Integration Test: PASS
[2025-06-14 13:26:19,931] __main__ - INFO - Overall Result: PASS
(py312) PS C:\convo_bot> 


(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_tool_discovery.py
[2025-06-14 13:27:00,503] INFO - === Testing Tool Discovery ===
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
[2025-06-14 13:27:00,504] INFO - Loaded 2 servers from config
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
[2025-06-14 13:27:00,508] INFO - Platform detected: windows
[2025-06-14 13:27:00,509] INFO - Project root: c:\convo_bot
[2025-06-14 13:27:00,509] INFO - Base directory: c:\convo_bot
✅ Connected to azure-devops via URL
Connection attempt for azure-devops completed, result: True
✅ azure-devops added to connected servers
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 49792)
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
[2025-06-14 13:27:19,208] INFO - Connected to 2 MCP servers
[2025-06-14 13:27:19,212] INFO -   Connected: azure-devops (URL: http://127.0.0.1:8000)
[2025-06-14 13:27:19,233] INFO -   Connected: playwright (URL: http://localhost:3000)
[2025-06-14 13:27:19,234] INFO - Discovering server capabilities...
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
Error sending MCP request: HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded with url: /jsonrpc (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001F594108D40>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
  ❌ Failed to initialize playwright
  🔧 Discovering tools...
  📡 Sending JSON-RPC request to: http://localhost:3000/jsonrpc
  📤 Method: getTools
  ❌ Error sending MCP request: HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded with url: /jsonrpc (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001F594109340>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
    No tools found
✅ Connected to MCP server: playwright
   Tools: 0
[2025-06-14 13:27:27,462] INFO -   azure-devops: 0 tools
[2025-06-14 13:27:27,463] INFO -   playwright: 0 tools
[2025-06-14 13:27:27,463] INFO - Total tools discovered: 0
[2025-06-14 13:27:27,464] ERROR - ❌ Tool discovery FAILED - no tools found
Shutting down MCP server: playwright
  ✅ Server playwright terminated
[2025-06-14 13:27:27,584] INFO - Cleaned up servers

Test Result: FAIL
(py312) PS C:\convo_bot> 