from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
# Add this import for your local LLM agent (e.g., Llama)
# from pydantic_ai.models.llama import LlamaModel

class GeminiAIAgent:
    def __init__(self, api_key, tools=None, local_llm_agent=None):
        self.model = GeminiModel(model_name="gemini-1.5-flash", api_key=api_key)
        self.agent = Agent(self.model)
        self.tools = tools or []
        self.local_llm_agent = local_llm_agent  # Optional: for fallback or extraction

    async def get_response(self, user_input):
        # Weather tool
        if "weather" in user_input.lower():
            for tool in self.tools:
                if hasattr(tool, "get_weather"):
                    location, city_name = await self.extract_location(user_input)
                    return tool.get_weather(location, city_name)
        # Azure DevOps tool
        if "azure devops" in user_input.lower() or "devops" in user_input.lower() or "board" in user_input.lower() or "work item" in user_input.lower():
            for tool in self.tools:
                if hasattr(tool, "run") and tool.name() == "azure_devops":
                    # Example: parse action and params from user_input (simple demo, real use should use NLP)
                    if "board" in user_input.lower():
                        # Example: get boards (requires function_url and pat)
                        # You may want to extract these from config or prompt user for them
                        function_url = "YOUR_FUNCTION_URL"  # TODO: Replace or extract
                        pat = "YOUR_PAT"  # TODO: Replace or extract
                        return await tool.run("get_boards", function_url=function_url, pat=pat)
                    elif "add task" in user_input.lower():
                        # Example: add task (requires several params)
                        # TODO: Extract these from user_input or config
                        function_app_url = "YOUR_FUNCTION_APP_URL"
                        function_app_key = "YOUR_FUNCTION_APP_KEY"
                        azure_devops_pat = "YOUR_AZURE_DEVOPS_PAT"
                        parent_id = "WORK_ITEM_ID"
                        task_title = "Task Title"
                        task_description = "Task Description"
                        return await tool.run(
                            "add_task",
                            function_app_url=function_app_url,
                            function_app_key=function_app_key,
                            azure_devops_pat=azure_devops_pat,
                            parent_id=parent_id,
                            task_title=task_title,
                            task_description=task_description
                        )
        response = await self.agent.run(user_input)
        return response.data

    async def extract_location(self, user_input):
        prompt = f"Extract the city name from this sentence. If no city is mentioned, return 'Denver'.\nSentence: '{user_input}'\nCity:"
        print(f"[extract_location] Asking Gemini: {prompt}")
        response = await self.agent.run(prompt)
        city = response.data.strip()
        print(f"[extract_location] Gemini extracted: {city}")
        from models.cities import get_city
        city_cashe = get_city(city)

        return (city_cashe, city or "Denver") 

    async def run_tool(self, tool_name, *args, **kwargs):
        for tool in self.tools:
            if tool.name() == tool_name:
                return await tool.run(*args, **kwargs)
        raise ValueError(f"Tool '{tool_name}' not found.")

