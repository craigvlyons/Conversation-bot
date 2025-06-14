"""
Function schema generation for MCP tools to integrate with pydantic-ai agents.
Converts MCP tool definitions into function calling schemas that LLMs can understand.
"""
from typing import Dict, List, Any, Optional, Callable, Union
import json
import inspect
from dataclasses import dataclass

@dataclass
class FunctionSchema:
    """Schema for a function that can be called by an LLM"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable
    mcp_tool_name: Optional[str] = None

class MCPFunctionSchemaGenerator:
    """
    Generates function schemas from MCP tool definitions for use with pydantic-ai agents.
    """
    
    def __init__(self):
        self.generated_schemas: Dict[str, FunctionSchema] = {}
    
    def generate_function_schema(self, tool_name: str, tool_info: Dict[str, Any], 
                               executor_function: Callable) -> FunctionSchema:
        """
        Generate a function schema from an MCP tool definition.
        
        Args:
            tool_name: Name of the MCP tool
            tool_info: Tool metadata from MCP server
            executor_function: Function that will execute the tool
            
        Returns:
            FunctionSchema object ready for pydantic-ai registration
        """
        # Extract basic information
        description = tool_info.get("description", f"Execute {tool_name} tool")
        
        # Convert MCP parameters to function schema parameters
        mcp_params = tool_info.get("inputSchema", {}).get("properties", {})
        required_params = tool_info.get("inputSchema", {}).get("required", [])
        
        # Build function parameters schema
        parameters = self._build_parameters_schema(mcp_params, required_params)
        
        # Create the schema
        schema = FunctionSchema(
            name=self._sanitize_function_name(tool_name),
            description=description,
            parameters=parameters,
            function=executor_function,
            mcp_tool_name=tool_name
        )
        
        self.generated_schemas[tool_name] = schema
        return schema
    
    def _build_parameters_schema(self, mcp_params: Dict[str, Any], 
                                required_params: List[str]) -> Dict[str, Any]:
        """
        Convert MCP parameter schema to function calling parameter schema.
        """
        parameters = {
            "type": "object",
            "properties": {},
            "required": required_params
        }
        
        for param_name, param_info in mcp_params.items():
            param_schema = self._convert_parameter_type(param_info)
            parameters["properties"][param_name] = param_schema
        
        return parameters
    
    def _convert_parameter_type(self, param_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MCP parameter type to JSON schema type.
        """
        param_schema = {}
        
        # Copy basic properties
        if "type" in param_info:
            param_schema["type"] = param_info["type"]
        if "description" in param_info:
            param_schema["description"] = param_info["description"]
        if "enum" in param_info:
            param_schema["enum"] = param_info["enum"]
        if "default" in param_info:
            param_schema["default"] = param_info["default"]
        
        # Handle array types
        if param_info.get("type") == "array" and "items" in param_info:
            param_schema["items"] = self._convert_parameter_type(param_info["items"])
        
        # Handle object types
        if param_info.get("type") == "object" and "properties" in param_info:
            param_schema["properties"] = {}
            for prop_name, prop_info in param_info["properties"].items():
                param_schema["properties"][prop_name] = self._convert_parameter_type(prop_info)
            
            if "required" in param_info:
                param_schema["required"] = param_info["required"]
        
        return param_schema
    
    def _sanitize_function_name(self, tool_name: str) -> str:
        """
        Sanitize tool name to be a valid Python function name.
        """
        # Replace non-alphanumeric characters with underscores
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', tool_name)
        
        # Ensure it starts with a letter or underscore
        if sanitized and sanitized[0].isdigit():
            sanitized = f"tool_{sanitized}"
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "unnamed_tool"
        
        return sanitized
    
    def generate_schemas_from_mcp_tools(self, mcp_tools: Dict[str, Any], 
                                      executor_function: Callable) -> List[FunctionSchema]:
        """
        Generate function schemas for all MCP tools.
        
        Args:
            mcp_tools: Dictionary of MCP tools from client
            executor_function: Function that will execute MCP tools
            
        Returns:
            List of FunctionSchema objects
        """
        schemas = []
        
        for tool_name, tool_info in mcp_tools.items():
            try:
                schema = self.generate_function_schema(tool_name, tool_info, executor_function)
                schemas.append(schema)
            except Exception as e:
                print(f"Warning: Failed to generate schema for tool {tool_name}: {e}")
        
        return schemas
    
    def create_wrapper_function(self, tool_name: str, mcp_executor: Callable) -> Callable:
        """
        Create a wrapper function for an MCP tool that can be called by pydantic-ai.
        
        Args:
            tool_name: Name of the MCP tool
            mcp_executor: Function that executes MCP tools
            
        Returns:
            Async function that can be registered with pydantic-ai
        """
        async def mcp_tool_wrapper(**kwargs):
            """
            Wrapper function for MCP tool execution.
            This function will be called by the pydantic-ai agent.
            """
            try:
                # Execute the MCP tool
                result = await mcp_executor(tool_name, kwargs)
                
                # Format the result for the LLM
                if hasattr(result, 'result') and result.result is not None:
                    if isinstance(result.result, (dict, list)):
                        return json.dumps(result.result, indent=2)
                    else:
                        return str(result.result)
                elif hasattr(result, 'error') and result.error:
                    return f"Error: {result.error}"
                else:
                    return str(result)
                    
            except Exception as e:
                return f"Error executing {tool_name}: {str(e)}"
        
        # Set function metadata
        mcp_tool_wrapper.__name__ = self._sanitize_function_name(tool_name)
        mcp_tool_wrapper.__doc__ = f"Execute MCP tool: {tool_name}"
        
        return mcp_tool_wrapper
    
    def get_schema(self, tool_name: str) -> Optional[FunctionSchema]:
        """Get a generated schema by tool name"""
        return self.generated_schemas.get(tool_name)
    
    def get_all_schemas(self) -> Dict[str, FunctionSchema]:
        """Get all generated schemas"""
        return self.generated_schemas.copy()
    
    def clear_schemas(self):
        """Clear all generated schemas"""
        self.generated_schemas.clear()

# Global instance for use across the application
_schema_generator: Optional[MCPFunctionSchemaGenerator] = None

def get_schema_generator() -> MCPFunctionSchemaGenerator:
    """Get the global schema generator instance"""
    global _schema_generator
    if _schema_generator is None:
        _schema_generator = MCPFunctionSchemaGenerator()
    return _schema_generator