import os
import dotenv
from agents.gemini_agent import GeminiAIAgent
from .azure_devops_tool import AzureDevOpsTool
from .weather_tool import WeatherTool
from .rag_memory_tool import RAGMemoryTool

# Load Gemini API key
GEMINI_KEY = os.getenv("GEMINI_KEY")
gemini_agent = GeminiAIAgent(GEMINI_KEY)

# List of available tools, that the agent has access to.
TOOLS_LIST = [ 
    AzureDevOpsTool(), 
    WeatherTool(), 
    RAGMemoryTool(fallback_llm=gemini_agent) 
    ]  