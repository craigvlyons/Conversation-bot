from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

class GeminiAIAgent:
    def __init__(self, api_key, tools=None):
        self.model = GeminiModel(model_name="gemini-1.5-flash", api_key=api_key)
        self.agent = Agent(self.model)
        self.tools = tools or []

    async def get_response(self, user_input):
        for tool in self.tools:
            if tool.name() in user_input.lower():
                return await tool.run(user_input)

        response = await self.agent.run(user_input)
        return response.data








# from pydantic_ai import Agent
# from pydantic_ai.models.gemini import GeminiModel
# from models.devops_work_item_formatter import DevOpsWorkItemFormatter
# import os
# # Add this import for your local LLM agent (e.g., Llama)
# # from pydantic_ai.models.llama import LlamaModel

# FUNCTION_BASE_URL = os.getenv("FUNCTION_BASE_URL")
# FUNCTION_APP_KEY = os.getenv("FUNCTION_APP_KEY")
# AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")

# class GeminiAIAgent:
#     def __init__(self, api_key, tools=None, local_llm_agent=None):
#         self.model = GeminiModel(model_name="gemini-1.5-flash", api_key=api_key)
#         self.agent = Agent(self.model)
#         self.tools = tools or []
#         # self.local_llm_agent = local_llm_agent  # Optional: for fallback or extraction

#     async def get_response(self, user_input):
#         # Weather tool
#         if "weather" in user_input.lower():
#             for tool in self.tools:
#                 if hasattr(tool, "get_weather"):
#                     location, city_name = await self.extract_location(user_input)
#                     return tool.get_weather(location, city_name)
#         # Azure DevOps tool
#         if "azure devops" in user_input.lower() or "devops" in user_input.lower() or "board" in user_input.lower() or "work item" in user_input.lower():
#             for tool in self.tools:
#                 if hasattr(tool, "run") and tool.name() == "azure_devops":
#                     # Example: parse action and params from user_input (simple demo, real use should use NLP)
#                     if "board" in user_input.lower():
#                         # Example: get boards (requires function_url and pat)
#                          # https://devopsfunctionappmcp.azurewebsites.net/api/GetMyBoards?code={function key}
#                         function_url = f"{FUNCTION_BASE_URL}api/GetMyBoards?code={FUNCTION_APP_KEY}" 
#                         pat = AZURE_DEVOPS_PAT  
#                         return await tool.run("get_boards", function_url=function_url, pat=pat)
                    
#                     elif "add task" in user_input.lower():
#                         """
#                         we will use a prompt to extract the parent ID, and have the llm generate a list of tasks for the work item.

#                         Example user input:

#                         "Add a task to the work item with ID 9746. The task title is 'Task Title' and the description is 'Task Description'."

#                         "Give me a list of tasks for the work item with ID 9746. The task title is 'Task Title' and the description is 'Task Description'.'"

#                         Example response from the LLM:

#                             [ parent_id = 9746
#                               task_title = "update the documentation"
#                               task_description = "Update the documentation to reflect the latest changes in the API." ,
#                               parent_id = 9746
#                               task_title = "fix the bug"
#                               task_description = "Fix the bug that causes the application to crash when the user clicks the 'Save' button." ]
#                         """
#                         parent_id = 9746
#                         task_title = "Task Title"
#                         task_description = "Task Description"
#                         return await tool.run(
#                             "add_task",
#                             function_app_url=FUNCTION_BASE_URL,
#                             function_app_key=FUNCTION_APP_KEY,
#                             azure_devops_pat=AZURE_DEVOPS_PAT,
#                             parent_id=parent_id,
#                             task_title=task_title,
#                             task_description=task_description
#                         )
#         response = await self.agent.run(user_input)
#         work_items = response.get("value", [])  # extract list of items
#         top_level_items = []
#         task_items = []

#         for item in work_items:
#             work_item_type = item.get("fields", {}).get("System.WorkItemType", "")
#             if work_item_type.lower() == "task":
#                 task_items.append(item)
#             else:
#                 top_level_items.append(item)

#         # Save to work items file
#         with open("work_items.txt", "w", encoding="utf-8") as file:
#             file.write("▶ TOP-LEVEL WORK ITEMS:\n\n")
#             for item in top_level_items:
#                 formatted = DevOpsWorkItemFormatter.format(item)
#                 file.write(formatted + "\n")

#         # Save to work items tasks file
#         with open("work_items_tasks.txt", "w", encoding="utf-8") as file:
#             file.write("\n▶ TASKS:\n\n")
#             for item in task_items:
#                 formatted = DevOpsWorkItemFormatter.format(item)
#                 file.write(formatted + "\n")

#         return response.data

#     async def extract_location(self, user_input):
#         prompt = f"Extract the city name from this sentence. If no city is mentioned, return 'Colorado Springs'.\nSentence: '{user_input}'\nCity:"
#         #print(f"[extract_location] Asking Gemini: {prompt}")
#         response = await self.agent.run(prompt)
#         city = response.data.strip()
#         #print(f"[extract_location] Gemini extracted: {city}")
#         from models.cities import get_city
#         city_cashe = get_city(city)

#         return (city_cashe, city or "Denver") 

#     async def run_tool(self, tool_name, *args, **kwargs):
#         for tool in self.tools:
#             if tool.name() == tool_name:
#                 return await tool.run(*args, **kwargs)
#         raise ValueError(f"Tool '{tool_name}' not found.")

