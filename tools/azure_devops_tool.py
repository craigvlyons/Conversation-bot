"""
Azure DevOps Tool for Convo Bot Agent
This module is intended for Azure DevOps integration, such as pipelines, builds, releases, or work item automation.
Add your Azure DevOps API client logic, helper functions, and utilities here.
"""

import requests
import base64
import json

def get_azure_boards(function_url: str, pat: str):
    """
    Calls the Azure Function App to get boards, using a Personal Access Token (PAT).
    Returns the parsed JSON result or raises an exception.
    """
    auth_str = f"user:{pat}"
    auth_bytes = auth_str.encode('utf-8')
    auth_header = base64.b64encode(auth_bytes).decode('utf-8')
    headers = {
        "Authorization": f"Basic {auth_header}"
    }
    response = requests.get(function_url, headers=headers)
    response.raise_for_status()
    return response.json()

def add_task_to_workitem(function_app_url, function_app_key, azure_devops_pat, parent_id, task_title, task_description):
    """
    Adds a task to a work item using the Azure Function App and Azure DevOps PAT.
    Returns the response JSON if successful, or raises an exception.
    """
    auth = base64.b64encode(f":{azure_devops_pat}".encode("utf-8")).decode("utf-8")
    headers = {
        "x-functions-key": function_app_key,
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }
    url = f"{function_app_url}/api/AddTaskToWorkItem"
    payload = {
        "parent_id": parent_id,
        "title": task_title,
        "description": task_description
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()

class AzureDevOpsTool:
    def name(self):
        return "azure_devops"

    async def run(self, action, **kwargs):
        if action == "get_boards":
            return get_azure_boards(kwargs["function_url"], kwargs["pat"])
        elif action == "add_task":
            return add_task_to_workitem(
                kwargs["function_app_url"],
                kwargs["function_app_key"],
                kwargs["azure_devops_pat"],
                kwargs["parent_id"],
                kwargs["task_title"],
                kwargs["task_description"]
            )
        else:
            raise ValueError(f"Unknown Azure DevOps action: {action}")

# Example usage (for testing only):
# result = get_azure_boards(AZURE_FUNCTION_URL, pat)
# print(result)

# Add more MCP-style Azure DevOps functions below as needed.


