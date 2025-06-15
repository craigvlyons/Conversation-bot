"""
Azure DevOps MCP Server

This server provides tools to interact with Azure DevOps boards, allowing you to:
- List projects in your organization
- List work items with filtering options (type, assignee, state)
- Get detailed work item information
- Create new work items (Tasks, Bugs, User Stories, etc.)
- Update work item status
- Search work items by text
- Get work item comments and discussions
- Add child tasks to existing work items
- Link work items together (Parent/Child, Related, etc.)
- Access server configuration information
- Use specialized prompts for common operations

Requirements:
- pip install "mcp[cli]" azure-devops python-dotenv

Setup:
1. Create a Personal Access Token (PAT) in Azure DevOps
2. Set environment variables:
   - AZURE_DEVOPS_ORG_URL: Your organization URL (e.g., https://dev.azure.com/yourorg)
   - AZURE_DEVOPS_PAT: Your Personal Access Token
   - AZURE_DEVOPS_PROJECT: Your project name (optional, can be specified per call)
   - AZURE_USERNAME: Your Azure DevOps username or email. (optional, can be specified per call)
3. These variables can be set in a .env file in the same directory

Usage:
mcp dev azure_devops_server.py

Available Tools:
- list_projects: Get all projects in your organization
- list_work_items: List and filter work items by type, assignee, state
- get_work_item: Get detailed info for a specific work item
- create_work_item: Create tasks, bugs, user stories, etc.
- update_work_item_state: Change work item status
- search_work_items: Find work items by text
- get_work_item_comments: Get comments on a work item
- add_task_to_work_item: Create child tasks
- link_work_items: Create relationships between items
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Import from modules
from core.azure_devops_api import AZURE_DEVOPS_ORG_URL, AZURE_DEVOPS_PAT, DEFAULT_PROJECT, AZURE_USERNAME, validate_env
from core.models import (
    AddTaskInput,
    CreateWorkItemInput,
    UpdateWorkItemStateInput,
    SearchWorkItemsInput,
    LinkWorkItemsInput,
    LinkType,
    GetWorkItemInput,
    GetWorkItemCommentsInput,
    ListWorkItemsInput
)
from core.logging_config import configure_logging, get_logger
from core.exceptions import AzureDevOpsAPIError

# Initialize logger for this module
logger = get_logger(__name__)

# Import tools from modules
from tools import projects, work_items, links

# Import prompts from the prompts module
from prompts import create_work_item_prompt, analyze_work_items_prompt, add_task_to_work_item_prompt, link_work_items_prompt

# Load environment variables from .env file
load_dotenv()

# Configure logging
configure_logging()

# Initialize FastMCP server
mcp = FastMCP("Azure DevOps")

# Validate environment configuration
logger.info("Validating environment configuration...")
validation_result = validate_env()
if not validation_result["valid"]:
    logger.error(f"Environment validation failed: {validation_result['message']}")
    raise ValueError(validation_result["message"])
logger.info("Environment configuration validated successfully")

# Register tools from projects module
@mcp.tool()
async def list_projects() -> str:
    """List all projects in the Azure DevOps organization"""
    try:
        return await projects.list_projects()
    except AzureDevOpsAPIError as e:
        # Return a user-friendly error response
        logger.error(f"Azure DevOps API error in list_projects tool: {e}")
        return json.dumps({
            "error": True,
            "message": "Failed to retrieve projects from Azure DevOps.",
            "details": e.to_dict()
        }, indent=2)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in list_projects tool: {str(e)}")
        return json.dumps({
            "error": True,
            "message": "An unexpected error occurred while retrieving projects.",
            "details": str(e)
        }, indent=2)

# Register tools from work_items module
@mcp.tool()
async def list_work_items(input_model: ListWorkItemsInput) -> str:
    """
    List work items in a project with optional filters
    
    Args:
        input_model: ListWorkItemsInput model with the following fields:
            project: Project name or ID (defaults to configured DEFAULT_PROJECT)
            work_item_type: Filter by work item type (e.g., 'Task', 'Bug', 'User Story')
            assigned_to: Filter by assigned user (display name or email)
            state: Filter by state (e.g., 'New item', 'Approved', 'In Progress', 'In Review', 'Closed', 'Done')
            limit: Maximum number of items to return (default 50)
    """
    try:
        return await work_items.list_work_items(input_model)
    except AzureDevOpsAPIError as e:
        # Return a user-friendly error response
        logger.error(f"Azure DevOps API error in list_work_items tool: {e}")
        return json.dumps({
            "error": True,
            "message": f"Failed to retrieve work items from project '{input_model.project}'.",
            "details": e.to_dict()
        }, indent=2)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in list_work_items tool: {str(e)}")
        return json.dumps({
            "error": True,
            "message": f"An unexpected error occurred while retrieving work items from project '{input_model.project}'.",
            "details": str(e)
        }, indent=2)

@mcp.tool()
async def get_work_item(input_model: GetWorkItemInput) -> str:
    """
    Get detailed information about a specific work item
    
    Args:
        input_model: GetWorkItemInput model with the following fields:
            work_item_id: ID of the work item to retrieve
            project: Project name or ID (defaults to configured DEFAULT_PROJECT)
    """
    try:
        return await work_items.get_work_item(input_model)
    except AzureDevOpsAPIError as e:
        # Return a user-friendly error response
        logger.error(f"Azure DevOps API error in get_work_item tool: {e}")
        return json.dumps({
            "error": True,
            "message": f"Failed to retrieve work item #{input_model.work_item_id} from project '{input_model.project}'.",
            "details": e.to_dict()
        }, indent=2)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in get_work_item tool: {str(e)}")
        return json.dumps({
            "error": True,
            "message": f"An unexpected error occurred while retrieving work item #{input_model.work_item_id}.",
            "details": str(e)
        }, indent=2)

@mcp.tool()
async def create_work_item(input_model: CreateWorkItemInput) -> str:
    """
    Create a new work item
    
    Args:
        input_model: CreateWorkItemInput model with the following fields:
            work_item_type: Type of work item (e.g., 'Task', 'Bug', 'User Story')
            title: Work item title
            project: Project name or ID (defaults to configured DEFAULT_PROJECT)
            description: Work item description (optional)
            assigned_to: User to assign the work item to (defaults to current user)
            priority: Priority level (1-4, where 1 is highest)
            tags: Comma-separated tags
    """
    try:
        return await work_items.create_work_item(input_model)
    except AzureDevOpsAPIError as e:
        # Return a user-friendly error response
        logger.error(f"Azure DevOps API error in create_work_item tool: {e}")
        return json.dumps({
            "error": True,
            "message": f"Failed to create {input_model.work_item_type} in project '{input_model.project}'.",
            "details": e.to_dict()
        }, indent=2)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in create_work_item tool: {str(e)}")
        return json.dumps({
            "error": True,
            "message": f"An unexpected error occurred while creating {input_model.work_item_type} in project '{input_model.project}'.",
            "details": str(e)
        }, indent=2)

@mcp.tool()
async def update_work_item_state(input_model: UpdateWorkItemStateInput) -> str:
    """
    Update the state of a work item
    
    Args:
        input_model: UpdateWorkItemStateInput model with the following fields:
            work_item_id: ID of the work item to update
            new_state: New state value (e.g., 'New', 'Active', 'Resolved', 'Closed')
            project: Project name or ID (defaults to configured DEFAULT_PROJECT)
    """
    try:
        return await work_items.update_work_item_state(input_model)
    except AzureDevOpsAPIError as e:
        # Return a user-friendly error response
        logger.error(f"Azure DevOps API error in update_work_item_state tool: {e}")
        return json.dumps({
            "error": True,
            "message": f"Failed to update work item #{input_model.work_item_id} state to '{input_model.new_state}'.",
            "details": e.to_dict()
        }, indent=2)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in update_work_item_state tool: {str(e)}")
        return json.dumps({
            "error": True,
            "message": f"An unexpected error occurred while updating work item #{input_model.work_item_id} state.",
            "details": str(e)
        }, indent=2)

@mcp.tool()
async def search_work_items(input_model: SearchWorkItemsInput) -> str:
    """
    Search for work items containing specific text
    
    Args:
        input_model: SearchWorkItemsInput model with the following fields:
            search_text: Text to search for in title and description
            project: Project name or ID (defaults to configured DEFAULT_PROJECT)
            limit: Maximum number of results to return
    """
    try:
        return await work_items.search_work_items(input_model)
    except AzureDevOpsAPIError as e:
        # Return a user-friendly error response
        logger.error(f"Azure DevOps API error in search_work_items tool: {e}")
        return json.dumps({
            "error": True,
            "message": f"Failed to search for work items in project '{input_model.project}'.",
            "details": e.to_dict()
        }, indent=2)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in search_work_items tool: {str(e)}")
        return json.dumps({
            "error": True,
            "message": f"An unexpected error occurred while searching for work items in project '{input_model.project}'.",
            "details": str(e)
        }, indent=2)

@mcp.tool()
async def get_work_item_comments(input_model: GetWorkItemCommentsInput) -> str:
    """
    Get comments/discussion for a work item
    
    Args:
        input_model: GetWorkItemCommentsInput model with the following fields:
            work_item_id: ID of the work item to retrieve comments for
            project: Project name or ID (defaults to configured DEFAULT_PROJECT)
    """
    try:
        return await work_items.get_work_item_comments(input_model)
    except AzureDevOpsAPIError as e:
        # Return a user-friendly error response
        logger.error(f"Azure DevOps API error in get_work_item_comments tool: {e}")
        return json.dumps({
            "error": True,
            "message": f"Failed to retrieve comments for work item #{input_model.work_item_id}.",
            "details": e.to_dict()
        }, indent=2)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in get_work_item_comments tool: {str(e)}")
        return json.dumps({
            "error": True,
            "message": f"An unexpected error occurred while retrieving comments for work item #{input_model.work_item_id}.",
            "details": str(e)
        }, indent=2)

@mcp.tool()
async def add_task_to_work_item(input_model: AddTaskInput) -> Dict[str, Any]:
    """
    Creates a child task under a parent Azure DevOps work item.

    Args:
        input_model: AddTaskInput model with the following fields:
            parent_id: ID of parent work item
            title: Task title
            description: Task description (optional)
            assigned_to: User to assign the task to (email or display name)
            priority: Priority level (1-4, where 1 is highest)
            tags: Comma-separated tags
            project: Project name or ID (defaults to configured DEFAULT_PROJECT)
    """
    try:
        return await work_items.add_task_to_work_item(input_model)
    except AzureDevOpsAPIError as e:
        # Return a user-friendly error response
        logger.error(f"Azure DevOps API error in add_task_to_work_item tool: {e}")
        return {
            "error": True,
            "message": f"Failed to add task to work item #{input_model.parent_id}.",
            "details": e.to_dict()
        }
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in add_task_to_work_item tool: {str(e)}")
        return {
            "error": True,
            "message": f"An unexpected error occurred while adding task to work item #{input_model.parent_id}.",
            "details": str(e)
        }

# Register tools from links module
@mcp.tool()
async def link_work_items(input_model: LinkWorkItemsInput) -> str:
    """
    Create a link between two work items
    
    Args:
        input_model: LinkWorkItemsInput model with the following fields:
            source_id: ID of the source work item
            target_id: ID of the target work item
            link_type: Type of link (Related, Parent, Child, Duplicate, Successor, or Predecessor)
            project: Project name or ID (defaults to configured DEFAULT_PROJECT)
    """
    try:
        return await links.link_work_items(input_model)
    except AzureDevOpsAPIError as e:
        # Return a user-friendly error response
        logger.error(f"Azure DevOps API error in link_work_items tool: {e}")
        return json.dumps({
            "error": True,
            "message": f"Failed to link work item #{input_model.source_id} to #{input_model.target_id} with link type '{input_model.link_type}'.",
            "details": e.to_dict()
        }, indent=2)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in link_work_items tool: {str(e)}")
        return json.dumps({
            "error": True,
            "message": f"An unexpected error occurred while linking work items #{input_model.source_id} and #{input_model.target_id}.",
            "details": str(e)
        }, indent=2)

# Resource to get project configuration
@mcp.resource("azure-devops://config")
def get_config() -> str:
    """Get Azure DevOps server configuration"""
    config = {
        "organization_url": AZURE_DEVOPS_ORG_URL,
        "default_project": DEFAULT_PROJECT or "Not set",
        "pat_configured": bool(AZURE_DEVOPS_PAT),
    }
    return json.dumps(config, indent=2)

# Register prompt functions from prompts module
@mcp.prompt()
def create_work_item_prompt_handler(work_item_type: str = "Task") -> str:
    """Handler for create work item prompt"""
    return create_work_item_prompt(work_item_type)

@mcp.prompt()
def analyze_work_items_prompt_handler() -> str:
    """Handler for analyze work items prompt"""
    return analyze_work_items_prompt()

@mcp.prompt()
def add_task_to_work_item_prompt_handler() -> str:
    """Handler for add task to work item prompt"""
    return add_task_to_work_item_prompt()

@mcp.prompt()
def link_work_items_prompt_handler() -> str:
    """Handler for link work items prompt"""
    return link_work_items_prompt()

if __name__ == "__main__":
    # Run the MCP server with SSE transport on port 8000
    asyncio.run(mcp.run(transport="sse"))