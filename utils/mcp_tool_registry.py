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
    
    # Tool categorization patterns
    CATEGORY_PATTERNS = {
        "browser": [
            r"browser_", r"playwright", r"click", r"type", r"navigate", 
            r"screenshot", r"tab", r"hover", r"select"
        ],
        "devops": [
            r"azure", r"devops", r"work_item", r"pull_request", r"repository",
            r"pipeline", r"build", r"deploy"
        ],
        "filesystem": [
            r"file", r"directory", r"folder", r"path", r"read", r"write", 
            r"create", r"delete", r"list"
        ],
        "search": [
            r"search", r"find", r"query", r"lookup", r"discover"
        ],
        "utility": [
            r"util", r"format", r"convert", r"parse", r"transform"
        ]
    }
    
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
    
    def auto_categorize_tool(self, tool_name: str, tool_description: str = None) -> str:
        """Automatically categorize a tool based on its name and description"""
        name_lower = tool_name.lower()
        desc_lower = tool_description.lower() if tool_description else ""
        
        # Try to match against category patterns
        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, name_lower) or (desc_lower and re.search(pattern, desc_lower)):
                    return category
        
        # Default category if no match found
        return "other"
    
    def register_tool_with_category(self, tool_name: str, metadata: Dict[str, Any], 
                                   category: str = None) -> str:
        """Register a tool with a category"""
        # Auto-categorize if no category provided
        if not category:
            category = self.auto_categorize_tool(tool_name, metadata.get("description", ""))
        
        # Add to metadata
        self.tool_metadata[tool_name] = metadata
        self.enabled_tools[tool_name] = True
        
        # Add to category
        if category not in self.tool_categories:
            self.tool_categories[category] = []
        
        if tool_name not in self.tool_categories[category]:
            self.tool_categories[category].append(tool_name)
            
        return category
    
    def register_from_mcp_client(self) -> int:
        """Register tools from the MCP client"""
        try:
            # Load the config first
            self.load_config()
            
            # Get all tools from the MCP client
            all_tools = self.mcp_client.get_all_tools()
            
            # Register each tool
            for tool_name, tool_info in all_tools.items():
                # Skip tools that are explicitly disabled
                if tool_name in self.enabled_tools and not self.enabled_tools[tool_name]:
                    print(f"⏭️ Skipping disabled tool: {tool_name}")
                    continue
                
                # Store tool metadata
                self.tool_metadata[tool_name] = tool_info
                
                # Set tool as enabled by default
                if tool_name not in self.enabled_tools:
                    self.enabled_tools[tool_name] = True
                
                # Auto-categorize the tool if not already categorized
                server_name = tool_info.get("server", "unknown")
                tool_description = tool_info.get("description", "")
                
                # Check if the tool is already in a category
                categorized = False
                for category, tools in self.tool_categories.items():
                    if tool_name in tools:
                        categorized = True
                        break
                
                # If not categorized, auto-categorize based on name/description
                if not categorized:
                    category = self.auto_categorize_tool(tool_name, tool_description)
                    if category not in self.tool_categories:
                        self.tool_categories[category] = []
                    if tool_name not in self.tool_categories[category]:
                        self.tool_categories[category].append(tool_name)
            
            # Save the config
            self.save_config()
            
            return len(all_tools)
            
        except Exception as e:
            print(f"❌ Error registering tools from MCP client: {e}")
            return 0
    
    def register_tool(self, name: str, tool_info: Dict[str, Any]) -> bool:
        """Register a single tool"""
        try:
            # Add tool metadata
            metadata = {
                "name": name,
                "description": tool_info.get("description", ""),
                "server": tool_info.get("server", "unknown"),
                "schema": tool_info.get("schema", {})
            }
            
            # Auto-categorize the tool
            category = self.auto_categorize_tool(name, metadata["description"])
            self.register_tool_with_category(name, metadata, category)
            
            # Enable the tool by default
            self.enabled_tools[name] = True
            
            return True
            
        except Exception as e:
            print(f"❌ Error registering tool {name}: {e}")
            return False
    
    def get_tool_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool metadata by name"""
        return self.tool_metadata.get(name)
    
    def find_tool_by_pattern(self, pattern: str) -> List[str]:
        """Find tools matching a regex pattern"""
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            return [name for name in self.tool_metadata.keys() 
                    if regex.search(name)]
        except:
            return []
    
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
                - pattern: Filter by name pattern
                - enabled: Filter by enabled status
                - server: Filter by server name
        """
        tools = list(self.tool_metadata.values())
        
        # Apply category filter
        if "category" in filters:
            category = filters["category"]
            if category in self.tool_categories:
                tool_names = self.tool_categories[category]
                tools = [t for t in tools if t["name"] in tool_names]
        
        # Apply pattern filter
        if "pattern" in filters:
            pattern = filters["pattern"]
            try:
                regex = re.compile(pattern, re.IGNORECASE)
                tools = [t for t in tools if regex.search(t["name"]) or regex.search(t.get("description", ""))]
            except:
                pass
        
        # Apply enabled filter
        if "enabled" in filters:
            enabled = filters["enabled"]
            tools = [t for t in tools if self.is_tool_enabled(t["name"]) == enabled]
        
        # Apply server filter
        if "server" in filters:
            server = filters["server"]
            tools = [t for t in tools if t.get("server") == server]
        
        return tools
    
    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all tool metadata"""
        return self.tool_metadata
    
    def get_tools_for_agent(self) -> Dict[str, Dict[str, Any]]:
        """Get all enabled tools for agent consumption"""
        return {name: tool for name, tool in self.tool_metadata.items() 
                if self.is_tool_enabled(name)}
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Search tools by query text"""
        if not query:
            return []
        
        query_lower = query.lower()
        results = []
        
        for name, tool in self.tool_metadata.items():
            score = 0
            name_lower = name.lower()
            desc_lower = tool.get("description", "").lower()
            
            # Exact name match gets highest score
            if name_lower == query_lower:
                score += 100
            # Name contains query
            elif query_lower in name_lower:
                score += 50
            # Description contains query
            elif query_lower in desc_lower:
                score += 20
            
            # Calculate token-based similarity
            query_tokens = query_lower.split()
            name_tokens = name_lower.split("_")
            desc_tokens = desc_lower.split()
            
            for token in query_tokens:
                if token in name_tokens:
                    score += 5
                
                for desc_token in desc_tokens:
                    if token == desc_token:
                        score += 2
                    elif token in desc_token:
                        score += 1
            
            if score > 0:
                tool["score"] = score
                results.append(tool)
        
        # Sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Remove score field
        for result in results:
            if "score" in result:
                del result["score"]
        
        return results

    def register_from_mcp_client(self) -> int:
        """Register tools from the MCP client"""
        try:
            # Load the config first
            self.load_config()
            
            # Get all tools from the MCP client
            all_tools = self.mcp_client.get_all_tools()
            
            # Register each tool
            for tool_name, tool_info in all_tools.items():
                # Skip tools that are explicitly disabled
                if tool_name in self.enabled_tools and not self.enabled_tools[tool_name]:
                    print(f"⏭️ Skipping disabled tool: {tool_name}")
                    continue
                
                # Store tool metadata
                self.tool_metadata[tool_name] = tool_info
                
                # Set tool as enabled by default
                if tool_name not in self.enabled_tools:
                    self.enabled_tools[tool_name] = True
                
                # Auto-categorize the tool if not already categorized
                server_name = tool_info.get("server", "unknown")
                tool_description = tool_info.get("description", "")
                
                # Check if the tool is already in a category
                categorized = False
                for category, tools in self.tool_categories.items():
                    if tool_name in tools:
                        categorized = True
                        break
                
                # If not categorized, auto-categorize based on name/description
                if not categorized:
                    category = self.auto_categorize_tool(tool_name, tool_description)
                    if category not in self.tool_categories:
                        self.tool_categories[category] = []
                    if tool_name not in self.tool_categories[category]:
                        self.tool_categories[category].append(tool_name)
            
            # Save the config
            self.save_config()
            
            return len(all_tools)
            
        except Exception as e:
            print(f"❌ Error registering tools from MCP client: {e}")
            return 0