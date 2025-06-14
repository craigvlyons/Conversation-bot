(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_mcp_integration.py
[2025-06-14 12:57:30,084] __main__ - INFO - Starting MCP Integration Tests
[2025-06-14 12:57:30,084] __main__ - INFO - === Testing MCP Integration ===
[2025-06-14 12:57:30,084] __main__ - INFO - 1. Testing MCP server connection...
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
[2025-06-14 12:57:30,085] __main__ - INFO - Loaded 2 servers from config
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
[2025-06-14 12:57:30,089] utils.platform_config - INFO - Platform detected: windows
[2025-06-14 12:57:30,089] utils.platform_config - INFO - Project root: c:\convo_bot
[2025-06-14 12:57:30,089] utils.platform_config - INFO - Base directory: c:\convo_bot
❌ URL connection failed for azure-devops
🚀 Starting azure-devops via command: python
Starting MCP server: python azure_devops_server.py
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
Starting MCP server: npx.cmd @playwright/mcp@latest
  ✅ Process started (PID: 28292)
  ✅ Process started (PID: 29824)
❌ Process failed to start or exited early for azure-devops
Connection attempt for azure-devops completed, result: False
  Waiting for Playwright MCP to start...
  No responsive URL found for Playwright, using default
✅ Found server URL: http://localhost:3000
⚠️ URL not responding yet, but process is running
✅ Started playwright via command (process running)
Connection attempt for playwright completed, result: True
✅ playwright added to connected servers
📊 Final connection summary: 1/2 servers connected
  ✅ playwright
Moving on with 1 connected servers
[2025-06-14 12:57:48,945] __main__ - INFO - Connected to 1 MCP servers
[2025-06-14 12:57:48,946] __main__ - INFO -   Connected: playwright (URL: http://localhost:3000, Process: 29824)
[2025-06-14 12:57:48,947] __main__ - INFO - 2. Testing tool discovery...
✅ Loaded MCP tools config from config/mcp_tools.json
✅ Saved MCP tools config to config/mcp_tools.json
[2025-06-14 12:57:48,964] __main__ - INFO - Discovered 0 tools
[2025-06-14 12:57:48,971] __main__ - INFO - Available tools: []
[2025-06-14 12:57:48,973] __main__ - WARNING - No tools discovered from MCP servers
[2025-06-14 12:57:48,973] __main__ - WARNING - This is unexpected since servers did connect
[2025-06-14 12:57:48,973] __main__ - INFO - 3. Testing MCP agent creation...
[2025-06-14 12:57:48,979] __main__ - INFO - MCP agent has 0 tools
[2025-06-14 12:57:48,980] __main__ - INFO - 4. Testing integration setup...
[2025-06-14 12:57:48,981] __main__ - INFO - MCP integration configured
[2025-06-14 12:57:48,982] __main__ - INFO - 6. Testing agent registration...
[2025-06-14 12:57:48,982] __main__ - INFO - Agent registration successful
[2025-06-14 12:57:48,984] __main__ - INFO - === MCP Integration Test Completed ===
[2025-06-14 12:57:48,984] __main__ - INFO - ✅ Test PASSED: Servers connected successfully
Shutting down MCP server: playwright
  ✅ Server playwright terminated
[2025-06-14 12:57:49,100] __main__ - INFO - Cleaned up MCP servers
[2025-06-14 12:57:49,102] __main__ - INFO - === Testing Agent Tool Integration ===
[2025-06-14 12:57:49,760] __main__ - INFO - Agent MCP enabled: True
[2025-06-14 12:57:49,762] __main__ - INFO - Agent MCP tools: ['browser_navigate', 'browser_screenshot', 'test_automation_tool']
[2025-06-14 12:57:49,762] __main__ - INFO -   browser_navigate: Navigate to a URL using browser automation
[2025-06-14 12:57:49,763] __main__ - INFO -   browser_screenshot: Take a screenshot of the current browser page
[2025-06-14 12:57:49,763] __main__ - INFO -   test_automation_tool: Test tool for browser automation and testing
[2025-06-14 12:57:49,764] __main__ - INFO - Input: 'open google.com' -> Tool trigger: browser_navigate
[2025-06-14 12:57:49,764] __main__ - INFO - Input: 'take a screenshot' -> Tool trigger: browser_screenshot
[2025-06-14 12:57:49,765] __main__ - INFO - Input: 'navigate to example.com' -> Tool trigger: browser_navigate
[2025-06-14 12:57:49,768] __main__ - INFO - Input: 'browser automation test' -> Tool trigger: browser_navigate
[2025-06-14 12:57:49,771] __main__ - INFO - Input: 'what tools are available' -> Tool trigger: None   
[2025-06-14 12:57:49,772] __main__ - INFO - Input: 'hello world' -> Tool trigger: None
[2025-06-14 12:57:49,807] __main__ - INFO - Agent tool integration test completed
[2025-06-14 12:57:49,813] __main__ - INFO - === Test Summary ===
[2025-06-14 12:57:49,814] __main__ - INFO - MCP Integration Test: PASS
[2025-06-14 12:57:49,814] __main__ - INFO - Agent Tool Integration Test: PASS
[2025-06-14 12:57:49,814] __main__ - INFO - Overall Result: PASS
(py312) PS C:\convo_bot> 