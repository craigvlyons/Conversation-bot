# tools/rag_memory_tool.py
from pymongo import MongoClient
from .base_tool import BaseTool
from utils.rag_helper import RAGHelper
import os

class RAGMemoryTool(BaseTool):
    def __init__(self):
        self.helper = RAGHelper()

    def name(self):
        return "rag_memory"

    async def run(self, user_input):
        lower_input = user_input.lower()
        if "remember" in lower_input:
            self.helper.add_memory(user_input, category="note")
            return "Got it. I'll remember that."

        elif "recall" in lower_input or "what do you remember" in lower_input:
            results = self.helper.query_memory(user_input, category="note")
            return "\n".join(results)

        return "I'm not sure what to do with that memory request."


