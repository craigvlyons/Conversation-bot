from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

class GeminiAIAgent:
    def __init__(self, api_key):
        self.model = GeminiModel(model_name="gemini-1.5-flash", api_key=api_key)
        self.agent = Agent(self.model)

    async def get_response(self, user_input):
        response = await self.agent.run(user_input)
        return response.data