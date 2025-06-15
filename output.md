ttributeError: 'Agent' object has no attribute 'function'

2025-06-15 10:20:33,446 - utils.mcp_agent_integration - ERROR - Failed to register MCP tool browser_tab_list: 'Agent' object has no attribute 'function'
2025-06-15 10:20:33,446 - utils.mcp_agent_integration - ERROR - Tool info: {'description': 'List browser tabs', 'schema': {'type': 'object', 'properties': {}, 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'server_id': 'playwright', 'metadata': {'name': 'browser_tab_list', 'description': 'List browser tabs', 'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'annotations': {'title': 'List tabs', 'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': True}, 'server': 'playwright'}}
2025-06-15 10:20:33,446 - utils.mcp_agent_integration - ERROR - Traceback (most recent call last):
  File "/Users/macc/Projects/python/Conversation-bot/utils/mcp_agent_integration.py", line 55, in register_mcp_tools_with_agent
    agent.function(wrapper_func)
    ^^^^^^^^^^^^^^
AttributeError: 'Agent' object has no attribute 'function'

2025-06-15 10:20:33,446 - utils.mcp_agent_integration - ERROR - Failed to register MCP tool browser_tab_new: 'Agent' object has no attribute 'function'
2025-06-15 10:20:33,446 - utils.mcp_agent_integration - ERROR - Tool info: {'description': 'Open a new tab', 'schema': {'type': 'object', 'properties': {'url': {'type': 'string', 'description': 'The URL to navigate to in the new tab. If not provided, the new tab will be blank.'}}, 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'server_id': 'playwright', 'metadata': {'name': 'browser_tab_new', 'description': 'Open a new tab', 'inputSchema': {'type': 'object', 'properties': {'url': {'type': 'string', 'description': 'The URL to navigate to in the new tab. If not provided, the new tab will be blank.'}}, 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'annotations': {'title': 'Open a new tab', 'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': True}, 'server': 'playwright'}}
2025-06-15 10:20:33,446 - utils.mcp_agent_integration - ERROR - Traceback (most recent call last):
  File "/Users/macc/Projects/python/Conversation-bot/utils/mcp_agent_integration.py", line 55, in register_mcp_tools_with_agent
    agent.function(wrapper_func)
    ^^^^^^^^^^^^^^
AttributeError: 'Agent' object has no attribute 'function'

2025-06-15 10:20:33,447 - utils.mcp_agent_integration - ERROR - Failed to register MCP tool browser_tab_select: 'Agent' object has no attribute 'function'
2025-06-15 10:20:33,447 - utils.mcp_agent_integration - ERROR - Tool info: {'description': 'Select a tab by index', 'schema': {'type': 'object', 'properties': {'index': {'type': 'number', 'description': 'The index of the tab to select'}}, 'required': ['index'], 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'server_id': 'playwright', 'metadata': {'name': 'browser_tab_select', 'description': 'Select a tab by index', 'inputSchema': {'type': 'object', 'properties': {'index': {'type': 'number', 'description': 'The index of the tab to select'}}, 'required': ['index'], 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'annotations': {'title': 'Select a tab', 'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': True}, 'server': 'playwright'}}
2025-06-15 10:20:33,447 - utils.mcp_agent_integration - ERROR - Traceback (most recent call last):
  File "/Users/macc/Projects/python/Conversation-bot/utils/mcp_agent_integration.py", line 55, in register_mcp_tools_with_agent
    agent.function(wrapper_func)
    ^^^^^^^^^^^^^^
AttributeError: 'Agent' object has no attribute 'function'

2025-06-15 10:20:33,447 - utils.mcp_agent_integration - ERROR - Failed to register MCP tool browser_tab_close: 'Agent' object has no attribute 'function'
2025-06-15 10:20:33,447 - utils.mcp_agent_integration - ERROR - Tool info: {'description': 'Close a tab', 'schema': {'type': 'object', 'properties': {'index': {'type': 'number', 'description': 'The index of the tab to close. Closes current tab if not provided.'}}, 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'server_id': 'playwright', 'metadata': {'name': 'browser_tab_close', 'description': 'Close a tab', 'inputSchema': {'type': 'object', 'properties': {'index': {'type': 'number', 'description': 'The index of the tab to close. Closes current tab if not provided.'}}, 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'annotations': {'title': 'Close a tab', 'readOnlyHint': False, 'destructiveHint': True, 'openWorldHint': True}, 'server': 'playwright'}}
2025-06-15 10:20:33,447 - utils.mcp_agent_integration - ERROR - Traceback (most recent call last):
  File "/Users/macc/Projects/python/Conversation-bot/utils/mcp_agent_integration.py", line 55, in register_mcp_tools_with_agent
    agent.function(wrapper_func)
    ^^^^^^^^^^^^^^
AttributeError: 'Agent' object has no attribute 'function'

2025-06-15 10:20:33,447 - utils.mcp_agent_integration - ERROR - Failed to register MCP tool browser_generate_playwright_test: 'Agent' object has no attribute 'function'
2025-06-15 10:20:33,447 - utils.mcp_agent_integration - ERROR - Tool info: {'description': 'Generate a Playwright test for given scenario', 'schema': {'type': 'object', 'properties': {'name': {'type': 'string', 'description': 'The name of the test'}, 'description': {'type': 'string', 'description': 'The description of the test'}, 'steps': {'type': 'array', 'items': {'type': 'string'}, 'description': 'The steps of the test'}}, 'required': ['name', 'description', 'steps'], 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'server_id': 'playwright', 'metadata': {'name': 'browser_generate_playwright_test', 'description': 'Generate a Playwright test for given scenario', 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string', 'description': 'The name of the test'}, 'description': {'type': 'string', 'description': 'The description of the test'}, 'steps': {'type': 'array', 'items': {'type': 'string'}, 'description': 'The steps of the test'}}, 'required': ['name', 'description', 'steps'], 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'annotations': {'title': 'Generate a Playwright test', 'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': True}, 'server': 'playwright'}}
2025-06-15 10:20:33,448 - utils.mcp_agent_integration - ERROR - Traceback (most recent call last):
  File "/Users/macc/Projects/python/Conversation-bot/utils/mcp_agent_integration.py", line 55, in register_mcp_tools_with_agent
    agent.function(wrapper_func)
    ^^^^^^^^^^^^^^
AttributeError: 'Agent' object has no attribute 'function'

2025-06-15 10:20:33,448 - utils.mcp_agent_integration - ERROR - Failed to register MCP tool browser_wait_for: 'Agent' object has no attribute 'function'
2025-06-15 10:20:33,448 - utils.mcp_agent_integration - ERROR - Tool info: {'description': 'Wait for text to appear or disappear or a specified time to pass', 'schema': {'type': 'object', 'properties': {'time': {'type': 'number', 'description': 'The time to wait in seconds'}, 'text': {'type': 'string', 'description': 'The text to wait for'}, 'textGone': {'type': 'string', 'description': 'The text to wait for to disappear'}}, 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'server_id': 'playwright', 'metadata': {'name': 'browser_wait_for', 'description': 'Wait for text to appear or disappear or a specified time to pass', 'inputSchema': {'type': 'object', 'properties': {'time': {'type': 'number', 'description': 'The time to wait in seconds'}, 'text': {'type': 'string', 'description': 'The text to wait for'}, 'textGone': {'type': 'string', 'description': 'The text to wait for to disappear'}}, 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}, 'annotations': {'title': 'Wait for', 'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': True}, 'server': 'playwright'}}
2025-06-15 10:20:33,448 - utils.mcp_agent_integration - ERROR - Traceback (most recent call last):
  File "/Users/macc/Projects/python/Conversation-bot/utils/mcp_agent_integration.py", line 55, in register_mcp_tools_with_agent
    agent.function(wrapper_func)
    ^^^^^^^^^^^^^^
AttributeError: 'Agent' object has no attribute 'function'

2025-06-15 10:20:33,448 - utils.mcp_agent_integration - ERROR - Failed to register MCP tool get_work_items: 'Agent' object has no attribute 'function'
2025-06-15 10:20:33,448 - utils.mcp_agent_integration - ERROR - Tool info: {'description': 'Get list of work items from Azure DevOps', 'schema': {'type': 'object', 'properties': {'project': {'type': 'string', 'description': 'Project name'}, 'status': {'type': 'string', 'description': 'Filter by status'}}}, 'server_id': 'azure-devops', 'metadata': {'name': 'get_work_items', 'description': 'Get list of work items from Azure DevOps', 'inputSchema': {'type': 'object', 'properties': {'project': {'type': 'string', 'description': 'Project name'}, 'status': {'type': 'string', 'description': 'Filter by status'}}}, 'server': 'azure-devops'}}
2025-06-15 10:20:33,449 - utils.mcp_agent_integration - ERROR - Traceback (most recent call last):
  File "/Users/macc/Projects/python/Conversation-bot/utils/mcp_agent_integration.py", line 55, in register_mcp_tools_with_agent
    agent.function(wrapper_func)
    ^^^^^^^^^^^^^^
AttributeError: 'Agent' object has no attribute 'function'

2025-06-15 10:20:33,449 - utils.mcp_agent_integration - ERROR - Failed to register MCP tool create_work_item: 'Agent' object has no attribute 'function'
2025-06-15 10:20:33,449 - utils.mcp_agent_integration - ERROR - Tool info: {'description': 'Create a new work item in Azure DevOps', 'schema': {'type': 'object', 'properties': {'title': {'type': 'string', 'description': 'Work item title'}, 'description': {'type': 'string', 'description': 'Work item description'}, 'type': {'type': 'string', 'description': 'Work item type'}}, 'required': ['title']}, 'server_id': 'azure-devops', 'metadata': {'name': 'create_work_item', 'description': 'Create a new work item in Azure DevOps', 'inputSchema': {'type': 'object', 'properties': {'title': {'type': 'string', 'description': 'Work item title'}, 'description': {'type': 'string', 'description': 'Work item description'}, 'type': {'type': 'string', 'description': 'Work item type'}}, 'required': ['title']}, 'server': 'azure-devops'}}
2025-06-15 10:20:33,449 - utils.mcp_agent_integration - ERROR - Traceback (most recent call last):
  File "/Users/macc/Projects/python/Conversation-bot/utils/mcp_agent_integration.py", line 55, in register_mcp_tools_with_agent
    agent.function(wrapper_func)
    ^^^^^^^^^^^^^^
AttributeError: 'Agent' object has no attribute 'function'

2025-06-15 10:20:33,449 - utils.mcp_agent_integration - ERROR - Failed to register MCP tool update_work_item: 'Agent' object has no attribute 'function'
2025-06-15 10:20:33,450 - utils.mcp_agent_integration - ERROR - Tool info: {'description': 'Update an existing work item', 'schema': {'type': 'object', 'properties': {'id': {'type': 'integer', 'description': 'Work item ID'}, 'status': {'type': 'string', 'description': 'New status'}, 'assignee': {'type': 'string', 'description': 'Assign to user'}}, 'required': ['id']}, 'server_id': 'azure-devops', 'metadata': {'name': 'update_work_item', 'description': 'Update an existing work item', 'inputSchema': {'type': 'object', 'properties': {'id': {'type': 'integer', 'description': 'Work item ID'}, 'status': {'type': 'string', 'description': 'New status'}, 'assignee': {'type': 'string', 'description': 'Assign to user'}}, 'required': ['id']}, 'server': 'azure-devops'}}
2025-06-15 10:20:33,450 - utils.mcp_agent_integration - ERROR - Traceback (most recent call last):
  File "/Users/macc/Projects/python/Conversation-bot/utils/mcp_agent_integration.py", line 55, in register_mcp_tools_with_agent
    agent.function(wrapper_func)
    ^^^^^^^^^^^^^^
AttributeError: 'Agent' object has no attribute 'function'

2025-06-15 10:20:33,450 - setup.initialize_agents - INFO - MCP tools registered with all agents
2025-06-15 10:20:33,450 - setup.initialize_agents - INFO - MCP setup completed in background thread