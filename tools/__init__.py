from .azure_devops_tool import AzureDevOpsTool
from .weather_tool import WeatherTool
from .rag_memory_tool import RAGMemoryTool

# List of available tools, that the agent has access to.
TOOLS_LIST = [ 
    AzureDevOpsTool(), 
    WeatherTool(), 
    RAGMemoryTool() 
    ]  