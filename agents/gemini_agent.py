from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

TOOL_TRIGGER_MAP = {
     "azure_devops": [
        "azure devops",
        "devops",
        "get boards",
        "work items",
        "azure boards",
        "add task",
        "create tasks from board",
        "analyze board"
    ],
    "weather": ["weather", "forecast", "temperature"],
}


class GeminiAIAgent:
    def __init__(self, api_key, tools=None):
        self.model = GeminiModel(model_name="gemini-1.5-flash", api_key=api_key)
        self.agent = Agent(self.model)
        self.tools = tools or []

    async def get_response(self, user_input):
        normalized_input = user_input.lower()
        for tool in self.tools:
            triggers = TOOL_TRIGGER_MAP.get(tool.name(), [])
            if any(trigger in normalized_input for trigger in triggers):
                return await tool.run(user_input)

        response = await self.agent.run(user_input)
        return response.data

    