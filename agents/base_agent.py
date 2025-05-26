from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Each agent must implement the `get_response` method.
    Optionally, agents can handle memory, tools, and chat history.
    """

    def __init__(self, name: str = "base", tools: Optional[list] = None):
        self.name = name
        self.tools = tools or []

    @abstractmethod
    async def get_response(self, user_input: str, history: Optional[str] = None) -> Any:
        """
        Generate a response based on user input (and optionally conversation history).
        Must be implemented by subclasses.
        """
        pass

    def name(self) -> str:
        """Return the name of the agent."""
        return self.name

    def register_tool(self, tool):
        """Optionally allow tools to be registered dynamically."""
        self.tools.append(tool)