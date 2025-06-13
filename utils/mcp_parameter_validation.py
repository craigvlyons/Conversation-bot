import json
from typing import Dict, List, Any, Optional, Union, Tuple, Set
import re
from jsonschema import validate, ValidationError

class ToolParameterValidator:
    """Validator for tool parameters based on JSON schema"""
    
    def __init__(self):
        pass
    
    def validate_against_schema(self, params: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate parameters against a JSON schema"""
        if not schema:
            return True, ""
        
        try:
            # Extract the properties section if it exists
            if "properties" in schema:
                properties_schema = {
                    "type": "object",
                    "properties": schema["properties"],
                }
                
                # Add required properties if they exist
                if "required" in schema:
                    properties_schema["required"] = schema["required"]
                
                validate(instance=params, schema=properties_schema)
            else:
                validate(instance=params, schema=schema)
                
            return True, ""
            
        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_required_params(self, params: Dict[str, Any], required: List[str]) -> Tuple[bool, str]:
        """Validate that all required parameters are present"""
        missing = [param for param in required if param not in params]
        if missing:
            return False, f"Missing required parameters: {', '.join(missing)}"
        return True, ""
    
    def validate_parameter_types(self, params: Dict[str, Any], properties: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
        """Validate parameter types"""
        for name, value in params.items():
            if name in properties:
                prop = properties[name]
                expected_type = prop.get("type")
                
                if expected_type == "string" and not isinstance(value, str):
                    return False, f"Parameter '{name}' must be a string"
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    return False, f"Parameter '{name}' must be a number"
                elif expected_type == "integer" and not isinstance(value, int):
                    return False, f"Parameter '{name}' must be an integer"
                elif expected_type == "boolean" and not isinstance(value, bool):
                    return False, f"Parameter '{name}' must be a boolean"
                elif expected_type == "array" and not isinstance(value, list):
                    return False, f"Parameter '{name}' must be an array"
                elif expected_type == "object" and not isinstance(value, dict):
                    return False, f"Parameter '{name}' must be an object"
        
        return True, ""


class ParameterTransformer:
    """Transforms parameters from natural language to structured format"""
    
    def __init__(self):
        pass
    
    def extract_parameters(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters from natural language text based on schema"""
        if not schema or "properties" not in schema:
            return {}
        
        properties = schema["properties"]
        params = {}
        
        # Extract parameters based on property descriptions and names
        for prop_name, prop_info in properties.items():
            description = prop_info.get("description", "")
            prop_type = prop_info.get("type", "string")
            
            # Search for patterns like "parameter: value" or "parameter=value"
            param_patterns = [
                rf"{prop_name}[=:]\s*(\S+)",
                rf"{prop_name}\s+(?:is|as|to)\s+(\S+)",
            ]
            
            for pattern in param_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    params[prop_name] = self._convert_value(value, prop_type)
                    break
        
        # Try to extract missing required parameters based on descriptions
        if "required" in schema:
            for prop_name in schema["required"]:
                if prop_name in params:
                    continue
                
                if prop_name in properties:
                    description = properties[prop_name].get("description", "")
                    prop_type = properties[prop_name].get("type", "string")
                    
                    # Create a pattern based on the description
                    keywords = set(self._extract_keywords(description))
                    patterns = []
                    
                    for keyword in keywords:
                        if len(keyword) > 3:  # Only use meaningful keywords
                            patterns.append(rf"{keyword}\s+(?:is|as|to|of|for|with)\s+(\S+)")
                            patterns.append(rf"{keyword}[=:]\s*(\S+)")
                    
                    for pattern in patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            value = match.group(1)
                            params[prop_name] = self._convert_value(value, prop_type)
                            break
        
        return params
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "of", "in", "for", "to", "with", "on", "at", "from", "by", "about",
            "as", "into", "like", "through", "after", "over", "before", "between", "under",
            "and", "or", "not", "but", "if", "else", "when", "where", "how", "what", "why",
            "who", "which", "is", "are", "was", "were", "be", "been", "being", "have", "has",
            "had", "do", "does", "did", "will", "would", "shall", "should", "may", "might",
            "must", "can", "could"
        }
        
        # Split text into words and remove stop words
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def _convert_value(self, value: str, expected_type: str) -> Any:
        """Convert a string value to the expected type"""
        if expected_type == "string":
            # Remove quotes if present
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                return value[1:-1]
            return value
        
        elif expected_type == "number":
            try:
                if "." in value:
                    return float(value)
                return int(value)
            except ValueError:
                return value
        
        elif expected_type == "integer":
            try:
                return int(float(value))
            except ValueError:
                return value
        
        elif expected_type == "boolean":
            value_lower = value.lower()
            if value_lower in ["true", "yes", "1", "y"]:
                return True
            elif value_lower in ["false", "no", "0", "n"]:
                return False
            return value
        
        elif expected_type == "array":
            # Try to parse as JSON
            if value.startswith("[") and value.endswith("]"):
                try:
                    return json.loads(value)
                except:
                    pass
            
            # Split by commas otherwise
            return value.split(",")
        
        elif expected_type == "object":
            # Try to parse as JSON
            if value.startswith("{") and value.endswith("}"):
                try:
                    return json.loads(value)
                except:
                    pass
            
            return value
        
        return value


class ToolResultFormatter:
    """Formats tool results for display"""
    
    def __init__(self):
        pass
    
    def format_for_display(self, result: Any, tool_name: str, tool_category: str) -> Dict[str, Any]:
        """Format a result for display"""
        if result is None:
            return {"display": "No result", "type": "text"}
        
        # Handle different result types
        if isinstance(result, dict):
            return self._format_dict_result(result, tool_name, tool_category)
        elif isinstance(result, list):
            return self._format_list_result(result, tool_name, tool_category)
        elif isinstance(result, str):
            return self._format_string_result(result, tool_name, tool_category)
        else:
            return {"display": str(result), "type": "text"}
    
    def _format_dict_result(self, result: Dict[str, Any], tool_name: str, tool_category: str) -> Dict[str, Any]:
        """Format a dictionary result"""
        # Check if it's an image result
        if "image_data" in result or "data" in result and tool_category == "browser":
            return {
                "display": "Screenshot captured",
                "type": "image",
                "data": result.get("image_data") or result.get("data"),
                "format": result.get("format", "png"),
            }
        
        # Check if it's a search result
        if "results" in result and tool_category == "search":
            formatted_results = []
            for item in result.get("results", []):
                formatted_results.append({
                    "title": item.get("title", "Untitled"),
                    "url": item.get("url", ""),
                    "snippet": item.get("snippet", ""),
                })
            
            return {
                "display": f"Found {len(formatted_results)} results",
                "type": "search_results",
                "results": formatted_results,
            }
        
        # Check if it's a file result
        if "content" in result and tool_category == "filesystem":
            return {
                "display": f"File content ({len(result.get('content', ''))} bytes)",
                "type": "file",
                "content": result.get("content", ""),
                "path": result.get("path", ""),
                "content_type": result.get("content_type", "text/plain"),
            }
        
        # Check if it's a directory listing
        if "items" in result and tool_category == "filesystem":
            return {
                "display": f"Directory listing: {len(result.get('items', []))} items",
                "type": "directory",
                "items": result.get("items", []),
                "path": result.get("path", ""),
            }
        
        # Default: convert dict to formatted string
        return {
            "display": json.dumps(result, indent=2),
            "type": "json",
            "data": result,
        }
    
    def _format_list_result(self, result: List[Any], tool_name: str, tool_category: str) -> Dict[str, Any]:
        """Format a list result"""
        # Check if it's a list of items (e.g., work items)
        if all(isinstance(item, dict) for item in result) and len(result) > 0:
            # Convert to table format if possible
            if tool_category == "devops":
                # Extract common keys
                keys = set()
                for item in result:
                    keys.update(item.keys())
                
                # Include only common display fields
                display_fields = ["id", "title", "state", "type", "assignedTo", "createdBy", "createdDate"]
                headers = [field for field in display_fields if field in keys]
                
                rows = []
                for item in result:
                    row = [str(item.get(field, "")) for field in headers]
                    rows.append(row)
                
                return {
                    "display": f"List of {len(result)} items",
                    "type": "table",
                    "headers": headers,
                    "rows": rows,
                    "data": result,
                }
            
            return {
                "display": f"List of {len(result)} items",
                "type": "list",
                "items": result,
            }
        
        # Default: convert list to formatted string
        return {
            "display": json.dumps(result, indent=2),
            "type": "json",
            "data": result,
        }
    
    def _format_string_result(self, result: str, tool_name: str, tool_category: str) -> Dict[str, Any]:
        """Format a string result"""
        # Check if it looks like HTML
        if result.strip().startswith("<") and result.strip().endswith(">"):
            return {
                "display": result,
                "type": "html",
            }
        
        # Check if it looks like JSON
        if result.strip().startswith("{") and result.strip().endswith("}"):
            try:
                data = json.loads(result)
                return {
                    "display": json.dumps(data, indent=2),
                    "type": "json",
                    "data": data,
                }
            except:
                pass
        
        # Default: plain text
        return {
            "display": result,
            "type": "text",
        }
