from typing import Dict, List, Any, Optional, Union, Tuple
import os
import json
import re
import asyncio

class MCPConfigManager:
    """Manager for MCP server configurations"""
    
    def __init__(self, config_path: str = "mcp_servers.json"):
        self.config_path = config_path
        self.config: Dict[str, Dict[str, Any]] = {}
        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if not os.path.exists(self.config_path):
                print(f"Config file not found: {self.config_path}")
                return False
            
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
            
            return True
            
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_server_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific server"""
        return self.config.get(name)
    
    def get_all_server_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get configurations for all servers"""
        return self.config
    
    def add_server_config(self, name: str, config: Dict[str, Any]) -> bool:
        """Add a new server configuration"""
        if not name:
            print("Server name cannot be empty")
            return False
        
        # Validate server name
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            print("Server name can only contain alphanumeric characters, underscore, and hyphen")
            return False
        
        # Validate configuration
        if "description" not in config:
            print("Server configuration must include a description")
            return False
        
        if "url" not in config and "command" not in config:
            print("Server configuration must include either a URL or a command")
            return False
        
        # Add the configuration
        self.config[name] = config
        
        # Save the updated configuration
        return self.save_config()
    
    def update_server_config(self, name: str, config: Dict[str, Any]) -> bool:
        """Update an existing server configuration"""
        if name not in self.config:
            print(f"Server not found: {name}")
            return False
        
        # Update the configuration
        self.config[name].update(config)
        
        # Save the updated configuration
        return self.save_config()
    
    def delete_server_config(self, name: str) -> bool:
        """Delete a server configuration"""
        if name not in self.config:
            print(f"Server not found: {name}")
            return False
        
        # Delete the configuration
        del self.config[name]
        
        # Save the updated configuration
        return self.save_config()
    
    def validate_server_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a server configuration"""
        if "description" not in config:
            return False, "Description is required"
        
        if "url" not in config and "command" not in config:
            return False, "Either URL or command is required"
        
        if "url" in config and not isinstance(config["url"], str):
            return False, "URL must be a string"
        
        if "command" in config and not isinstance(config["command"], str):
            return False, "Command must be a string"
        
        if "args" in config and not isinstance(config["args"], list):
            return False, "Arguments must be a list"
        
        return True, ""
    
    async def test_server_connection(self, name: str) -> Dict[str, Any]:
        """Test connection to a server"""
        if name not in self.config:
            return {"success": False, "error": f"Server not found: {name}"}
        
        config = self.config[name]
        
        # Import here to avoid circular imports
        from utils.mcp_server_manager_old import MCPServerManager, MCPServer
        
        try:
            # Create a temporary server instance
            server = MCPServer(
                name=name,
                url=config.get("url"),
                command=config.get("command"),
                args=config.get("args"),
                description=config.get("description")
            )
            
            # Create a temporary server manager
            server_manager = MCPServerManager()
            
            # Try to connect to the server
            success = await server_manager.connect_server(name)
            
            if not success:
                return {"success": False, "error": "Failed to connect to server"}
            
            # Get server capabilities
            capabilities = {
                "tools": len(server.tools or {}),
                "prompts": len(server.prompts or {}),
                "resources": len(server.resources or {})
            }
            
            # Stop the server
            await server_manager.stop_server(name)
            
            return {
                "success": True,
                "capabilities": capabilities
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
