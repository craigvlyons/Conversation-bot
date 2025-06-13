"""
Tests for MCP tools configuration and loading
"""

import asyncio
import json
import logging
import os
import sys
import unittest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.mcp_tool_registry import MCPToolRegistry

class TestMCPTools(unittest.TestCase):
    """Test cases for MCP tools functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.registry = MCPToolRegistry.get_instance()
    
    def test_config_file_exists(self):
        """Test that MCP tools config file exists"""
        config_path = os.path.join("config", "mcp_tools.json")
        self.assertTrue(os.path.exists(config_path), f"Config file not found: {config_path}")
    
    def test_config_file_valid_json(self):
        """Test that MCP tools config file is valid JSON"""
        config_path = os.path.join("config", "mcp_tools.json")
        try:
            with open(config_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            self.fail(f"Config file is not valid JSON: {e}")
    
    def test_config_has_required_sections(self):
        """Test that MCP tools config has required sections"""
        config_path = os.path.join("config", "mcp_tools.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.assertIn("servers", config, "Config is missing 'servers' section")
        self.assertIn("tools", config, "Config is missing 'tools' section")
    
    def test_registry_load_tools(self):
        """Test that registry loads tools from config"""
        tools = self.registry.get_tools()
        self.assertIsNotNone(tools, "Registry should return a tools list")
    
    def test_tool_health_check(self):
        """Test tool health check functionality"""
        # This is an async operation - we'll need to run it in the event loop
        loop = asyncio.get_event_loop()
        health_results = loop.run_until_complete(self.registry.check_tool_health())
        
        self.assertIsNotNone(health_results, "Health check should return results")
        # We don't assert they're healthy as they may not be running during tests

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
