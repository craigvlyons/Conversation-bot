from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from agents.base_agent import BaseAgent
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeminiAIAgent(BaseAgent):
    def __init__(self, api_key, tools=None):
        super().__init__(name="gemini", tools=tools)
        self.model = GeminiModel(model_name="gemini-2.0-flash-lite", api_key=api_key)
        self.agent = Agent(self.model)
        
    async def get_response(self, user_input: str, history: Optional[str]=None):
        context =  f"{history}\nUser: {user_input}" if history else user_input
        normalized_input = context.lower()

        # Check regular tools first
        for tool in self.tools:
            if any(trigger in normalized_input for trigger in tool.triggers()):
                logger.info(f"Using tool: {tool.name()} for input: {user_input}")
                return await tool.run(user_input)

        # Check for MCP tool triggers if MCP is enabled
        if self.mcp_enabled and hasattr(self, 'check_for_mcp_tool_trigger'):
            matching_tool = self.check_for_mcp_tool_trigger(user_input)
            if matching_tool:
                logger.info(f"MCP tool trigger detected: {matching_tool}")
                try:
                    # Try to execute the MCP tool through the registry
                    from agents.registry import AgentRegistry
                    mcp_agent = AgentRegistry.get("mcp")
                    if mcp_agent:
                        result = await mcp_agent.execute_mcp_tool(matching_tool, {})
                        if result and not isinstance(result, dict) or not result.get('error'):
                            return str(result)
                except Exception as e:
                    logger.warning(f"Failed to execute MCP tool {matching_tool}: {e}")

        # Fall back to normal agent response
        response = await self.agent.run(context)
        return response.data

    