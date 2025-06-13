from typing import Dict, List, Any, Optional, Union, Callable, Type
import json
import re
from dataclasses import dataclass
import html

from utils.mcp_client import ToolResponse

class CategoryHandler:
    """Base class for handling specific tool categories"""
    
    def __init__(self):
        self.name = "base"
    
    def preprocess_params(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess parameters before execution"""
        return params
    
    def format_result(self, tool_name: str, response: ToolResponse) -> ToolResponse:
        """Format the result after execution"""
        return response
    
    def handle_error(self, tool_name: str, error: str) -> str:
        """Handle and possibly transform errors"""
        return error


class BrowserToolHandler(CategoryHandler):
    """Handler for browser/Playwright tools"""
    
    def __init__(self):
        super().__init__()
        self.name = "browser"
    
    def preprocess_params(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess parameters for browser tools"""
        processed = params.copy()
        
        # Handle URL normalization
        if "url" in processed and processed["url"]:
            url = processed["url"]
            if not url.startswith(("http://", "https://")):
                processed["url"] = f"https://{url}"
        
        # Handle selector transformations
        if "selector" in processed and processed["selector"]:
            # Convert simple descriptions to likely selectors if they don't look like CSS selectors
            selector = processed["selector"]
            if not re.match(r"[.#\[\]:]", selector):
                # Try to convert to a likely selector
                if selector.lower() in ["submit", "login", "signup", "register"]:
                    processed["selector"] = f"button[type='submit'], input[type='submit'], button:contains('{selector}')"
                else:
                    processed["selector"] = f"#{selector}, .{selector}, [name='{selector}'], [id*='{selector}'], [class*='{selector}'], :contains('{selector}')"
        
        return processed
    
    def format_result(self, tool_name: str, response: ToolResponse) -> ToolResponse:
        """Format browser tool results"""
        if not response.is_success or response.result is None:
            return response
        
        # Create a new response with the same data
        new_response = ToolResponse(
            id=response.id,
            tool_name=response.tool_name,
            result=response.result,
            is_success=response.is_success,
            error=response.error,
            server_name=response.server_name,
            execution_time=response.execution_time,
            timestamp=response.timestamp,
            is_complete=response.is_complete,
            is_streaming=response.is_streaming,
            stream_data=response.stream_data
        )
        
        # Format based on tool type
        if "snapshot" in tool_name or "screenshot" in tool_name:
            # For snapshot/screenshot tools, create a better result format
            if isinstance(new_response.result, dict) and "data" in new_response.result:
                new_response.result = {
                    "image_data": new_response.result.get("data"),
                    "width": new_response.result.get("width", 0),
                    "height": new_response.result.get("height", 0),
                    "format": new_response.result.get("format", "png"),
                    "summary": f"Screenshot captured ({new_response.result.get('width', 0)}x{new_response.result.get('height', 0)})"
                }
        
        elif "navigate" in tool_name:
            # For navigation tools, extract the page title and URL
            if isinstance(new_response.result, dict):
                new_response.result = {
                    "url": new_response.result.get("url", ""),
                    "title": new_response.result.get("title", ""),
                    "success": True,
                    "summary": f"Navigated to: {new_response.result.get('title', 'page')}"
                }
        
        return new_response
    
    def handle_error(self, tool_name: str, error: str) -> str:
        """Handle browser tool errors"""
        if "element not found" in error.lower():
            return f"Element not found. Try with a different selector or wait for the page to load completely."
        elif "navigation failed" in error.lower():
            return f"Navigation failed. Check if the URL is correct and accessible."
        else:
            return error


class DevOpsToolHandler(CategoryHandler):
    """Handler for Azure DevOps tools"""
    
    def __init__(self):
        super().__init__()
        self.name = "devops"
    
    def preprocess_params(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess parameters for DevOps tools"""
        processed = params.copy()
        
        # Convert work item titles to title case for consistency
        if "title" in processed and isinstance(processed["title"], str):
            processed["title"] = processed["title"].title()
        
        return processed
    
    def format_result(self, tool_name: str, response: ToolResponse) -> ToolResponse:
        """Format DevOps tool results"""
        if not response.is_success or response.result is None:
            return response
        
        # Create a new response with the same data
        new_response = ToolResponse(
            id=response.id,
            tool_name=response.tool_name,
            result=response.result,
            is_success=response.is_success,
            error=response.error,
            server_name=response.server_name,
            execution_time=response.execution_time,
            timestamp=response.timestamp,
            is_complete=response.is_complete,
            is_streaming=response.is_streaming,
            stream_data=response.stream_data
        )
        
        # Format work item responses
        if "work_item" in tool_name:
            if isinstance(new_response.result, dict):
                # Add a formatted summary for work items
                work_item = new_response.result
                work_item_id = work_item.get("id", "Unknown")
                work_item_type = work_item.get("type", "Item")
                work_item_title = work_item.get("title", "Untitled")
                work_item_state = work_item.get("state", "Unknown")
                
                # Add a summary
                work_item["summary"] = f"{work_item_type} #{work_item_id}: {work_item_title} ({work_item_state})"
                
                # Format HTML description to plain text if present
                if "description" in work_item and work_item["description"]:
                    # Simple HTML to plain text conversion
                    desc = work_item["description"]
                    desc = re.sub(r'<br\s*/?>|<p>', '\n', desc)
                    desc = re.sub(r'<[^>]+>', '', desc)
                    desc = html.unescape(desc)
                    work_item["description_text"] = desc.strip()
                
                new_response.result = work_item
        
        return new_response
    
    def handle_error(self, tool_name: str, error: str) -> str:
        """Handle DevOps tool errors"""
        if "not authorized" in error.lower() or "unauthorized" in error.lower():
            return "Authorization failed. Please check your Azure DevOps credentials."
        elif "not found" in error.lower():
            if "work_item" in tool_name:
                return "Work item not found. Please check the work item ID."
            elif "project" in tool_name:
                return "Project not found. Please check the project name."
            else:
                return error
        else:
            return error


class FileSystemToolHandler(CategoryHandler):
    """Handler for filesystem tools"""
    
    def __init__(self):
        super().__init__()
        self.name = "filesystem"
    
    def preprocess_params(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess parameters for filesystem tools"""
        processed = params.copy()
        
        # Normalize file paths (replace backslashes with forward slashes)
        if "path" in processed and isinstance(processed["path"], str):
            processed["path"] = processed["path"].replace("\\", "/")
        
        if "file_path" in processed and isinstance(processed["file_path"], str):
            processed["file_path"] = processed["file_path"].replace("\\", "/")
        
        return processed
    
    def format_result(self, tool_name: str, response: ToolResponse) -> ToolResponse:
        """Format filesystem tool results"""
        if not response.is_success or response.result is None:
            return response
        
        # Create a new response with the same data
        new_response = ToolResponse(
            id=response.id,
            tool_name=response.tool_name,
            result=response.result,
            is_success=response.is_success,
            error=response.error,
            server_name=response.server_name,
            execution_time=response.execution_time,
            timestamp=response.timestamp,
            is_complete=response.is_complete,
            is_streaming=response.is_streaming,
            stream_data=response.stream_data
        )
        
        # Format based on tool type
        if "read" in tool_name:
            if isinstance(new_response.result, dict) and "content" in new_response.result:
                content = new_response.result["content"]
                path = new_response.result.get("path", "")
                
                # Add a summary
                new_response.result["summary"] = f"Read file: {path} ({len(content)} bytes)"
                
                # Add file type information
                if "." in path:
                    ext = path.split(".")[-1].lower()
                    new_response.result["file_type"] = ext
                    
                    # For known file types, add a content_type
                    content_types = {
                        "txt": "text/plain",
                        "md": "text/markdown",
                        "json": "application/json",
                        "xml": "application/xml",
                        "html": "text/html",
                        "csv": "text/csv",
                        "py": "text/x-python",
                        "js": "text/javascript",
                        "css": "text/css",
                    }
                    
                    new_response.result["content_type"] = content_types.get(ext, "text/plain")
        
        elif "list" in tool_name:
            if isinstance(new_response.result, dict) and "items" in new_response.result:
                items = new_response.result["items"]
                path = new_response.result.get("path", "")
                
                # Add a summary
                new_response.result["summary"] = f"Listed directory: {path} ({len(items)} items)"
                
                # Add counts by type
                files = [item for item in items if not item.get("is_directory", False)]
                directories = [item for item in items if item.get("is_directory", False)]
                
                new_response.result["file_count"] = len(files)
                new_response.result["directory_count"] = len(directories)
        
        return new_response
    
    def handle_error(self, tool_name: str, error: str) -> str:
        """Handle filesystem tool errors"""
        if "no such file" in error.lower() or "not found" in error.lower():
            return "File or directory not found. Please check the path."
        elif "permission" in error.lower():
            return "Permission denied. The tool does not have access to this file or directory."
        else:
            return error


class SearchToolHandler(CategoryHandler):
    """Handler for search tools"""
    
    def __init__(self):
        super().__init__()
        self.name = "search"
    
    def preprocess_params(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess parameters for search tools"""
        processed = params.copy()
        
        # Improve query formatting
        if "query" in processed and isinstance(processed["query"], str):
            # Remove excess whitespace
            processed["query"] = re.sub(r'\s+', ' ', processed["query"]).strip()
            
            # Add quotes for exact phrases if they're not already there
            if " " in processed["query"] and not (processed["query"].startswith('"') and processed["query"].endswith('"')):
                # Check if it looks like a natural language query vs. keywords
                if len(processed["query"]) > 20 and any(w in processed["query"].lower() for w in ["what", "how", "when", "why", "where", "who", "is", "are", "can", "could"]):
                    # Keep as is for natural language queries
                    pass
                else:
                    # Add quotes for keyword phrases
                    processed["query"] = f'"{processed["query"]}"'
        
        return processed
    
    def format_result(self, tool_name: str, response: ToolResponse) -> ToolResponse:
        """Format search tool results"""
        if not response.is_success or response.result is None:
            return response
        
        # Create a new response with the same data
        new_response = ToolResponse(
            id=response.id,
            tool_name=response.tool_name,
            result=response.result,
            is_success=response.is_success,
            error=response.error,
            server_name=response.server_name,
            execution_time=response.execution_time,
            timestamp=response.timestamp,
            is_complete=response.is_complete,
            is_streaming=response.is_streaming,
            stream_data=response.stream_data
        )
        
        # Format search results
        if isinstance(new_response.result, dict) and "results" in new_response.result:
            results = new_response.result["results"]
            query = new_response.result.get("query", "")
            
            # Add a summary
            new_response.result["summary"] = f"Search results for: {query} ({len(results)} results)"
            
            # Add formatted versions of results
            if results:
                formatted_results = []
                for i, result in enumerate(results):
                    formatted_result = {
                        "index": i + 1,
                        "title": result.get("title", "Untitled"),
                        "url": result.get("url", ""),
                        "snippet": result.get("snippet", ""),
                    }
                    
                    # Clean up snippet
                    if formatted_result["snippet"]:
                        # Remove excess whitespace
                        formatted_result["snippet"] = re.sub(r'\s+', ' ', formatted_result["snippet"]).strip()
                        # Truncate if too long
                        if len(formatted_result["snippet"]) > 200:
                            formatted_result["snippet"] = formatted_result["snippet"][:197] + "..."
                    
                    formatted_results.append(formatted_result)
                
                new_response.result["formatted_results"] = formatted_results
        
        return new_response
    
    def handle_error(self, tool_name: str, error: str) -> str:
        """Handle search tool errors"""
        if "rate limit" in error.lower():
            return "Search rate limit exceeded. Please try again later."
        elif "no results" in error.lower():
            return "No search results found. Try with different keywords."
        else:
            return error


class CategoryHandlerRegistry:
    """Registry for category handlers"""
    
    def __init__(self):
        self.handlers: Dict[str, CategoryHandler] = {}
        self.default_handler = CategoryHandler()
        
        # Register built-in handlers
        self.register_handler("browser", BrowserToolHandler())
        self.register_handler("devops", DevOpsToolHandler())
        self.register_handler("filesystem", FileSystemToolHandler())
        self.register_handler("search", SearchToolHandler())
    
    def register_handler(self, category: str, handler: CategoryHandler):
        """Register a handler for a category"""
        self.handlers[category] = handler
    
    def get_handler(self, category: str) -> CategoryHandler:
        """Get a handler for a category"""
        return self.handlers.get(category, self.default_handler)
    
    def preprocess_params(self, category: str, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess parameters for a tool"""
        handler = self.get_handler(category)
        return handler.preprocess_params(tool_name, params)
    
    def format_result(self, category: str, tool_name: str, response: ToolResponse) -> ToolResponse:
        """Format the result for a tool"""
        handler = self.get_handler(category)
        return handler.format_result(tool_name, response)
    
    def handle_error(self, category: str, tool_name: str, error: str) -> str:
        """Handle an error for a tool"""
        handler = self.get_handler(category)
        return handler.handle_error(tool_name, error)
