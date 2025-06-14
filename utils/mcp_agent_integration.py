"""
Integration layer for MCP tools with pydantic-ai agents.
This module provides the necessary functionality to register MCP tools with pydantic-ai agents
and handle function calling during conversations.
"""
from typing import Dict, List, Any, Optional, Callable, Union
import json
import logging
from pydantic_ai import Agent
from pydantic import BaseModel

from utils.mcp_function_schema import get_schema_generator, FunctionSchema
from agents.registry import AgentRegistry

logger = logging.getLogger(__name__)

class MCPAgentIntegration:
    """
    Handles integration of MCP tools with pydantic-ai agents.
    """
    
    def __init__(self):
        self.schema_generator = get_schema_generator()
        self.registered_functions: Dict[str, Callable] = {}
        self.mcp_executor: Optional[Callable] = None
    
    def set_mcp_executor(self, executor: Callable):
        """Set the MCP tool executor function"""
        self.mcp_executor = executor
    
    def register_mcp_tools_with_agent(self, agent: Agent, mcp_tools: Dict[str, Any]) -> None:
        """
        Register MCP tools as functions with a pydantic-ai agent.
        
        Args:
            agent: The pydantic-ai Agent instance
            mcp_tools: Dictionary of MCP tools from the client
        """
        if not self.mcp_executor:
            logger.error("MCP executor not set. Cannot register tools.")
            return
        
        if not mcp_tools:
            logger.info("No MCP tools to register")
            return
        
        logger.info(f"Registering {len(mcp_tools)} MCP tools with pydantic-ai agent")
        
        for tool_name, tool_info in mcp_tools.items():
            try:
                # Create wrapper function for this tool
                wrapper_func = self._create_tool_wrapper(tool_name, tool_info)
                
                # Register the function with pydantic-ai agent using the function method
                agent.function(wrapper_func)
                
                self.registered_functions[tool_name] = wrapper_func
                logger.debug(f"Registered MCP tool as function: {tool_name}")
                
            except Exception as e:
                logger.error(f"Failed to register MCP tool {tool_name}: {e}")
                logger.error(f"Tool info: {tool_info}")
                import traceback
                logger.error(traceback.format_exc())
    
    def _create_tool_wrapper(self, tool_name: str, tool_info: Dict[str, Any]) -> Callable:
        """
        Create a wrapper function for an MCP tool that's compatible with pydantic-ai.
        """
        # Extract tool metadata
        description = tool_info.get("description", f"Execute {tool_name}")
        input_schema = tool_info.get("inputSchema", {})
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])
        
        # Create a dynamic function that calls the MCP executor
        async def mcp_tool_wrapper(**kwargs) -> str:
            """
            Auto-generated wrapper for MCP tool execution.
            """
            try:
                logger.info(f"Executing MCP tool: {tool_name} with params: {kwargs}")
                
                # Call the MCP executor
                result = await self.mcp_executor(tool_name, kwargs)
                
                # Format the result for the LLM
                return self._format_tool_result(result, tool_name)
                
            except Exception as e:
                error_msg = f"Error executing {tool_name}: {str(e)}"
                logger.error(error_msg)
                return error_msg
        
        # Set function metadata for pydantic-ai
        mcp_tool_wrapper.__name__ = self._sanitize_function_name(tool_name)
        mcp_tool_wrapper.__doc__ = description
        
        # Add parameter annotations if possible
        self._add_parameter_annotations(mcp_tool_wrapper, properties, required)
        
        return mcp_tool_wrapper
    
    def _format_tool_result(self, result: Any, tool_name: str) -> str:
        """
        Format tool execution result for the LLM.
        """
        try:
            if hasattr(result, 'result') and result.result is not None:
                if isinstance(result.result, (dict, list)):
                    return json.dumps(result.result, indent=2)
                else:
                    return str(result.result)
            elif hasattr(result, 'error') and result.error:
                return f"Error: {result.error}"
            elif hasattr(result, 'is_success') and not result.is_success:
                return f"Tool execution failed: {getattr(result, 'error', 'Unknown error')}"
            else:
                # Handle raw results
                if isinstance(result, (dict, list)):
                    return json.dumps(result, indent=2)
                else:
                    return str(result)
        except Exception as e:
            return f"Error formatting result from {tool_name}: {str(e)}"
    
    def _sanitize_function_name(self, tool_name: str) -> str:
        """
        Sanitize tool name to be a valid Python function name.
        """
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', tool_name)
        
        if sanitized and sanitized[0].isdigit():
            sanitized = f"tool_{sanitized}"
        
        if not sanitized:
            sanitized = "unnamed_tool"
        
        return sanitized
    
    def _add_parameter_annotations(self, func: Callable, properties: Dict[str, Any], required: List[str]):
        """
        Add parameter annotations to the function for pydantic-ai.
        This is a simplified version - pydantic-ai will handle the full schema.
        """
        # For now, we'll let pydantic-ai infer from the docstring and usage
        # More sophisticated parameter handling can be added later
        pass
    
    def create_enhanced_agent(self, base_agent_class, *args, **kwargs):
        """
        Create an enhanced agent that supports MCP tools.
        """
        # Create the base agent
        agent = base_agent_class(*args, **kwargs)
        
        # Get MCP tools from registry if available
        if hasattr(agent, 'get_all_mcp_tools'):
            mcp_tools = agent.get_all_mcp_tools()
            if mcp_tools and self.mcp_executor:
                self.register_mcp_tools_with_agent(agent.agent, mcp_tools)
        
        return agent

class MCPToolChecker:
    """
    Utility class to check if user input should trigger MCP tools.
    """
    
    def __init__(self):
        self.tool_triggers: Dict[str, List[str]] = {}
    
    def register_tool_triggers(self, tool_name: str, triggers: List[str]):
        """Register triggers/keywords for a tool"""
        self.tool_triggers[tool_name] = [t.lower() for t in triggers]
    
    def check_for_tool_match(self, user_input: str, available_tools: List[str]) -> Optional[str]:
        """
        Check if user input matches any tool triggers.
        Returns the matching tool name or None.
        """
        user_lower = user_input.lower()
        
        # Check explicit tool triggers first
        for tool_name in available_tools:
            if tool_name in self.tool_triggers:
                triggers = self.tool_triggers[tool_name]
                if any(trigger in user_lower for trigger in triggers):
                    return tool_name
        
        # Basic keyword matching for common patterns
        tool_keywords = {
            'browser': ['open', 'navigate', 'visit', 'screenshot', 'click', 'type'],
            'devops': ['work item', 'task', 'project', 'create', 'list'],
            'search': ['search', 'find', 'query', 'lookup'],
            'file': ['read file', 'write file', 'create file', 'delete file']
        }
        
        for tool_name in available_tools:
            for category, keywords in tool_keywords.items():
                if category in tool_name.lower():
                    if any(keyword in user_lower for keyword in keywords):
                        return tool_name
        
        return None

# Enhanced agent classes that support MCP tools
class MCPEnhancedGeminiAgent:
    """
    Gemini agent enhanced with MCP tool capabilities.
    """
    
    def __init__(self, api_key: str, tools=None):
        from agents.gemini_agent import GeminiAIAgent
        
        self.base_agent = GeminiAIAgent(api_key, tools)
        self.mcp_integration = MCPAgentIntegration()
        self.tool_checker = MCPToolChecker()
        self._setup_mcp_integration()
    
    def _setup_mcp_integration(self):
        """Set up MCP integration with the agent"""
        # Get MCP executor from agent registry
        registry = AgentRegistry
        if hasattr(registry, 'get_tool_executor') and registry.get_tool_executor():
            executor = registry.get_tool_executor()
            if hasattr(executor, 'execute'):
                self.mcp_integration.set_mcp_executor(executor.execute)
    
    def register_mcp_tools(self, mcp_tools: Dict[str, Any]):
        """Register MCP tools with this agent"""
        self.base_agent.register_mcp_tools(mcp_tools)
        self.mcp_integration.register_mcp_tools_with_agent(self.base_agent.agent, mcp_tools)
    
    async def get_response(self, user_input: str, history: Optional[str] = None) -> str:
        """
        Enhanced get_response that can use MCP tools.
        """
        # Check if we should use MCP tools
        available_tools = list(self.base_agent.get_all_mcp_tools().keys())
        matching_tool = self.tool_checker.check_for_tool_match(user_input, available_tools)
        
        if matching_tool and self.base_agent.mcp_enabled:
            logger.info(f"MCP tool match found: {matching_tool}")
            # Let pydantic-ai handle the tool calling naturally
            # The tools are already registered with the agent
        
        # Use the base agent's response method
        # pydantic-ai will automatically call tools if appropriate
        return await self.base_agent.get_response(user_input, history)
    
    def __getattr__(self, name):
        """Delegate unknown attributes to the base agent"""
        return getattr(self.base_agent, name)

class MCPEnhancedGPTAgent:
    """
    GPT agent enhanced with MCP tool capabilities.
    """
    
    def __init__(self, api_key: str, tools=None):
        from agents.gpt_agent import GPT4oAgent
        
        self.base_agent = GPT4oAgent(api_key, tools)
        self.mcp_integration = MCPAgentIntegration()
        self.tool_checker = MCPToolChecker()
        self._setup_mcp_integration()
    
    def _setup_mcp_integration(self):
        """Set up MCP integration with the agent"""
        registry = AgentRegistry
        if hasattr(registry, 'get_tool_executor') and registry.get_tool_executor():
            executor = registry.get_tool_executor()
            if hasattr(executor, 'execute'):
                self.mcp_integration.set_mcp_executor(executor.execute)
    
    def register_mcp_tools(self, mcp_tools: Dict[str, Any]):
        """Register MCP tools with this agent"""
        self.base_agent.register_mcp_tools(mcp_tools)
        self.mcp_integration.register_mcp_tools_with_agent(self.base_agent.agent, mcp_tools)
    
    async def get_response(self, user_input: str, history: Optional[str] = None) -> str:
        """
        Enhanced get_response that can use MCP tools.
        """
        available_tools = list(self.base_agent.get_all_mcp_tools().keys())
        matching_tool = self.tool_checker.check_for_tool_match(user_input, available_tools)
        
        if matching_tool and self.base_agent.mcp_enabled:
            logger.info(f"MCP tool match found: {matching_tool}")
        
        return await self.base_agent.get_response(user_input, history)
    
    def __getattr__(self, name):
        """Delegate unknown attributes to the base agent"""
        return getattr(self.base_agent, name)

# Global integration instance
_integration: Optional[MCPAgentIntegration] = None

def get_mcp_integration() -> MCPAgentIntegration:
    """Get the global MCP integration instance"""
    global _integration
    if _integration is None:
        _integration = MCPAgentIntegration()
    return _integration