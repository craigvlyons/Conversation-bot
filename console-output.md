(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_with_production_server.py
[2025-06-14 13:44:21,988] INFO - === Testing Production MCP Server Compatibility ===
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
[2025-06-14 13:44:21,989] INFO - Loaded 2 servers from production config
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
[2025-06-14 13:44:21,993] INFO - Platform detected: windows
[2025-06-14 13:44:21,993] INFO - Project root: c:\convo_bot
[2025-06-14 13:44:21,994] INFO - Base directory: c:\convo_bot
✅ Connected to azure-devops via URL
Connection attempt for azure-devops completed, result: True
✅ azure-devops added to connected servers
Starting MCP server: npx.cmd @playwright/mcp@latest
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 51152)
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
[2025-06-14 13:44:40,886] INFO - Connected to 2 MCP servers
[2025-06-14 13:44:40,887] INFO -   Connected: azure-devops
[2025-06-14 13:44:40,887] INFO -     URL: http://127.0.0.1:8000/sse
[2025-06-14 13:44:40,888] INFO -     Process: External server
[2025-06-14 13:44:40,888] INFO -     💡 This appears to be an SSE-based MCP server
[2025-06-14 13:44:40,888] INFO -     💡 Tool discovery via SSE requires WebSocket or SSE client       
[2025-06-14 13:44:40,889] INFO -     💡 Your production server IS working - it's just using a different transport
[2025-06-14 13:44:43,926] INFO -     ⚠️ HTTP connection test: HTTPConnectionPool(host='127.0.0.1', porrt=8000): Read timed out.
[2025-06-14 13:44:43,930] INFO -   Connected: playwright
[2025-06-14 13:44:43,930] INFO -     URL: http://localhost:3000
[2025-06-14 13:44:43,930] INFO -     Process: 51152
[2025-06-14 13:44:43,930] INFO -
=== Testing Custom Server Approach ===
[2025-06-14 13:44:45,955] INFO - ✅ Port 8001 is available for test server
[2025-06-14 13:44:45,956] INFO - 💡 Run 'python azure_devops_server.py' in another terminal for full testing
[2025-06-14 13:44:45,957] INFO - 💡 That server will provide HTTP JSON-RPC endpoints for tool discovery
[2025-06-14 13:44:45,957] INFO -
=== Summary ===
[2025-06-14 13:44:45,957] INFO - ✅ Production server connection: WORKING
[2025-06-14 13:44:45,957] INFO - ✅ URL handling: FIXED (no more /sse/sse)
[2025-06-14 13:44:45,958] INFO - ✅ Server detection: WORKING
[2025-06-14 13:44:45,961] INFO -
[2025-06-14 13:44:45,961] INFO - 💡 Your production Azure DevOps server is working correctly!
[2025-06-14 13:44:45,962] INFO - 💡 It uses SSE transport (different from HTTP JSON-RPC)
[2025-06-14 13:44:45,963] INFO - 💡 For testing tool discovery, you can either:
[2025-06-14 13:44:45,963] INFO -    1. Temporarily stop your production server and run our test server
[2025-06-14 13:44:45,964] INFO -    2. Or implement SSE-based tool discovery (more complex)
Shutting down MCP server: playwright
  ✅ Server playwright terminated
[2025-06-14 13:44:46,081] INFO - Cleaned up test connections

Test Result: PASS

============================================================
RECOMMENDATION:
============================================================
1. Your production Azure DevOps server IS working correctly
2. It uses SSE transport (visible in your program logs)
3. For tool discovery testing, temporarily stop your production
   server and run: python azure_devops_server.py
4. Then run: python test_tool_discovery.py
5. You should see full tool discovery working!
============================================================
(py312) PS C:\convo_bot> 


(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_tool_discovery.py
[2025-06-14 13:48:13,304] INFO - === Testing Tool Discovery ===
✅ Loaded 2 MCP servers from config
[2025-06-14 13:48:13,305] INFO - Loaded 2 servers from test config
Connecting to MCP server: azure-devops-test
🚀 Starting azure-devops-test via command: python
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
[2025-06-14 13:48:13,307] INFO - Platform detected: windows
[2025-06-14 13:48:13,307] INFO - Project root: c:\convo_bot
[2025-06-14 13:48:13,307] INFO - Base directory: c:\convo_bot
Starting MCP server: python azure_devops_server.py
[2025-06-14 13:48:13,308] INFO - Platform detected: windows
[2025-06-14 13:48:13,308] INFO - Project root: c:\convo_bot
[2025-06-14 13:48:13,308] INFO - Base directory: c:\convo_bot
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
Starting MCP server: npx.cmd @playwright/mcp@latest
  ✅ Process started (PID: 23896)
  ✅ Process started (PID: 18908)
❌ Process failed to start or exited early for azure-devops-test
Connection attempt for azure-devops-test completed, result: False
  Waiting for Playwright MCP to start...
⚠️ 1 servers still connecting, giving extra time...
  No responsive URL found for Playwright, using default
✅ Found server URL: http://localhost:3000
⚠️ URL not responding yet, but process is running
✅ Started playwright via command (process running)
Connection attempt for playwright completed, result: True
✅ playwright added to connected servers
✅ playwright connected during extra time
📊 Final connection summary: 1/2 servers connected
  ✅ playwright
Moving on with 1 connected servers
[2025-06-14 13:48:32,207] INFO - Connected to 1 MCP servers
[2025-06-14 13:48:32,208] INFO -   Connected: playwright (URL: http://localhost:3000)
[2025-06-14 13:48:32,209] INFO - Discovering server capabilities...
🔍 Discovering capabilities for playwright...
Error sending MCP request: HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded with url: /jsonrpc (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x00000200E5F80650>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
  ❌ Failed to initialize playwright
  🔧 Discovering tools...
  📡 Sending JSON-RPC request to: http://localhost:3000/jsonrpc
  📤 Method: getTools
  ❌ Error sending MCP request: HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded with url: /jsonrpc (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x00000200E5F80E00>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
    No tools found
✅ Connected to MCP server: playwright
   Tools: 0
[2025-06-14 13:48:40,414] INFO -   playwright: 0 tools
[2025-06-14 13:48:40,414] INFO - Total tools discovered: 0
[2025-06-14 13:48:40,415] ERROR - ❌ Tool discovery FAILED - no tools found
Shutting down MCP server: playwright
  ✅ Server playwright terminated
[2025-06-14 13:48:40,535] INFO - Cleaned up servers

Test Result: FAIL
(py312) PS C:\convo_bot> 
