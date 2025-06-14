2025-06-14 12:56:42 - __main__ - INFO - Validating environment configuration...
2025-06-14 12:56:42 - core.azure_devops_api - INFO - Environment validation successful
2025-06-14 12:56:42 - __main__ - INFO - Environment configuration validated successfully
INFO:     Started server process [18864]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:52703 - "POST /sse HTTP/1.1" 405 Method Not Allowed
INFO:     127.0.0.1:52704 - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:52705 - "POST /messages/?session_id=fd55b5e20f4e43a786932d409b8ed5ce HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:52706 - "POST /messages/?session_id=fd55b5e20f4e43a786932d409b8ed5ce HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:52707 - "POST /messages/?session_id=fd55b5e20f4e43a786932d409b8ed5ce HTTP/1.1" 202 Accepted
2025-06-14 12:56:49 - mcp.server.lowlevel.server - INFO - Processing request of type ListToolsRequest
INFO:     127.0.0.1:52708 - "POST /messages/?session_id=fd55b5e20f4e43a786932d409b8ed5ce HTTP/1.1" 202 Accepted
2025-06-14 12:56:49 - mcp.server.lowlevel.server - INFO - Processing request of type ListPromptsRequest
INFO:     127.0.0.1:52724 - "GET /sse/sse HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:52858 - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:52908 - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:52927 - "GET /sse/capabilities HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:53109 - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:53123 - "GET /capabilities HTTP/1.1" 404 Not Found
that is the server devops logg.


(py312) PS C:\convo_bot> & c:/convo_bot/.venv/Scripts/python.exe c:/convo_bot/test_tool_discovery.py
[2025-06-14 13:12:58,986] INFO - === Testing Tool Discovery ===
⏭️ Skipping disabled server: brave-search
✅ Loaded 2 MCP servers from config
[2025-06-14 13:12:58,987] INFO - Loaded 2 servers from config
Connecting to MCP server: azure-devops
🌐 Trying URL connection for azure-devops: http://127.0.0.1:8000/sse/sse
Connecting to MCP server: playwright
🚀 Starting playwright via command: npx
[2025-06-14 13:12:58,991] INFO - Platform detected: windows
[2025-06-14 13:12:58,991] INFO - Project root: c:\convo_bot
[2025-06-14 13:12:58,991] INFO - Base directory: c:\convo_bot
✅ Connected to azure-devops via URL
Starting MCP server: npx.cmd @playwright/mcp@latest
Connection attempt for azure-devops completed, result: True
✅ azure-devops added to connected servers
C:\Python312\Lib\subprocess.py:1016: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stdout = io.open(c2pread, 'rb', bufsize)
C:\Python312\Lib\subprocess.py:1021: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
  self.stderr = io.open(errread, 'rb', bufsize)
  ✅ Process started (PID: 26960)
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
[2025-06-14 13:13:17,871] INFO - Connected to 2 MCP servers
[2025-06-14 13:13:17,872] INFO -   Connected: azure-devops (URL: http://127.0.0.1:8000/sse)
[2025-06-14 13:13:17,874] INFO -   Connected: playwright (URL: http://localhost:3000)
[2025-06-14 13:13:17,877] INFO - Discovering server capabilities...
❌ Failed to get capabilities for azure-devops: 404
❌ Error discovering capabilities for playwright: HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded with url: /capabilities (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000001F90DA8CB60>: Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))
[2025-06-14 13:13:21,982] INFO -   azure-devops: 0 tools
[2025-06-14 13:13:21,983] INFO -   playwright: 0 tools
[2025-06-14 13:13:21,983] INFO - Total tools discovered: 0
[2025-06-14 13:13:21,984] ERROR - ❌ Tool discovery FAILED - no tools found
Shutting down MCP server: playwright
  ✅ Server playwright terminated
[2025-06-14 13:13:22,092] INFO - Cleaned up servers

Test Result: FAIL
(py312) PS C:\convo_bot> 