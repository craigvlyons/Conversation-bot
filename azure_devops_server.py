#!/usr/bin/env python3
"""
Simple Azure DevOps MCP Server for testing local MCP server connections.
This is a mock server that simulates Azure DevOps operations for testing purposes.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from aiohttp import web, web_request
from aiohttp.web_response import Response
import aiohttp_cors

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class AzureDevOpsMCPServer:
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()
        
        # Mock data for testing
        self.mock_work_items = [
            {
                "id": 1,
                "title": "Implement user authentication",
                "description": "Add OAuth2 authentication to the web application",
                "status": "Active",
                "created_at": "2025-06-14T10:00:00Z"
            },
            {
                "id": 2,
                "title": "Fix login bug",
                "description": "Users cannot log in with special characters in password",
                "status": "New",
                "created_at": "2025-06-14T11:30:00Z"
            },
            {
                "id": 3,
                "title": "Update documentation",
                "description": "Update API documentation for v2.0 release",
                "status": "Completed",
                "created_at": "2025-06-13T14:15:00Z"
            }
        ]
    
    def setup_cors(self):
        """Setup CORS for cross-origin requests"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def setup_routes(self):
        """Setup HTTP routes for the MCP server"""
        self.app.router.add_get('/', self.health_check)
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/sse', self.sse_endpoint)
        self.app.router.add_post('/jsonrpc', self.jsonrpc_handler)
        self.app.router.add_get('/capabilities', self.get_capabilities)
    
    async def health_check(self, request: web_request.Request) -> Response:
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "server": "Azure DevOps MCP Server",
            "timestamp": datetime.now().isoformat()
        })
    
    async def sse_endpoint(self, request: web_request.Request) -> Response:
        """Server-Sent Events endpoint for MCP communication"""
        return web.json_response({
            "message": "SSE endpoint ready",
            "server": "Azure DevOps MCP Server"
        })
    
    async def get_capabilities(self, request: web_request.Request) -> Response:
        """Get server capabilities including available tools"""
        capabilities = {
            "server": "Azure DevOps MCP Server",
            "version": "1.0.0",
            "tools": {
                "get_work_items": {
                    "description": "Get list of work items from Azure DevOps",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name"},
                            "status": {"type": "string", "description": "Filter by status"}
                        }
                    }
                },
                "create_work_item": {
                    "description": "Create a new work item in Azure DevOps",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Work item title"},
                            "description": {"type": "string", "description": "Work item description"},
                            "type": {"type": "string", "description": "Work item type (Bug, Task, etc.)"}
                        },
                        "required": ["title"]
                    }
                },
                "update_work_item": {
                    "description": "Update an existing work item",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Work item ID"},
                            "status": {"type": "string", "description": "New status"},
                            "assignee": {"type": "string", "description": "Assign to user"}
                        },
                        "required": ["id"]
                    }
                }
            }
        }
        return web.json_response(capabilities)
    
    async def jsonrpc_handler(self, request: web_request.Request) -> Response:
        """Handle JSON-RPC requests"""
        try:
            data = await request.json()
            method = data.get("method")
            params = data.get("params", {})
            request_id = data.get("id")
            
            logger.info(f"Received JSON-RPC request: {method}")
            
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "getTools":
                result = await self.handle_get_tools()
            elif method == "callTool":
                result = await self.handle_call_tool(params)
            else:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                })
            
            return web.json_response({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            })
            
        except Exception as e:
            logger.error(f"Error handling JSON-RPC request: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "id": data.get("id") if 'data' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            })
    
    async def handle_initialize(self, params: Dict) -> Dict:
        """Handle MCP initialization"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": "azure-devops-mcp",
                "version": "1.0.0"
            }
        }
    
    async def handle_get_tools(self) -> List[Dict]:
        """Return available tools"""
        return [
            {
                "name": "get_work_items",
                "description": "Get list of work items from Azure DevOps",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project": {"type": "string", "description": "Project name"},
                        "status": {"type": "string", "description": "Filter by status"}
                    }
                }
            },
            {
                "name": "create_work_item",
                "description": "Create a new work item in Azure DevOps",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Work item title"},
                        "description": {"type": "string", "description": "Work item description"},
                        "type": {"type": "string", "description": "Work item type"}
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "update_work_item",
                "description": "Update an existing work item",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Work item ID"},
                        "status": {"type": "string", "description": "New status"},
                        "assignee": {"type": "string", "description": "Assign to user"}
                    },
                    "required": ["id"]
                }
            }
        ]
    
    async def handle_call_tool(self, params: Dict) -> Dict:
        """Handle tool execution"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        if tool_name == "get_work_items":
            return await self.get_work_items(arguments)
        elif tool_name == "create_work_item":
            return await self.create_work_item(arguments)
        elif tool_name == "update_work_item":
            return await self.update_work_item(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def get_work_items(self, args: Dict) -> Dict:
        """Get work items (mock implementation)"""
        project = args.get("project", "default")
        status_filter = args.get("status")
        
        items = self.mock_work_items.copy()
        
        if status_filter:
            items = [item for item in items if item["status"].lower() == status_filter.lower()]
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Found {len(items)} work items in project '{project}':\n\n" + 
                           "\n".join([f"#{item['id']}: {item['title']} ({item['status']})" for item in items])
                }
            ]
        }
    
    async def create_work_item(self, args: Dict) -> Dict:
        """Create work item (mock implementation)"""
        title = args.get("title")
        description = args.get("description", "")
        work_item_type = args.get("type", "Task")
        
        new_id = max([item["id"] for item in self.mock_work_items]) + 1
        
        new_item = {
            "id": new_id,
            "title": title,
            "description": description,
            "status": "New",
            "type": work_item_type,
            "created_at": datetime.now().isoformat()
        }
        
        self.mock_work_items.append(new_item)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Created work item #{new_id}: {title}"
                }
            ]
        }
    
    async def update_work_item(self, args: Dict) -> Dict:
        """Update work item (mock implementation)"""
        item_id = args.get("id")
        new_status = args.get("status")
        assignee = args.get("assignee")
        
        # Find the work item
        item = next((item for item in self.mock_work_items if item["id"] == item_id), None)
        
        if not item:
            raise ValueError(f"Work item {item_id} not found")
        
        updates = []
        if new_status:
            item["status"] = new_status
            updates.append(f"status to {new_status}")
        
        if assignee:
            item["assignee"] = assignee
            updates.append(f"assignee to {assignee}")
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Updated work item #{item_id}: {', '.join(updates)}"
                }
            ]
        }

async def main():
    """Main function to start the server"""
    server = AzureDevOpsMCPServer()
    
    # Create and start the web server
    runner = web.AppRunner(server.app)
    await runner.setup()
    
    host = "127.0.0.1"
    port = 8000
    
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    logger.info(f"🚀 Azure DevOps MCP Server started at http://{host}:{port}")
    logger.info(f"📋 Available endpoints:")
    logger.info(f"   - Health: http://{host}:{port}/health")
    logger.info(f"   - SSE: http://{host}:{port}/sse")
    logger.info(f"   - JSON-RPC: http://{host}:{port}/jsonrpc")
    logger.info(f"   - Capabilities: http://{host}:{port}/capabilities")
    
    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    # Install required dependencies check
    try:
        import aiohttp
        import aiohttp_cors
    except ImportError as e:
        print(f"Missing required dependency: {e}")
        print("Please install with: pip install aiohttp aiohttp-cors")
        exit(1)
    
    asyncio.run(main())