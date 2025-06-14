import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from utils.tool_manager import MCPTool, ToolManager

logger = logging.getLogger(__name__)

@dataclass
class ToolExecutionResult:
    """Represents the result of executing an MCP tool."""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: Optional[float] = None

class DynamicToolHandler:
    """
    Universal tool handler that can dynamically execute any MCP tool
    without requiring domain-specific knowledge.
    """
    
    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager
        self.execution_history: List[ToolExecutionResult] = []
        
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolExecutionResult:
        """
        Execute any MCP tool dynamically based on its schema.
        """
        import time
        start_time = time.time()
        
        try:
            # Get the tool definition
            tool = self.tool_manager.get_tool_by_name(tool_name)
            if not tool:
                error_msg = f"Tool '{tool_name}' not found"
                logger.error(error_msg)
                return ToolExecutionResult(
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=error_msg
                )
            
            # Validate parameters against tool schema
            validated_params = self._validate_parameters(tool, parameters)
            if validated_params is None:
                error_msg = f"Parameter validation failed for tool '{tool_name}'"
                logger.error(error_msg)
                return ToolExecutionResult(
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=error_msg
                )
            
            # Execute the tool using the appropriate protocol
            result = await self._execute_tool_on_server(tool, validated_params)
            
            execution_time = time.time() - start_time
            
            # Create successful result
            execution_result = ToolExecutionResult(
                tool_name=tool_name,
                success=True,
                result=result,
                execution_time=execution_time
            )
            
            self.execution_history.append(execution_result)
            logger.info(f"Successfully executed tool '{tool_name}' in {execution_time:.2f}s")
            
            return execution_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            logger.error(error_msg)
            
            execution_result = ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time
            )
            
            self.execution_history.append(execution_result)
            return execution_result
    
    def _validate_parameters(self, tool: MCPTool, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate parameters against the tool's schema.
        Returns validated parameters or None if validation fails.
        """
        try:
            # If no schema is provided, assume all parameters are valid
            if not tool.schema:
                logger.warning(f"No schema found for tool '{tool.name}', skipping validation")
                return parameters
            
            # Basic validation based on schema
            schema = tool.schema
            validated_params = {}
            
            # Check required parameters
            required_params = schema.get('required', [])
            for param in required_params:
                if param not in parameters:
                    logger.error(f"Missing required parameter '{param}' for tool '{tool.name}'")
                    return None
            
            # Validate parameter types if schema provides them
            properties = schema.get('properties', {})
            for param_name, param_value in parameters.items():
                if param_name in properties:
                    param_schema = properties[param_name]
                    if not self._validate_parameter_type(param_value, param_schema):
                        logger.error(f"Invalid type for parameter '{param_name}' in tool '{tool.name}'")
                        return None
                
                validated_params[param_name] = param_value
            
            return validated_params
            
        except Exception as e:
            logger.error(f"Parameter validation error for tool '{tool.name}': {e}")
            return None
    
    def _validate_parameter_type(self, value: Any, param_schema: Dict[str, Any]) -> bool:
        """
        Validate a single parameter against its schema.
        """
        try:
            expected_type = param_schema.get('type')
            if not expected_type:
                return True  # No type specified, assume valid
            
            # Map JSON schema types to Python types
            type_mapping = {
                'string': str,
                'integer': int,
                'number': (int, float),
                'boolean': bool,
                'array': list,
                'object': dict
            }
            
            expected_python_type = type_mapping.get(expected_type)
            if expected_python_type:
                return isinstance(value, expected_python_type)
            
            return True  # Unknown type, assume valid
            
        except Exception:
            return True  # If validation fails, assume valid
    
    async def _execute_tool_on_server(self, tool: MCPTool, parameters: Dict[str, Any]) -> Any:
        """
        Execute the tool on its originating MCP server using the appropriate protocol client.
        """
        try:
            # Get the protocol client for this server
            client = self.tool_manager.get_protocol_client(tool.server_id)
            if not client:
                raise Exception(f"No protocol client available for server '{tool.server_id}'")
            
            # Execute the tool using the protocol client
            result = await client.execute_tool(tool.name, parameters)
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute tool '{tool.name}' on server '{tool.server_id}': {e}")
            raise
    
    
    def get_execution_history(self) -> List[ToolExecutionResult]:
        """Get the history of tool executions."""
        return self.execution_history
    
    def get_last_execution_result(self) -> Optional[ToolExecutionResult]:
        """Get the result of the last tool execution."""
        return self.execution_history[-1] if self.execution_history else None
    
    def clear_execution_history(self):
        """Clear the execution history."""
        self.execution_history.clear()
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about tool executions."""
        if not self.execution_history:
            return {"total_executions": 0}
        
        successful_executions = [r for r in self.execution_history if r.success]
        failed_executions = [r for r in self.execution_history if not r.success]
        
        avg_execution_time = None
        if successful_executions:
            times = [r.execution_time for r in successful_executions if r.execution_time]
            if times:
                avg_execution_time = sum(times) / len(times)
        
        return {
            "total_executions": len(self.execution_history),
            "successful_executions": len(successful_executions),
            "failed_executions": len(failed_executions),
            "success_rate": len(successful_executions) / len(self.execution_history) if self.execution_history else 0,
            "average_execution_time": avg_execution_time
        }

class ToolRouter:
    """
    Routes tool execution requests to the appropriate handler.
    Provides intelligent tool selection and parameter extraction.
    """
    
    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager
        self.tool_handler = DynamicToolHandler(tool_manager)
        
    async def route_and_execute(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Optional[ToolExecutionResult]:
        """
        Analyze user input, determine if a tool should be executed, and execute it.
        """
        # Find matching tools
        matching_tools = self._find_matching_tools(user_input)
        
        if not matching_tools:
            return None
        
        # Select the best matching tool
        selected_tool = self._select_best_tool(matching_tools, user_input)
        
        # Extract parameters from user input
        parameters = self._extract_parameters(selected_tool, user_input, context)
        
        # Execute the tool
        result = await self.tool_handler.execute_tool(selected_tool.name, parameters)
        return result
    
    def _find_matching_tools(self, user_input: str) -> List[MCPTool]:
        """
        Find tools that might be relevant to the user input.
        """
        # Extract keywords from user input
        keywords = self._extract_keywords(user_input)
        
        # Find tools that match these keywords
        matching_tools = self.tool_manager.find_tools_by_keywords(keywords)
        
        return matching_tools
    
    def _extract_keywords(self, user_input: str) -> List[str]:
        """
        Extract relevant keywords from user input.
        """
        # Simple keyword extraction - could be enhanced with NLP
        words = user_input.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add some common action keywords
        action_keywords = []
        if any(word in user_input.lower() for word in ['open', 'navigate', 'go to', 'visit']):
            action_keywords.append('browser')
        if any(word in user_input.lower() for word in ['screenshot', 'capture', 'image']):
            action_keywords.append('screenshot')
        if any(word in user_input.lower() for word in ['search', 'find', 'look for']):
            action_keywords.append('search')
        if any(word in user_input.lower() for word in ['create', 'make', 'add', 'new']):
            action_keywords.append('create')
        
        return keywords + action_keywords
    
    def _select_best_tool(self, tools: List[MCPTool], user_input: str) -> MCPTool:
        """
        Select the best tool from a list of matching tools.
        """
        if len(tools) == 1:
            return tools[0]
        
        # Simple scoring based on keyword matches
        best_tool = tools[0]
        best_score = 0
        
        user_lower = user_input.lower()
        
        for tool in tools:
            score = 0
            tool_text = f"{tool.name} {tool.description}".lower()
            
            # Count keyword matches
            for word in user_lower.split():
                if len(word) > 2 and word in tool_text:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_tool = tool
        
        return best_tool
    
    def _extract_parameters(self, tool: MCPTool, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract parameters for tool execution from user input and context.
        """
        parameters = {}
        
        # Basic parameter extraction - could be enhanced with NLP
        if tool.schema and 'properties' in tool.schema:
            for param_name, param_schema in tool.schema['properties'].items():
                param_type = param_schema.get('type', 'string')
                
                # Try to extract parameter value from user input
                if param_type == 'string':
                    # Look for URL patterns if parameter name suggests URL
                    if 'url' in param_name.lower():
                        import re
                        url_pattern = r'https?://[^\s]+'
                        urls = re.findall(url_pattern, user_input)
                        if urls:
                            parameters[param_name] = urls[0]
                    
                    # For other string parameters, use the user input or context
                    elif param_name.lower() in user_input.lower():
                        parameters[param_name] = user_input
                
                # Add default values from schema if available
                if param_name not in parameters and 'default' in param_schema:
                    parameters[param_name] = param_schema['default']
        
        # Add context parameters if available
        if context:
            parameters.update(context)
        
        return parameters