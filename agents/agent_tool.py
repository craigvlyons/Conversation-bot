from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AgentTool(ABC):
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the tool."""
        pass
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> str:
        """Runs the tool with the given arguments and returns a string response."""
        pass