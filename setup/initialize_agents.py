from agents.gemini_agent import GeminiAIAgent
from agents.gemini2agent import GeminiAIAgent2
from agents.gpt_agent import GPT4oAgent
from agents.registry import AgentRegistry
from tools.azure_devops_tool import AzureDevOpsTool
from tools.weather_tool import WeatherTool
from tools.rag_memory_tool import RAGMemoryTool
from utils.constants import GEMINI_KEY, OPENAI_KEY

# Instantiate core agents
primary_agent = GeminiAIAgent(api_key=GEMINI_KEY)       # Gemini - is probably good enough for basic tasks and cheap.
fallback_agent = GPT4oAgent(api_key=OPENAI_KEY)         # GPT - is probably better for code, then Gemini
secondary_agent = GeminiAIAgent2(api_key=GEMINI_KEY)    # Gemini2 - is probably better for more complex tasks, then Gemini 1.

# memory only
# memory_only_agent = GeminiAIAgent2(api_key=GEMINI_KEY)
# memory_tool = RAGMemoryTool(fallback_llm=fallback_agent)
# memory_only_agent.register_tool(memory_tool)

# Register them globally
AgentRegistry.register("primary", primary_agent)
AgentRegistry.register("fallback", fallback_agent)
AgentRegistry.register("gemini", primary_agent)
AgentRegistry.register("gpt4o", fallback_agent)
AgentRegistry.register("gemini2", secondary_agent)
# AgentRegistry.register("memory", memory_only_agent)

# Tools can be shared or scoped to agents
tools = [
    AzureDevOpsTool(agent=fallback_agent),
    WeatherTool(),
    RAGMemoryTool(fallback_llm=fallback_agent)
]

# Attach tools to the primary agent
for tool in tools:
    primary_agent.register_tool(tool)
    secondary_agent.register_tool(tool)