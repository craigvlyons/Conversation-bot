import os
import json
from typing import Dict, List, Any, Optional, Union, Callable, TypeVar
import re

# Import the MCP Client
from utils.mcp_client import MCPClient

T = TypeVar('T')

class MCPToolRegistry:
    """Registry for MCP tools with categorization and filtering capabilities"""
    
    CONFIG_PATH = "config/mcp_tools.json"
    
    def __init__(self, mcp_client: MCPClient = None, config_path: str = None):
        self.mcp_client = mcp_client or MCPClient()
        self.config_path = config_path or self.CONFIG_PATH
        self.tool_categories: Dict[str, List[str]] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}
        self.enabled_tools: Dict[str, bool] = {}
        
    def load_config(self) -> bool:
        """Load tool configuration from file"""
        try:
            if not os.path.exists(self.config_path):
                print(f"❌ MCP tools config file not found: {self.config_path}")
                return False
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Process tool categories and metadata from config
            if "categories" in config:
                self.tool_categories = config["categories"]
            
            if "metadata" in config:
                self.tool_metadata = config["metadata"]
            
            if "enabled" in config:
                self.enabled_tools = config["enabled"]
            
            print(f"✅ Loaded MCP tools config from {self.config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading MCP tools config: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save tool configuration to file"""
        try:
            config = {
                "categories": self.tool_categories,
                "metadata": self.tool_metadata,
                "enabled": self.enabled_tools
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Saved MCP tools config to {self.config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving MCP tools config: {e}")
            return False
    
    def register_from_mcp_client(self) -> int:
        """Register all tools from the MCP client"""
        if not self.mcp_client:
            print("❌ No MCP client provided")
            return 0
        
        all_tools = self.mcp_client.get_all_tools()
        if not all_tools:
            print("❌ No tools found in MCP client")
            return 0
        
        # Load existing config if any
        self.load_config()
        
        count = 0
        for tool_name, tool in all_tools.items():
            if self.register_tool(tool_name, tool):
                count += 1
        
        # Save the updated config
        self.save_config()
        
        print(f"✅ Registered {count} tools from MCP client")
        return count
    
    def register_tool(self, name: str, tool_info: Dict[str, Any]) -> bool:
        """Register a single tool"""
        try:
            # Add tool metadata
            self.tool_metadata[name] = {
                "name": name,
                "description": tool_info.get("description", ""),
                "server": tool_info.get("server", "unknown"),
                "schema": tool_info.get("schema", {})
            }
            
            # Enable the tool by default
            self.enabled_tools[name] = True
            
            # Categorize the tool based on name and server
            self._categorize_tool(name, tool_info)
            
            return True
            
        except Exception as e:
            print(f"❌ Error registering tool {name}: {e}")
            return False
    
    def _categorize_tool(self, name: str, tool_info: Dict[str, Any]):
        """Categorize a tool based on its name, description, and server"""
        # Initialize categories if not already done
        if not self.tool_categories:
            self.tool_categories = {
                "browser": [],
                "devops": [],
                "filesystem": [],
                "search": [],
                "utility": [],
                "other": []
            }
        
        # Determine category based on tool name, description and server
        server = tool_info.get("server", "").lower()
        description = tool_info.get("description", "").lower()
        name_lower = name.lower()
        
        # Check if already categorized
        is_categorized = False
        for category, tools in self.tool_categories.items():
            if name in tools:
                is_categorized = True
                break
        
        if is_categorized:
            return
        
        # Categorize based on patterns
        if any(x in name_lower for x in ["browser", "playwright"]) or "playwright" in server:
            self.add_tool_to_category(name, "browser")
        elif any(x in name_lower for x in ["devops", "azure"]) or "azure-devops" in server:
            self.add_tool_to_category(name, "devops")
        elif any(x in name_lower for x in ["file", "dir", "path"]) or "filesystem" in server:
            self.add_tool_to_category(name, "filesystem")
        elif any(x in name_lower for x in ["search", "find", "query"]) or "search" in server:
            self.add_tool_to_category(name, "search")
        elif any(x in name_lower for x in ["util", "format", "convert", "parse"]):
            self.add_tool_to_category(name, "utility")
        else:
            self.add_tool_to_category(name, "other")
    
    def add_tool_to_category(self, tool_name: str, category: str):
        """Add a tool to a specific category"""
        if category not in self.tool_categories:
            self.tool_categories[category] = []
        
        if tool_name not in self.tool_categories[category]:
            self.tool_categories[category].append(tool_name)
    
    def remove_tool_from_category(self, tool_name: str, category: str):
        """Remove a tool from a specific category"""
        if category in self.tool_categories and tool_name in self.tool_categories[category]:
            self.tool_categories[category].remove(tool_name)
    
    def get_tool_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool metadata by name"""
        return self.tool_metadata.get(name)
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all tools in a category"""
        if category not in self.tool_categories:
            return []
        
        tools = []
        for tool_name in self.tool_categories[category]:
            tool = self.get_tool_by_name(tool_name)
            if tool:
                tools.append(tool)
        
        return tools
    
    def get_all_categories(self) -> List[str]:
        """Get all category names"""
        return list(self.tool_categories.keys())
    
    def get_category_tools_count(self) -> Dict[str, int]:
        """Get the count of tools in each category"""
        return {category: len(tools) for category, tools in self.tool_categories.items()}
    
    def is_tool_enabled(self, name: str) -> bool:
        """Check if a tool is enabled"""
        return self.enabled_tools.get(name, False)
    
    def enable_tool(self, name: str) -> bool:
        """Enable a specific tool"""
        if name in self.tool_metadata:
            self.enabled_tools[name] = True
            return True
        return False
    
    def disable_tool(self, name: str) -> bool:
        """Disable a specific tool"""
        if name in self.tool_metadata:
            self.enabled_tools[name] = False
            return True
        return False
    
    def get_enabled_tools(self) -> List[str]:
        """Get list of all enabled tools"""
        return [name for name, enabled in self.enabled_tools.items() if enabled]
    
    def filter_tools(self, **filters) -> List[Dict[str, Any]]:
        """
        Filter tools based on various criteria
        
        Args:
            filters: Keyword arguments for filtering, such as:
                - category: Filter by category name
                - server: Filter by server name
                - enabled: Filter by enabled status
                - name_pattern: Regex pattern to match tool names
                - description_pattern: Regex pattern to match descriptions
        
        Returns:
            List of tool metadata dictionaries that match the filters
        """
        tools = []
        
        # Start with all tools
        tool_names = list(self.tool_metadata.keys())
        
        # Filter by category
        if "category" in filters:
            category = filters["category"]
            if category in self.tool_categories:
                tool_names = [name for name in tool_names if name in self.tool_categories[category]]
        
        # Filter by server
        if "server" in filters:
            server = filters["server"]
            tool_names = [name for name in tool_names if 
                         self.tool_metadata.get(name, {}).get("server") == server]
        
        # Filter by enabled status
        if "enabled" in filters:
            enabled = filters["enabled"]
            tool_names = [name for name in tool_names if self.enabled_tools.get(name, False) == enabled]
        
        # Filter by name pattern
        if "name_pattern" in filters:
            pattern = filters["name_pattern"]
            tool_names = [name for name in tool_names if re.search(pattern, name, re.IGNORECASE)]
        
        # Filter by description pattern
        if "description_pattern" in filters:
            pattern = filters["description_pattern"]
            tool_names = [name for name in tool_names if 
                         re.search(pattern, self.tool_metadata.get(name, {}).get("description", ""), re.IGNORECASE)]
        
        # Get metadata for matching tools
        for name in tool_names:
            if name in self.tool_metadata:
                tools.append(self.tool_metadata[name])
        
        return tools
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Search for tools matching a query string in name or description"""
        query = query.lower()
        tools = []
        
        for name, metadata in self.tool_metadata.items():
            description = metadata.get("description", "").lower()
            if query in name.lower() or query in description:
                tools.append(metadata)
        
        return tools
