# agents/registry.py
from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent

class AgentRegistry:
    _agents: Dict[str, BaseAgent] = {}
    _tools_registry = None
    _tool_factory = None
    _tool_executor = None

    @classmethod
    def register(cls, name: str, agent: BaseAgent):
        cls._agents[name] = agent

    @classmethod
    def get(cls, name: str) -> Optional[BaseAgent]:
        return cls._agents.get(name)

    @classmethod
    def all(cls) -> Dict[str, BaseAgent]:
        return cls._agents
    
    @classmethod
    def set_tool_registry(cls, registry):
        """Set the tool registry for all agents to use"""
        cls._tools_registry = registry
        # Make the registry accessible to all registered agents
        for agent in cls._agents.values():
            if hasattr(agent, 'set_tool_registry'):
                agent.set_tool_registry(registry)
    
    @classmethod
    def set_tool_factory(cls, factory):
        """Set the tool factory for all agents to use"""
        cls._tool_factory = factory
        # Make the factory accessible to all registered agents
        for agent in cls._agents.values():
            if hasattr(agent, 'set_tool_factory'):
                agent.set_tool_factory(factory)
    
    @classmethod
    def set_tool_executor(cls, executor):
        """Set the tool executor for all agents to use"""
        cls._tool_executor = executor
        # Make the executor accessible to all registered agents
        for agent in cls._agents.values():
            if hasattr(agent, 'set_tool_executor'):
                agent.set_tool_executor(executor)
    
    @classmethod
    def get_tool_registry(cls):
        """Get the shared tool registry"""
        return cls._tools_registry
    
    @classmethod
    def get_tool_factory(cls):
        """Get the shared tool factory"""
        return cls._tool_factory
    
    @classmethod
    def get_tool_executor(cls):
        """Get the shared tool executor"""
        return cls._tool_executor
    
    @classmethod
    def register_tools_with_all_agents(cls, tools: Dict[str, Any]):
        """Register tools with all agents"""
        for agent in cls._agents.values():
            if hasattr(agent, 'register_mcp_tool'):
                for tool_name, tool_info in tools.items():
                    agent.register_mcp_tool(tool_name, tool_info)
