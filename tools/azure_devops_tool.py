import base64
import json
import requests
import logging
import os

from .base_tool import BaseTool
from models.devops_work_item_formatter import DevOpsWorkItemFormatter
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from utils.azure_db_helper import AzureDevOpsDBHelper

import dotenv
dotenv.load_dotenv()

FUNCTION_BASE_URL = os.getenv("FUNCTION_BASE_URL")
FUNCTION_APP_KEY = os.getenv("FUNCTION_APP_KEY")
AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AzureDevOpsTool(BaseTool):
    def __init__(self):
        self._boards_cache = []
        self._formatted_boards_cache = ""
        self.model = GeminiModel(model_name="gemini-1.5-flash", api_key=os.getenv("GEMINI_KEY"))
        self.agent = Agent(self.model)
        self.db = AzureDevOpsDBHelper()

    def name(self):
        return "azure_devops"

    async def run(self, user_input: str) -> str:
        normalized = user_input.lower()
        logger.info(f"Azure DevOps Tool received input: {normalized}")
        if any(phrase in normalized for phrase in ["get boards", "get work items", "list boards", "my boards", "azure boards"]):
            return self._get_boards()
        elif "add task" in normalized:
            return self._add_task()
        elif "create tasks from board" in normalized or "analyze board" in normalized:
            return await self._create_tasks_from_board(user_input)
        elif "show board ids" in normalized:
            return self._list_board_ids()
        return "Azure DevOps: Command not recognized."

    def _get_boards(self):
        logger.info("Fetching Azure DevOps boards...")
        auth_str = f"user:{AZURE_DEVOPS_PAT}"
        headers = {
            "Authorization": f"Basic {base64.b64encode(auth_str.encode()).decode()}"
        }
        url = f"{FUNCTION_BASE_URL}api/GetMyBoards?code={FUNCTION_APP_KEY}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.info("Boards fetched successfully.")
        boards = response.json()
        self._boards_cache = boards.get("value", [])

        # Save full formatted boards
        self._formatted_boards_cache = self.save_work_items_to_file(self._boards_cache)

        # Filter in-progress work items for speech response
        in_progress_summary = self._summarize_in_progress_items(self._boards_cache)
        return in_progress_summary

    def _add_task(self, parent_id=9746, task_title="Task Title", task_description="Task Description"):
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

    async def _create_tasks_from_board(self, user_input):
        # Extract work item ID (simple digit extraction for now)
        logger.info(f"Creating tasks from board with user input: {user_input}")
        import re
        match = re.search(r"\b(\d{4,})\b", user_input)
        if not match:
            return "No work item ID found in your input."
        parent_id = int(match.group(1))

        # Find work item in cache
        work_item = next((item for item in self._boards_cache if item.get("id") == parent_id), None)
        if not work_item:
            return f"Work item with ID {parent_id} not found in cache. Please run 'get boards' first."

        # Get plain text version of the work item
        formatted = DevOpsWorkItemFormatter.format(work_item)

        # Prompt Gemini to generate tasks
        prompt = (
            "Given the following work item, generate a list of tasks with short titles and detailed descriptions.\n"
            f"Work Item:\n{formatted}\n\n"
            f"Additional User Context: {user_input}\n\n"
            "Return the tasks in this JSON list format: [\n"
            "  {\"title\": \"short task title\", \"description\": \"detailed description\" }, ...\n"
            "]"
        )
        logger.info(f"Prompting Gemini with: {prompt}")
        response = await self.agent.run(prompt)
        try:
            raw = response.data.strip()
            with open("temp_memory/last_llm_response.json", "w", encoding="utf-8") as f:
                f.write(raw)

            # Remove markdown code block if present
            if raw.startswith("```json"):
                raw = raw.removeprefix("```json").strip()
            if raw.endswith("```"):
                raw = raw.removesuffix("```").strip()

            # Remove "json" prefix if it exists
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()

            # Replace smart quotes if any
            raw = raw.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")

            # Log cleaned response for debugging
            logger.info(f"Cleaned LLM JSON response: {raw}")


            tasks = json.loads(raw)
            appended_output = []
            task_titles = []
            for task in tasks:
                logger.info(f"Processing task: {task}")
                title = task.get("title")
                description = task.get("description")
                self._add_task(parent_id=parent_id, task_title=title, task_description=description)
                task_titles.append(title)

                # Format and prepare for appending to file
                appended_output.append(
                    f"Task (Parent ID: {parent_id})\nTitle: {title}\nDescription: {description}\n{'-'*60}\n"
                )

            # Append to tasks file
            with open("temp_memory/work_items_tasks.txt", "a", encoding="utf-8") as file:
                file.write("\n▶ GENERATED TASKS:\n\n")
                file.writelines(appended_output)

            summary = ", ".join(task_titles)
            return f"Successfully added tasks to work item {parent_id}: {summary}"
        except Exception as e:
            return f"Failed to parse tasks from LLM response: {e}\nRaw Response: {response.data}"

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
