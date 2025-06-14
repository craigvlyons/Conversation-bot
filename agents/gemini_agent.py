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

        # Check if this looks like a tool request using intent detection
        if self._should_route_to_mcp_agent(user_input):
            logger.info(f"Routing to MCP agent for potential tool execution: {user_input}")
            try:
                from agents.registry import AgentRegistry
                mcp_agent = AgentRegistry.get("mcp")
                if mcp_agent:
                    result = await mcp_agent.get_response(user_input, history)
                    # If MCP agent found and executed a tool, return its result
                    if result and "No matching tools found" not in result:
                        return result
            except Exception as e:
                logger.warning(f"Failed to route to MCP agent: {e}")

        # Fall back to normal agent response
        response = await self.agent.run(context)
        return response.data
    
    def _should_route_to_mcp_agent(self, user_input: str) -> bool:
        """
        Determine if user input should be routed to MCP agent for tool execution.
        Uses intent detection patterns to identify tool requests.
        """
        user_lower = user_input.lower()
        
        # Tool request indicators
        tool_indicators = [
            # Direct tool mentions
            "what tools", "available tools", "list tools", "show tools",
            
            # Action patterns that typically require tools
            "take a screenshot", "screenshot", "capture screen",
            "open", "navigate to", "go to", "visit",
            "create", "make", "add", "new",
            "search for", "find", "look up", "query",
            "run", "execute", "call",
            
            # Browser automation keywords
            "browser", "webpage", "website", "url", "click", "type",
            
            # DevOps keywords
            "work item", "task", "project", "azure", "devops",
            
            # File operations
            "file", "read", "write", "save", "load",
            
            # Testing keywords
            "test", "automation", "selenium"
        ]
        
        # Check for tool indicators
        if any(indicator in user_lower for indicator in tool_indicators):
            return True
        
        # Check for URL patterns (likely browser tool requests)
        import re
        url_pattern = r'https?://[^\s]+'
        if re.search(url_pattern, user_input):
            return True
        
        # Check for imperative verbs that suggest tool actions
        imperative_patterns = [
            r'\b(open|navigate|go|visit|take|capture|create|make|add|search|find|run|execute)\b'
        ]
        
        for pattern in imperative_patterns:
            if re.search(pattern, user_lower):
                return True
        
        return False

    