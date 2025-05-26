from abc import ABC, abstractmethod

class BaseTool(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def run(self, user_input: str) -> str:
        pass

    def triggers(self) -> list[str]:
        return []