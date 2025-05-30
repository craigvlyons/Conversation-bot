import base64
import json
import requests
import logging
import os
import hashlib
from .base_tool import BaseTool
from models.devops_models import WorkItem, DevOpsTask
from agents.registry import AgentRegistry
from pydantic_ai.models.gemini import GeminiModel
from utils.azure_db_helper import AzureDevOpsDBHelper
from models.devops_work_item_formatter import DevOpsWorkItemFormatter
from utils.constants import AZURE_FUNCTION_URL, AZURE_FUNCTION_APP_KEY, AZURE_DEVOPS_PAT, LOG_LEVEL_VALUE


if not AZURE_FUNCTION_URL or not AZURE_FUNCTION_APP_KEY or not AZURE_DEVOPS_PAT:
    raise ValueError("Required environment variables AZURE_FUNCTION_URL, AZURE_FUNCTION_APP_KEY, or AZURE_DEVOPS_PAT are not set.")

logging.basicConfig(level=LOG_LEVEL_VALUE, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AzureDevOpsTool(BaseTool):
    def __init__(self, agent=None):
        self._boards_cache = []
        self._tasks_cache = []
        self._formatted_boards_cache = ""
        self.agent = agent 
        self.db = AzureDevOpsDBHelper()

    def name(self):
        return "azure_devops"
    
    def triggers(self):
        return ["azure devops",
                "devops",
                "get boards",
                "work items",
                "azure boards",
                "add task",
                "create tasks from board",
                "analyze board"
        ]

    async def run(self, user_input: str) -> str:
        normalized = user_input.lower()
        logger.info(f"Azure DevOps Tool received input: {normalized}")
        if any(phrase in normalized for phrase in ["get boards", "get work items", "list boards", "my boards", "azure boards"]):
            logger.info("Trigger matched: get boards/work items")
            return self._get_boards()
        elif "create tasks from board" in normalized or "analyze board" in normalized or "add task" in normalized:
            logger.info("Trigger matched: create/analyze tasks from board")
            return await self._create_tasks_from_board(user_input)
        elif "show board ids" in normalized:
            logger.info("Trigger matched: show board ids")
            return self._list_board_ids()
        logger.warning("No recognized Azure DevOps command in input.")
        return "Azure DevOps: Command not recognized."

    def _get_boards(self):
        logger.info("Fetching Azure DevOps boards...")
        auth_str = f"user:{AZURE_DEVOPS_PAT}"
        headers = {
            "Authorization": f"Basic {base64.b64encode(auth_str.encode()).decode()}"
        }
        url = f"{AZURE_FUNCTION_URL}api/GetMyBoards?code={AZURE_FUNCTION_APP_KEY}"
        logger.debug(f"Requesting boards from URL: {url}")
        response = requests.get(url, headers=headers)
        logger.debug(f"Response status code: {response.status_code}")
        response.raise_for_status()
        logger.info("Boards fetched successfully.")
        boards = response.json()
        raw_items = boards.get("value", [])
        logger.info(f"Total items received: {len(raw_items)}")

        # Separate work items and tasks
        work_items = []
        for item in raw_items:
            work_item_type = item.get("fields", {}).get("System.WorkItemType", "").lower()
            if work_item_type != "task":
                logger.info(f"Processing item with type: {work_item_type}")
                logger.info(f"Found work item: {item.get('id')}")
                logger.info(f"Work item details: {item}")
                work_items.append(WorkItem.from_api_workitem(item))
            

        logger.info(f"Work items: {len(work_items)}")
        # Cache separately
        self._boards_cache = work_items
        
        # Save to database
        logger.info("Saving work items and to database...")
        self.save_work_items_to_database(self._boards_cache)
        
        # Filter in-progress work items for speech response
        in_progress_summary = self._summarize_in_progress_items(self._boards_cache)
        logger.info("Returning in-progress summary.")
        return in_progress_summary

    def _add_task(self, parent_id=9746, task_title="Task Title", task_description="Task Description"):
        logger.info(f"Adding task: parent_id={parent_id}, title={task_title}")
        auth = base64.b64encode(f":{AZURE_DEVOPS_PAT}".encode()).decode()
        headers = {
            "x-functions-key": AZURE_FUNCTION_APP_KEY,
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        url = f"{AZURE_FUNCTION_URL}/api/AddTaskToWorkItem"
        payload = {
            "parent_id": parent_id,
            "title": task_title,
            "description": task_description
        }
        logger.debug(f"POST {url} with payload: {payload}")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        logger.debug(f"Response status code: {response.status_code}")
        response.raise_for_status()
        logger.info("Task added successfully.")
        return json.dumps(response.json(), indent=2)

    async def _create_tasks_from_board(self, user_input):
        logger.info(f"Creating tasks from board with user input: {user_input}")
        import re
        match = re.search(r"\b(\d{4,})\b", user_input)
        if not match:
            logger.warning("No work item ID found in user input.")
            return "No work item ID found in your input."
        parent_id = int(match.group(1))
        logger.info(f"Extracted parent_id: {parent_id}")

        # Find work item in database.
        work_item = self.db.get_work_item_by_id(id=parent_id)
        
        if not work_item:
            logger.warning(f"Work item with ID {parent_id} not found in database.")
            return f"Work item with ID {parent_id} not found in database. Please run 'get boards' first."

        # Get plain text version of the work item
        formatted = work_item.to_prompt_string()         
        logger.debug(f"Formatted work item for LLM: {formatted}")
        response = ""
        if self.agent:
            # Prompt Gemini to generate tasks
            prompt = (
                "Given the following Azure Devops work item, generate a list of tasks with short titles and detailed descriptions.\n"
                "As a developer these work items will most likly be for something in the Micorsoft ecosystem, power apps, dataverse, plugins, actions, Azure functions.\n"
                f"Work Item:\n{formatted}\n\n"
                f"Additional User Context: {user_input}\n\n"
                "Return the tasks in this JSON list format: [\n"
                "  {\"title\": \"short task title\", \"description\": \"detailed description\" }, ...\n"
                "]"
            )
            logger.info(f"Prompting Gemini with: {prompt}")
            response = await self.agent.get_response(prompt)

        else:
            logger.error("No agent registered to handle LLM requests.")
            return "No agent registered to handle LLM requests."

        try:
            raw = response.strip()
            logger.debug(f"Raw LLM response: {raw}")
            with open("temp_memory/last_llm_response.json", "w", encoding="utf-8") as f:
                f.write(raw)

            # Remove markdown code block if present
            if raw.startswith("```json"):
                raw = raw.removeprefix("```json").strip()
            if raw.endswith("```"):
                raw = raw.removesuffix("```" ).strip()

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

                _id = hashlib.md5(f"{parent_id}-{title}".encode()).hexdigest()
                # save to database
                task_model = DevOpsTask(
                    id=_id,
                    parent_id=parent_id,
                    title=title,
                    description=description
                )
                self.db.log_task(task_model)
                logger.debug(f"Task model created: {task_model}")

                # Format and prepare for appending to file
                appended_output.append(
                    f"Task (Parent ID: {parent_id})\nTitle: {title}\nDescription: {description}\n{'-'*60}\n"
                )

            summary = ", ".join(task_titles)
            logger.info(f"Successfully added tasks to work item {parent_id}: {summary}")
            return f"Successfully added tasks to work item {parent_id}: {summary}"
        except Exception as e:
            logger.error(f"Failed to parse tasks from LLM response: {e}")
            return f"Failed to parse tasks from LLM response: {e}\nRaw Response: {response}"

    def _list_board_ids(self):
        if not self._boards_cache:
            logger.warning("No boards cached. Please run 'get boards' first.")
            return "No boards cached. Please run 'get boards' first."

        lines = []
        for board in self._boards_cache:
            # Use attribute access for model
            name = getattr(board, "title", "Unknown")
            id_ = getattr(board, "id", "No ID")
            logger.debug(f"Board: {name} (ID: {id_})")
            lines.append(f"{name}: {id_}")
        return "\n".join(lines)

    def save_work_items_to_database(self, work_items: list[WorkItem]):
        logger.info(f"Saving {len(work_items)} work items to database...")
        for item in work_items:
            logger.debug(f"Saving work item: {item}")
            self.db.log_work_item(item)
        logger.info("Work items saved.")
        return f"Saved {len(work_items)} work items to database."

    def save_work_item_tasks_to_database(self, tasks: list[DevOpsTask]):
        logger.info(f"Saving {len(tasks)} work item tasks to database...")
        for task in tasks:
            logger.debug(f"Saving task: {task}")
            self.db.log_task(task)
        logger.info("Work item tasks saved.")
        return f"Saved {len(tasks)} work item tasks to database."

    def _summarize_in_progress_items(self, work_items):
        summaries = []
        for item in work_items:
            # Use 'state' for status if that's your model's field
            state = getattr(item, 'status', '').lower()
            if state == "in progress":
                title = getattr(item, 'title', 'No Title')
                id = getattr(item, 'id', 'Unknown ID')
                logger.debug(f"In-progress item: {title} (ID: {id})")
                summaries.append(f"{title} (ID: {id})")

        if not summaries:
            logger.info("No in-progress work items found.")
            return "No in-progress work items found."
        logger.info(f"Found {len(summaries)} in-progress work items.")
        return "In-progress work items:\n" + "\n".join(summaries)
