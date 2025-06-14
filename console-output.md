(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_playwright_connection.py
[2025-06-14 12:25:01,009] INFO - === Testing Playwright MCP Connection ===
⏭️ Skipping disabled server: azure-devops
⏭️ Skipping disabled server: brave-search
✅ Loaded 1 MCP servers from config
[2025-06-14 12:25:01,012] INFO - Playwright server config: MCPServer(id='playwright', url=None, command='npx', process=None, enabled=True, environment={}, directory=None, server_args=['@playwright/mcp@latest'], tools={})
[2025-06-14 12:25:01,012] INFO - Attempting to connect to Playwright server...
🚀 Starting playwright via command: npx
[2025-06-14 12:25:01,014] INFO - Platform detected: windows
[2025-06-14 12:25:01,014] INFO - Project root: c:\convo_bot
[2025-06-14 12:25:01,015] INFO - Base directory: c:\convo_bot
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 13688)
  Waiting for Playwright MCP to start...
  No responsive URL found for Playwright, using default
✅ Found server URL: http://localhost:3000
⚠️ URL not responding yet, but process is running
✅ Started playwright via command (process running)
[2025-06-14 12:25:19,757] INFO - ✅ Successfully connected to Playwright!
[2025-06-14 12:25:19,773] INFO - Server URL: http://localhost:3000
[2025-06-14 12:25:19,773] INFO - Process PID: 13688
[2025-06-14 12:25:19,774] INFO - ✅ Playwright process is running
[2025-06-14 12:25:19,781] INFO - Cleaned up servers

Test Result: PASS
(py312) PS C:\convo_bot> c



(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_mcp_integration.py
[2025-06-14 12:30:18,426] __main__ - INFO - Starting MCP Integration Tests
[2025-06-14 12:30:18,426] __main__ - INFO - === Testing MCP Integration ===
[2025-06-14 12:30:18,427] __main__ - INFO - 1. Testing MCP server connection...
⏭️ Skipping disabled server: azure-devops
⏭️ Skipping disabled server: brave-search
✅ Loaded 1 MCP servers from config
[2025-06-14 12:30:18,427] __main__ - INFO - Loaded 1 servers from config
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
[2025-06-14 12:30:18,429] utils.platform_config - INFO - Platform detected: windows
[2025-06-14 12:30:18,429] utils.platform_config - INFO - Project root: c:\convo_bot
[2025-06-14 12:30:18,429] utils.platform_config - INFO - Base directory: c:\convo_bot
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 38468)
  Waiting for Playwright MCP to start...
⚠️ 1 servers still connecting, giving extra time...
⚠️ Connection to playwright still in progress, but continuing
[2025-06-14 12:30:25,509] __main__ - INFO - Connected to 0 MCP servers
[2025-06-14 12:30:25,510] __main__ - WARNING - No MCP servers connected. Check your configuration.
[2025-06-14 12:30:25,510] __main__ - INFO - Cleaned up MCP servers
[2025-06-14 12:30:25,511] __main__ - INFO - === Testing Agent Tool Integration ===
[2025-06-14 12:30:26,311] __main__ - INFO - Agent MCP enabled: True
[2025-06-14 12:30:26,312] __main__ - INFO - Agent MCP tools: ['browser_navigate', 'browser_screenshot', 'test_automation_tool']
[2025-06-14 12:30:26,312] __main__ - INFO -   browser_navigate: Navigate to a URL using browser automation
[2025-06-14 12:30:26,312] __main__ - INFO -   browser_screenshot: Take a screenshot of the current browser page      
[2025-06-14 12:30:26,313] __main__ - INFO -   test_automation_tool: Test tool for browser automation and testing     
[2025-06-14 12:30:26,313] __main__ - INFO - Input: 'open google.com' -> Tool trigger: browser_navigate
[2025-06-14 12:30:26,313] __main__ - INFO - Input: 'take a screenshot' -> Tool trigger: browser_screenshot
[2025-06-14 12:30:26,314] __main__ - INFO - Input: 'navigate to example.com' -> Tool trigger: browser_navigate       
[2025-06-14 12:30:26,314] __main__ - INFO - Input: 'browser automation test' -> Tool trigger: browser_navigate       
[2025-06-14 12:30:26,315] __main__ - INFO - Input: 'what tools are available' -> Tool trigger: None
[2025-06-14 12:30:26,315] __main__ - INFO - Input: 'hello world' -> Tool trigger: None
[2025-06-14 12:30:26,316] __main__ - INFO - Agent tool integration test completed
[2025-06-14 12:30:26,316] __main__ - INFO - === Test Summary ===
[2025-06-14 12:30:26,317] __main__ - INFO - MCP Integration Test: FAIL
[2025-06-14 12:30:26,317] __main__ - INFO - Agent Tool Integration Test: PASS
[2025-06-14 12:30:26,318] __main__ - INFO - Overall Result: FAIL
(py312) PS C:\convo_bot> 