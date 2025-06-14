(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_mcp_integration.py
[2025-06-14 12:19:23,041] __main__ - INFO - Starting MCP Integration Tests
[2025-06-14 12:19:23,041] __main__ - INFO - === Testing MCP Integration ===
[2025-06-14 12:19:23,041] __main__ - INFO - 1. Testing MCP server connection...
⏭️ Skipping disabled server: azure-devops
⏭️ Skipping disabled server: brave-search
✅ Loaded 1 MCP servers from config
[2025-06-14 12:19:23,042] __main__ - INFO - Loaded 1 servers from config
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
[2025-06-14 12:19:23,044] utils.platform_config - INFO - Platform detected: windows
[2025-06-14 12:19:23,044] utils.platform_config - INFO - Project root: c:\convo_bot
[2025-06-14 12:19:23,044] utils.platform_config - INFO - Base directory: c:\convo_bot
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 39372)
⚠️ Connection to playwright timed out, but continuing
[2025-06-14 12:19:28,137] __main__ - INFO - Connected to 0 MCP servers
[2025-06-14 12:19:28,137] __main__ - WARNING - No MCP servers connected. Check your configuration.
[2025-06-14 12:19:28,138] __main__ - INFO - Cleaned up MCP servers
[2025-06-14 12:19:28,138] __main__ - INFO - === Testing Agent Tool Integration ===
[2025-06-14 12:19:28,866] __main__ - INFO - Agent MCP enabled: True
[2025-06-14 12:19:28,866] __main__ - INFO - Agent MCP tools: ['browser_navigate', 'browser_screenshot', 'test_automation_tool']
[2025-06-14 12:19:28,866] __main__ - INFO -   browser_navigate: Navigate to a URL using browser automation
[2025-06-14 12:19:28,867] __main__ - INFO -   browser_screenshot: Take a screenshot of the current browser page      
[2025-06-14 12:19:28,867] __main__ - INFO -   test_automation_tool: Test tool for browser automation and testing     
[2025-06-14 12:19:28,867] __main__ - INFO - Input: 'open google.com' -> Tool trigger: browser_navigate
[2025-06-14 12:19:28,867] __main__ - INFO - Input: 'take a screenshot' -> Tool trigger: browser_screenshot
[2025-06-14 12:19:28,868] __main__ - INFO - Input: 'navigate to example.com' -> Tool trigger: browser_navigate       
[2025-06-14 12:19:28,868] __main__ - INFO - Input: 'browser automation test' -> Tool trigger: browser_navigate       
[2025-06-14 12:19:28,868] __main__ - INFO - Input: 'what tools are available' -> Tool trigger: None
[2025-06-14 12:19:28,868] __main__ - INFO - Input: 'hello world' -> Tool trigger: None
[2025-06-14 12:19:28,869] __main__ - INFO - Agent tool integration test completed
[2025-06-14 12:19:28,869] __main__ - INFO - === Test Summary ===
[2025-06-14 12:19:28,869] __main__ - INFO - MCP Integration Test: FAIL
[2025-06-14 12:19:28,869] __main__ - INFO - Agent Tool Integration Test: PASS
[2025-06-14 12:19:28,869] __main__ - INFO - Overall Result: FAIL
(py312) PS C:\convo_bot> 