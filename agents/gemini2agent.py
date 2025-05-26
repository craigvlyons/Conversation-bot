from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from agents.base_agent import BaseAgent
from tools.base_tool import BaseTool
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeminiAIAgent2(BaseAgent):
    def __init__(self, api_key, tools=None):
        super().__init__(name="gemini2", tools=tools)
        self.model = GeminiModel(model_name="gemini-2.0-flash", api_key=api_key)
        self.agent = Agent(self.model)
        self.tools: List[BaseTool] = tools or []

    async def get_response(self, user_input: str, history: Optional[str]=None):
        context =  f"{history}\nUser: {user_input}" if history else user_input
        normalized_input = context.lower()

        for tool in self.tools:
            if any(trigger in normalized_input for trigger in tool.triggers()):
                logger.info(f"Using tool: {tool.name()} for input: {user_input}")
                return await tool.run(user_input)

        response = await self.agent.run(context)
        return response.data

    