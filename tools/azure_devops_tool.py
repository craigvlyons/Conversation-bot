import base64
import json
import requests
from .base_tool import BaseTool
import os
from models.devops_work_item_formatter import DevOpsWorkItemFormatter

FUNCTION_BASE_URL = os.getenv("FUNCTION_BASE_URL")
FUNCTION_APP_KEY = os.getenv("FUNCTION_APP_KEY")
AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")

class AzureDevOpsTool(BaseTool):
    def __init__(self):
        self._boards_cache = []
        self._formatted_boards_cache = ""

    def name(self):
        return "azure_devops"

    async def run(self, user_input: str) -> str:
        normalized = user_input.lower()

        if any(phrase in normalized for phrase in ["get boards", "get work items", "list boards", "my boards", "azure boards"]):
            return self._get_boards()
        elif "add task" in normalized:
            return self._add_task()
        elif "show board ids" in normalized:
            return self._list_board_ids()
        return "Azure DevOps: Command not recognized."

    def _get_boards(self):
        auth_str = f"user:{AZURE_DEVOPS_PAT}"
        headers = {
            "Authorization": f"Basic {base64.b64encode(auth_str.encode()).decode()}"
        }
        url = f"{FUNCTION_BASE_URL}api/GetMyBoards?code={FUNCTION_APP_KEY}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        boards = response.json()
        self._boards_cache = boards.get("value", [])

        # Save full formatted boards
        self._formatted_boards_cache = self.save_work_items_to_file(self._boards_cache)

        # Filter in-progress work items for speech response
        in_progress_summary = self._summarize_in_progress_items(self._boards_cache)
        return in_progress_summary

    def _add_task(self):
        parent_id = 9746
        task_title = "Task Title"
        task_description = "Task Description"
        auth = base64.b64encode(f":{AZURE_DEVOPS_PAT}".encode()).decode()
        headers = {
            "x-functions-key": FUNCTION_APP_KEY,
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        url = f"{FUNCTION_BASE_URL}/api/AddTaskToWorkItem"
        payload = {
            "parent_id": parent_id,
            "title": task_title,
            "description": task_description
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)

    def _list_board_ids(self):
        if not self._boards_cache:
            return "No boards cached. Please run 'get boards' first."

        lines = []
        for board in self._boards_cache:
            name = board.get("name", "Unknown")
            id_ = board.get("id", "No ID")
            lines.append(f"{name}: {id_}")
        return "\n".join(lines)

    def save_work_items_to_file(self, work_items):
        top_level_items = []
        task_items = []

        for item in work_items:
            work_item_type = item.get("fields", {}).get("System.WorkItemType", "")
            if work_item_type.lower() == "task":
                task_items.append(item)
            else:
                top_level_items.append(item)

        formatted_output = []

        with open("temp_memory/work_items.txt", "w", encoding="utf-8") as file:
            file.write("▶ TOP-LEVEL WORK ITEMS:\n\n")
            for item in top_level_items:
                formatted = DevOpsWorkItemFormatter.format(item)
                file.write(formatted + "\n")
                formatted_output.append(formatted)

        with open("temp_memory/work_items_tasks.txt", "w", encoding="utf-8") as file:
            file.write("▶ TASKS:\n\n")
            for item in task_items:
                formatted = DevOpsWorkItemFormatter.format(item)
                file.write(formatted + "\n")
                formatted_output.append(formatted)

        return "\n".join(formatted_output)

    def _summarize_in_progress_items(self, work_items):
        summaries = []
        for item in work_items:
            fields = item.get("fields", {})
            state = fields.get("System.State", "").lower()
            if state == "in progress":
                title = fields.get("System.Title", "No Title")
                id_ = item.get("id", "Unknown ID")
                summaries.append(f"{title} (ID: {id_})")

        if not summaries:
            return "No in-progress work items found."
        return "In-progress work items:\n" + "\n".join(summaries)
