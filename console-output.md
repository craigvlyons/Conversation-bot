(.venv) (py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_mcp_integration.py
[2025-06-14 12:10:37,728] __main__ - INFO - Starting MCP Integration Tests
[2025-06-14 12:10:37,728] __main__ - INFO - === Testing MCP Integration ===
[2025-06-14 12:10:37,729] __main__ - INFO - 1. Testing MCP server connection...
⏭️ Skipping disabled server: azure-devops
⏭️ Skipping disabled server: brave-search
✅ Loaded 1 MCP servers from config
[2025-06-14 12:10:37,739] __main__ - INFO - Loaded 1 servers from config
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
[2025-06-14 12:10:37,742] utils.platform_config - INFO - Platform detected: windows
[2025-06-14 12:10:37,744] utils.platform_config - INFO - Project root: c:\convo_bot
[2025-06-14 12:10:37,744] utils.platform_config - INFO - Base directory: c:\convo_bot
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 20940)
  Using default URL for Playwright MCP: http://localhost:3000
[2025-06-14 12:10:42,777] __main__ - WARNING - No MCP servers connected. Check your configuration.
[2025-06-14 12:10:42,778] __main__ - INFO - Cleaned up MCP servers
[2025-06-14 12:10:42,778] __main__ - INFO - === Testing Agent Tool Integration ===
[2025-06-14 12:10:43,476] __main__ - INFO - Input: 'open google.com' -> Tool trigger: None
[2025-06-14 12:10:43,477] __main__ - INFO - Input: 'take a screenshot' -> Tool trigger: None
[2025-06-14 12:10:43,477] __main__ - INFO - Input: 'navigate to example.com' -> Tool trigger: None
[2025-06-14 12:10:43,477] __main__ - INFO - Input: 'what tools are available' -> Tool trigger: None
[2025-06-14 12:10:43,478] __main__ - INFO - Input: 'hello world' -> Tool trigger: None
[2025-06-14 12:10:43,478] __main__ - INFO - Agent tool integration test completed
[2025-06-14 12:10:43,479] __main__ - INFO - === Test Summary ===
[2025-06-14 12:10:43,479] __main__ - INFO - MCP Integration Test: FAIL
[2025-06-14 12:10:43,479] __main__ - INFO - Agent Tool Integration Test: PASS
[2025-06-14 12:10:43,479] __main__ - INFO - Overall Result: FAIL
(.venv) (py312) PS C:\convo_bot>