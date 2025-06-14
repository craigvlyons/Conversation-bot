#!/usr/bin/env python3
"""
Test script specifically for MCP tool discovery.
Tests the complete flow from server connection to tool discovery.
"""

import json
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.mcp_server_manager import MCPServerManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_tool_discovery():
    """Test tool discovery from Azure DevOps MCP server"""
    logger.info("=== Testing Tool Discovery ===")
    
    try:
        # Create server manager and connect
        server_manager = MCPServerManager()
        logger.info(f"Loaded {len(server_manager.servers)} servers from config")
        
        # Connect to servers
        server_manager.connect_to_servers(timeout=10)
        connected_count = len(server_manager.connected_servers)
        logger.info(f"Connected to {connected_count} MCP servers")
        
        if connected_count == 0:
            logger.error("No servers connected - cannot test tool discovery")
            return False
        
        # Show connected servers
        for server_id, server in server_manager.connected_servers.items():
            logger.info(f"  Connected: {server_id} (URL: {server.url})")
        
        # Discover capabilities and tools
        logger.info("Discovering server capabilities...")
        server_manager.discover_capabilities()
        
        # Check if tools were discovered
        total_tools = 0
        for server_id, server in server_manager.connected_servers.items():
            tool_count = len(server.tools) if server.tools else 0
            total_tools += tool_count
            logger.info(f"  {server_id}: {tool_count} tools")
            
            if server.tools:
                for tool_name, tool_info in server.tools.items():
                    description = tool_info.get('description', 'No description')
                    logger.info(f"    - {tool_name}: {description}")
        
        logger.info(f"Total tools discovered: {total_tools}")
        
        if total_tools > 0:
            logger.info("✅ Tool discovery PASSED")
            return True
        else:
            logger.error("❌ Tool discovery FAILED - no tools found")
            return False
            
    except Exception as e:
        logger.error(f"Error during tool discovery test: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        # Cleanup
        try:
            if 'server_manager' in locals():
                import asyncio
                asyncio.run(server_manager.stop_all_servers())
                logger.info("Cleaned up servers")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    success = test_tool_discovery()
    print(f"\nTest Result: {'PASS' if success else 'FAIL'}")
    sys.exit(0 if success else 1)