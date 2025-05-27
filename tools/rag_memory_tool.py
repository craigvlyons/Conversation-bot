# tools/rag_memory_tool.py
from pymongo import MongoClient
from .base_tool import BaseTool
from utils.rag_helper import RAGHelper
from datetime import datetime, timezone
from utils.constants import LOG_LEVEL_VALUE
import logging

# Configure logging
logging.basicConfig(level=LOG_LEVEL_VALUE, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RAGMemoryTool(BaseTool):
    def __init__(self, fallback_llm=None):
        self.helper = RAGHelper()
        self.fallback_llm = fallback_llm

    def name(self):
        return "rag_memory"
    
    def triggers(self):
        return ["remember", "recall", "what do you remember", "note",
                "clear memory", "delete memory", "forget", "remove memory",
                "do you remember", "remind me", "when did I"
        ]
    
    async def run(self, user_input):
        lower_input = user_input.lower()
        is_question = lower_input.strip().endswith("?") or lower_input.startswith(("do", "what", "when"))  # Common question starters do you, when did i, etc.
       
        # === Case 1: Save memory ===
        if "remember" in lower_input and not is_question:
            existing = self.helper.query_memory(user_input, category="note", top_k=1)
            if existing and existing[0].lower() in user_input.lower():
                return "I've already noted that."

            self.helper.add_memory(user_input, category="note")
            logger.info(f"Memory saved: {user_input}")
            return "Got it. I'll remember that."

        # === Case 2: Explicit memory recall prompt ===
        if "recall" in lower_input or "what do you remember" in lower_input:
            recent = (
                self.helper.collection
                .find({"category": "note"})
                .sort("timestamp", -1)
                .limit(10)
            )
            notes = [doc["content"] for doc in recent]
            return "\n• " + "\n• ".join(notes) if notes else "I don't remember anything yet."
        
        # === Case 3: Dynamic LLM-backed recall ===
        if "remember" in lower_input or "recall" in lower_input or is_question:
            memory = self.helper.query_memory(user_input, category="note", top_k=5)

            if memory:
                if self.fallback_llm:
                    prompt = f"""Here is the user's question: "{user_input}"

                    Here are some memories that may help:
                    {chr(10).join(f"- {m}" for m in memory)}

                    Based on this, answer the user's question naturally. If none of the memories are relevant, say so.
                    """
                    response = await self.fallback_llm.get_response(prompt)
                    return response
                else:
                    return "\n• " + "\n• ".join(memory)

            return "I don't remember anything relevant to that."
        
        # === Case 4: Clear memory logic ===
        if "clear memory" in lower_input or "delete memory" in lower_input:
            # Extract keyword (if any)
            words = lower_input.split()
            keywords = [w for w in words if w not in ["clear", "delete", "memory", "about"]]

            if not keywords:
                deleted = self.helper.collection.delete_many({"category": "note"})
                logger.info(f"Deleted all memory entries.")
                return f"🧹 Cleared {deleted.deleted_count} memory entries."

            # Delete documents containing any keyword
            keyword_filter = {"$or": [{"content": {"$regex": k, "$options": "i"}} for k in keywords]}
            deleted = self.helper.collection.delete_many({
                "category": "note",
                **keyword_filter
            })
            logger.info(f"Deleted {deleted.deleted_count} memory entries with keywords: {keywords}")
            return f"🧹 Cleared {deleted.deleted_count} memory entries containing: {', '.join(keywords)}."

        # === Case 5: Fallback for anything else ===
        if self.fallback_llm:
            response = await self.fallback_llm.get_response(user_input)
            return response

        return "I'm not sure what to do with that memory request."


# 🧠 Next steps to improve:
# Categorize memory entries (e.g. "hailey", "reminders", "appointments").

# Time-aware prompting (detect things like "yesterday", "today", "tomorrow").

# Improve fallback response to directly answer with "Yes, you fed Hailey yesterday" if it finds a confident match.

# Store structured fields in memory (e.g. {"event": "feed hailey", "date": "2025-05-24"}).

# Let me know if you want to start working on any of those — especially structured memory or temporal reasoning.



