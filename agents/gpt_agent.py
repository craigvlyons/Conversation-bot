from agents.base_agent import BaseAgent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent

class GPT4oAgent(BaseAgent):
    def __init__(self, api_key: str, tools=None):
        super().__init__(name="gpt-4o-mini", tools=tools)
        model = OpenAIModel(model_name="gpt-4o", api_key=api_key)
        self.agent = Agent(model)

    async def get_response(self, user_input: str, history=None):
        context = f"{history}\nUser: {user_input}" if history else user_input
        response = await self.agent.run(context)
        return response.data
