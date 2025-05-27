from .azure_devops_tool import AzureDevOpsTool
from .weather_tool import WeatherTool
from .rag_memory_tool import RAGMemoryTool
from agents.fallback_agent import fallback_agent


# List of available tools, that the agent has access to.
TOOLS_LIST = [ 
    AzureDevOpsTool(), 
    WeatherTool(), 
    RAGMemoryTool(fallback_llm=fallback_agent) 
    ]  