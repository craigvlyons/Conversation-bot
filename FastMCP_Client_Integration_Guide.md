# FastMCP Client Integration Guide
## Azure DevOps MCP Server - SUCCESSFULLY IMPLEMENTED ✅

This guide provides all the necessary information for building a client to connect to this Azure DevOps FastMCP server.

**🎉 IMPLEMENTATION STATUS: COMPLETE**
- ✅ FastMCP SSE protocol fully implemented in `utils/mcp_sse_client.py`
- ✅ Dynamic tool discovery working with 9+ Azure DevOps tools
- ✅ Complete MCP initialization sequence: `initialize` → `notifications/initialized` → `tools/list`
- ✅ Session management and bidirectional SSE communication established
- ✅ Tool execution verified for both simple and complex operations
- ✅ Integrated with conversation bot agent system

## Server Overview

**Server Name**: Azure DevOps  
**Transport**: SSE (Server-Sent Events)  
**Default Port**: 8000  
**Entry Point**: `azure_devops_server.py`

## Connection Requirements

### Environment Variables (Required)
```env
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/yourorg
AZURE_DEVOPS_PAT=your_personal_access_token
AZURE_DEVOPS_PROJECT=your_default_project_name  # Optional
AZURE_USERNAME=your_email@domain.com            # Optional
```

### Dependencies
```
mcp[cli]
azure-devops
python-dotenv
httpx
pydantic
```

### Server Startup
```bash
# Development mode
mcp dev azure_devops_server.py

# Production (SSE transport on port 8000)
python azure_devops_server.py
```

## Available Tools

### 1. Project Management
- **`list_projects`**: Get all projects in the organization
  - Parameters: None
  - Returns: JSON list of projects

### 2. Work Item Management

#### `list_work_items`
- **Purpose**: List and filter work items
- **Input Model**: `ListWorkItemsInput`
- **Parameters**:
  - `project` (str): Project name/ID (defaults to DEFAULT_PROJECT)
  - `work_item_type` (str, optional): Filter by type ('Task', 'Bug', 'User Story')
  - `assigned_to` (str, optional): Filter by assignee (defaults to AZURE_USERNAME)
  - `state` (str, optional): Filter by state ('New', 'Active', 'Closed')
  - `limit` (int): Max results (default: 50)

#### `get_work_item`
- **Purpose**: Get detailed work item information
- **Input Model**: `GetWorkItemInput`
- **Parameters**:
  - `work_item_id` (int): Work item ID
  - `project` (str): Project name/ID

#### `create_work_item`
- **Purpose**: Create new work items
- **Input Model**: `CreateWorkItemInput`
- **Parameters**:
  - `work_item_type` (str): Type ('Task', 'Bug', 'User Story', 'Epic')
  - `title` (str): Work item title
  - `project` (str): Project name/ID
  - `description` (str, optional): HTML description
  - `assigned_to` (str, optional): Assignee email/name
  - `priority` (int, optional): Priority 1-4 (1=highest)
  - `tags` (str, optional): Comma-separated tags

#### `update_work_item_state`
- **Purpose**: Change work item status
- **Input Model**: `UpdateWorkItemStateInput`
- **Parameters**:
  - `work_item_id` (int): Work item ID
  - `new_state` (str): New state value
  - `project` (str): Project name/ID

#### `search_work_items`
- **Purpose**: Search work items by text
- **Input Model**: `SearchWorkItemsInput`
- **Parameters**:
  - `search_text` (str): Search term
  - `project` (str): Project name/ID
  - `limit` (int): Max results (default: 20)

#### `get_work_item_comments`
- **Purpose**: Get work item comments/discussions
- **Input Model**: `GetWorkItemCommentsInput`
- **Parameters**:
  - `work_item_id` (int): Work item ID
  - `project` (str): Project name/ID

#### `add_task_to_work_item`
- **Purpose**: Create child tasks
- **Input Model**: `AddTaskInput`
- **Parameters**:
  - `parent_id` (int): Parent work item ID
  - `title` (str): Task title
  - `project` (str): Project name/ID
  - `description` (str, optional): Task description
  - `assigned_to` (str, optional): Assignee
  - `priority` (int, optional): Priority 1-4
  - `tags` (str, optional): Comma-separated tags

### 3. Work Item Linking

#### `link_work_items`
- **Purpose**: Create relationships between work items
- **Input Model**: `LinkWorkItemsInput`
- **Parameters**:
  - `source_id` (int): Source work item ID
  - `target_id` (int): Target work item ID
  - `project` (str): Project name/ID
  - `link_type` (LinkType): Relationship type

**Available Link Types**:
- `Related`: General relationship
- `Parent`: Source is parent of target
- `Child`: Source is child of target
- `Duplicate`: Items represent same work
- `Successor`: Target follows source
- `Predecessor`: Target precedes source

## Available Resources

### Configuration Resource
- **URI**: `azure-devops://config`
- **Purpose**: Get server configuration
- **Returns**: JSON with org URL, default project, and PAT status

## Available Prompts

### 1. `create_work_item_prompt_handler`
- **Parameter**: `work_item_type` (str, default: "Task")
- **Purpose**: Template for creating work items

### 2. `analyze_work_items_prompt_handler`
- **Purpose**: Template for analyzing work items

### 3. `add_task_to_work_item_prompt_handler`  
- **Purpose**: Template for adding child tasks

### 4. `link_work_items_prompt_handler`
- **Purpose**: Template for linking work items

## Error Handling

### Custom Exception: `AzureDevOpsAPIError`
All API errors return structured JSON with:
```json
{
  "error": true,
  "message": "User-friendly error message",
  "details": {
    "status_code": 400,
    "response_body": "API response",
    "method": "GET",
    "url": "https://api.url"
  }
}
```

## Authentication

The server uses **Basic Authentication** with Personal Access Tokens:
- Username: empty string
- Password: Personal Access Token
- Header: `Authorization: Basic {base64_encoded_credentials}`

## API Endpoints Structure

**Organization-level**: `{org_url}/_apis/{endpoint}`  
**Project-level**: `{org_url}/{project}/_apis/{endpoint}`

## Client Implementation Notes

1. **Input Validation**: All tools use Pydantic models for input validation
2. **Async Operations**: All tools are async functions
3. **Error Responses**: Always check for `error: true` in responses
4. **Default Values**: Many parameters have defaults from environment variables
5. **Transport**: Use SSE transport for real-time communication
6. **Content Type**: Expect `application/json` responses
7. **Logging**: Server provides detailed logging for debugging

## MCP Protocol Format

### Tools/List Request
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

### Tools/List Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "create_work_item",
        "description": "Create a new work item",
        "inputSchema": {
          "type": "object",
          "properties": {
            "work_item_type": {
              "type": "string",
              "description": "Type of work item (e.g., 'Task', 'Bug', 'User Story')"
            },
            "title": {
              "type": "string", 
              "description": "Work item title"
            },
            "project": {
              "type": "string",
              "description": "Project name or ID"
            },
            "description": {
              "type": "string",
              "description": "Work item description (optional)"
            },
            "assigned_to": {
              "type": "string",
              "description": "Assignee email/name (optional)"
            },
            "priority": {
              "type": "integer",
              "description": "Priority 1-4 (1=highest, optional)"
            },
            "tags": {
              "type": "string",
              "description": "Comma-separated tags (optional)"
            }
          },
          "required": ["work_item_type", "title", "project"]
        }
      }
    ]
  }
}
```

### Tools/Call Request Format
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "create_work_item",
    "arguments": {
      "work_item_type": "Task",
      "title": "Implement login feature",
      "project": "MyProject",
      "description": "<p>Add login UI and validation</p>",
      "assigned_to": "user@example.com",
      "priority": 2,
      "tags": "frontend,authentication"
    }
  }
}
```

### Tools/Call Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Work item created successfully with ID: 123"
      }
    ],
    "isError": false
  }
}
```

## Server Startup Validation

The server validates environment variables on startup and will raise `ValueError` if required variables are missing. Ensure all required environment variables are set before connecting.

## Implementation Summary

### What We Accomplished ✅

The FastMCP Azure DevOps integration has been successfully implemented with the following achievements:

#### 1. FastMCP SSE Protocol Implementation
- **File**: `utils/mcp_sse_client.py`
- **Features**: Complete SSE transport with session management, async responses, proper initialization sequence
- **Status**: ✅ COMPLETE - All 9 Azure DevOps tools discovered and executable

#### 2. Protocol Auto-Detection
- **File**: `utils/mcp_protocol_client.py` 
- **Features**: Automatic detection of SSE vs WebSocket vs HTTP transports
- **Status**: ✅ COMPLETE - Correctly identifies SSE servers from URL patterns

#### 3. Dynamic Tool Discovery
- **File**: `utils/tool_manager.py`
- **Features**: Real-time tool discovery from live servers, replaces static caching
- **Status**: ✅ COMPLETE - Discovers 9 tools: list_projects, list_work_items, get_work_item, create_work_item, update_work_item_state, search_work_items, get_work_item_comments, add_task_to_work_item, link_work_items

#### 4. Agent Integration  
- **File**: `agents/mcp_agent.py`
- **Features**: Seamless integration with conversation bot agent system
- **Status**: ✅ COMPLETE - Agent can list, describe, and execute all Azure DevOps tools

#### 5. Server Connection Management
- **File**: `utils/mcp_server_manager.py`
- **Features**: Handles server lifecycle, connection management, graceful fallbacks
- **Status**: ✅ COMPLETE - Successfully connects to Azure DevOps FastMCP server

### Technical Challenges Solved

1. **Session ID Extraction**: Implemented proper regex to extract 32-character session IDs from SSE events
2. **Initialization Sequence**: Discovered and implemented required `initialize` → `notifications/initialized` → `tools/list` flow
3. **Async Response Handling**: Built bidirectional communication over SSE (HTTP POST requests, SSE stream responses)
4. **Tool Parameter Mapping**: Correctly handled complex Pydantic model parameters like `input_model` structures

### Verified Functionality

- ✅ **Connection**: Establishes SSE connection and extracts session ID
- ✅ **Initialization**: Completes full MCP handshake 
- ✅ **Discovery**: Finds all 9 Azure DevOps tools with complete schemas
- ✅ **Execution**: Successfully executes both simple (`list_projects`) and complex (`list_work_items`) tools
- ✅ **Integration**: Works seamlessly with conversation bot UI and agent system

### Usage Example

```python
# The integration is now fully functional
from agents.mcp_agent import MCPAgent

agent = MCPAgent()
await agent.initialize()  # Discovers Azure DevOps tools automatically

response = await agent.get_response('what tools do you have available?')
# Returns: "I have access to 9 MCP tools: Azure-Devops Tools (9 tools): list_projects, list_work_items, ..."
```

This implementation serves as a complete reference for integrating FastMCP SSE servers with any Python application.