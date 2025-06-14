(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_mcp_integration.py
[2025-06-14 12:36:26,493] __main__ - INFO - Starting MCP Integration Tests
[2025-06-14 12:36:26,493] __main__ - INFO - === Testing MCP Integration ===
[2025-06-14 12:36:26,494] __main__ - INFO - 1. Testing MCP server connection...
⏭️ Skipping disabled server: azure-devops
⏭️ Skipping disabled server: brave-search
✅ Loaded 1 MCP servers from config
[2025-06-14 12:36:26,496] __main__ - INFO - Loaded 1 servers from config
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
[2025-06-14 12:36:26,498] utils.platform_config - INFO - Platform detected: windows
[2025-06-14 12:36:26,498] utils.platform_config - INFO - Project root: c:\convo_bot
[2025-06-14 12:36:26,498] utils.platform_config - INFO - Base directory: c:\convo_bot
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 27100)
  Waiting for Playwright MCP to start...
⚠️ 1 servers still connecting, giving extra time...
⚠️ Connection to playwright still in progress after 8s
📊 Final connection summary: 0/1 servers connected
❌ No servers successfully connected
[2025-06-14 12:36:34,585] __main__ - INFO - Connected to 0 MCP servers
[2025-06-14 12:36:34,585] __main__ - WARNING - No MCP servers connected. Check your configuration.    
[2025-06-14 12:36:34,586] __main__ - INFO - Continuing with mock tools test anyway...
[2025-06-14 12:36:34,587] __main__ - INFO - 2. Testing tool discovery...
✅ Loaded MCP tools config from config/mcp_tools.json
✅ Saved MCP tools config to config/mcp_tools.json
[2025-06-14 12:36:34,592] __main__ - INFO - Discovered 0 tools
[2025-06-14 12:36:34,594] __main__ - INFO - Available tools: []
[2025-06-14 12:36:34,596] __main__ - WARNING - No tools discovered from MCP servers
[2025-06-14 12:36:34,597] __main__ - INFO - This is expected since no servers connected
[2025-06-14 12:36:34,630] __main__ - INFO - 3. Testing MCP agent creation...
[2025-06-14 12:36:34,639] __main__ - INFO - MCP agent has 0 tools
[2025-06-14 12:36:34,648] __main__ - INFO - 4. Testing integration setup...
[2025-06-14 12:36:34,654] __main__ - INFO - MCP integration configured
[2025-06-14 12:36:34,655] __main__ - INFO - 6. Testing agent registration...
[2025-06-14 12:36:34,656] __main__ - INFO - Agent registration successful
[2025-06-14 12:36:34,660] __main__ - INFO - === MCP Integration Test Completed ===
[2025-06-14 12:36:34,663] __main__ - INFO - ⚠️ Test PARTIAL: Server connection issues, but tool detecttion works
[2025-06-14 12:36:34,670] __main__ - INFO - Cleaned up MCP servers
[2025-06-14 12:36:34,670] __main__ - INFO - === Testing Agent Tool Integration ===
[2025-06-14 12:36:35,385] __main__ - INFO - Agent MCP enabled: True
[2025-06-14 12:36:35,385] __main__ - INFO - Agent MCP tools: ['browser_navigate', 'browser_screenshot', 'test_automation_tool']
[2025-06-14 12:36:35,386] __main__ - INFO -   browser_navigate: Navigate to a URL using browser automation
[2025-06-14 12:36:35,386] __main__ - INFO -   browser_screenshot: Take a screenshot of the current browser page
[2025-06-14 12:36:35,387] __main__ - INFO -   test_automation_tool: Test tool for browser automation and testing
[2025-06-14 12:36:35,387] __main__ - INFO - Input: 'open google.com' -> Tool trigger: browser_navigate
[2025-06-14 12:36:35,389] __main__ - INFO - Input: 'take a screenshot' -> Tool trigger: browser_screenshot
[2025-06-14 12:36:35,389] __main__ - INFO - Input: 'navigate to example.com' -> Tool trigger: browser_navigate
[2025-06-14 12:36:35,389] __main__ - INFO - Input: 'browser automation test' -> Tool trigger: browser_navigate
[2025-06-14 12:36:35,390] __main__ - INFO - Input: 'what tools are available' -> Tool trigger: None   
[2025-06-14 12:36:35,391] __main__ - INFO - Input: 'hello world' -> Tool trigger: None
[2025-06-14 12:36:35,391] __main__ - INFO - Agent tool integration test completed
[2025-06-14 12:36:35,393] __main__ - INFO - === Test Summary ===
[2025-06-14 12:36:35,394] __main__ - INFO - MCP Integration Test: PASS
[2025-06-14 12:36:35,394] __main__ - INFO - Agent Tool Integration Test: PASS
[2025-06-14 12:36:35,395] __main__ - INFO - Overall Result: PASS
(py312) PS C:\convo_bot> 


(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_playwright_connection.py
[2025-06-14 12:37:23,395] INFO - === Testing Playwright MCP Connection ===
⏭️ Skipping disabled server: azure-devops
⏭️ Skipping disabled server: brave-search
✅ Loaded 1 MCP servers from config
[2025-06-14 12:37:23,396] INFO - Playwright server config: MCPServer(id='playwright', url=None, command='npx', process=None, enabled=True, environment={}, directory=None, server_args=['@playwright/mcp@latest'], tools={})
[2025-06-14 12:37:23,396] INFO - Attempting to connect to Playwright server...
🚀 Starting playwright via command: npx
[2025-06-14 12:37:23,397] INFO - Platform detected: windows
[2025-06-14 12:37:23,397] INFO - Project root: c:\convo_bot
[2025-06-14 12:37:23,397] INFO - Base directory: c:\convo_bot
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 52048)
  Waiting for Playwright MCP to start...
  No responsive URL found for Playwright, using default
✅ Found server URL: http://localhost:3000
⚠️ URL not responding yet, but process is running
✅ Started playwright via command (process running)
[2025-06-14 12:37:42,090] INFO - ✅ Successfully connected to Playwright!
[2025-06-14 12:37:42,093] INFO - Server URL: http://localhost:3000
[2025-06-14 12:37:42,094] INFO - Process PID: 52048
[2025-06-14 12:37:42,095] INFO - ✅ Playwright process is running
[2025-06-14 12:37:42,127] INFO - Cleaned up servers

Test Result: PASS
(py312) PS C:\convo_bot> 