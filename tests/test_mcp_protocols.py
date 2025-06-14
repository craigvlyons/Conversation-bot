#!/usr/bin/env python3
"""
Test script for MCP protocol clients and tool discovery.
Tests the new protocol-aware architecture end-to-end.
"""

import asyncio
import logging
import sys
import json
from utils.mcp_server_manager import MCPServerManager
from utils.tool_manager import ToolManager
from utils.mcp_protocol_client import MCPProtocolClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_individual_servers():
    """Test each server individually with protocol detection."""
    print("🧪 Testing Individual MCP Servers")
    print("=" * 50)
    
    # Initialize server manager
    server_manager = MCPServerManager()
    
    # Connect to servers first
    print("🔌 Connecting to MCP servers...")
    server_manager.connect_to_servers()
    
    # Test each connected server
    for server_id, server in server_manager.connected_servers.items():
        print(f"\n📡 Testing server: {server_id}")
        print(f"   URL: {server.url}")
        print(f"   Command: {server.command}")
        
        # Create protocol client and test
        client = MCPProtocolClient(server)
        result = await client.test_connection()
        
        print(f"   Protocol: {result.get('protocol', 'unknown')}")
        print(f"   Connected: {result.get('connected', False)}")
        print(f"   Tools found: {result.get('tools_discovered', 0)}")
        
        if result.get('tools'):
            print(f"   Tool names: {', '.join(result['tools'])}")
        
        if result.get('error'):
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Test completed in {result.get('total_test_time', 0):.2f}s")

async def test_tool_manager():
    """Test the unified ToolManager with protocol-aware discovery."""
    print("\n\n🔧 Testing ToolManager Integration")
    print("=" * 50)
    
    # Initialize components
    server_manager = MCPServerManager()
    
    # Connect to servers first
    print("🔌 Connecting to MCP servers...")
    server_manager.connect_to_servers()
    
    tool_manager = ToolManager(server_manager)
    
    try:
        # Discover all tools
        print("🔍 Starting comprehensive tool discovery...")
        discovered_tools = await tool_manager.discover_all_tools()
        
        print(f"\n✅ Discovery complete!")
        print(f"📊 Total tools discovered: {len(discovered_tools)}")
        
        # Show stats
        stats = tool_manager.get_discovery_stats()
        print(f"📈 Discovery statistics:")
        print(f"   Servers with tools: {stats['servers_with_tools']}/{stats['total_servers']}")
        print(f"   Protocol clients: {stats['protocol_clients']}")
        
        # Show tools by server
        for server_id, tool_count in stats['tools_by_server'].items():
            protocol = stats['client_protocols'].get(server_id, 'unknown')
            print(f"   {server_id}: {tool_count} tools ({protocol} protocol)")
        
        # Show individual tools
        if discovered_tools:
            print(f"\n📋 Discovered tools:")
            for tool_name, tool in discovered_tools.items():
                print(f"   • {tool_name} ({tool.server_id}): {tool.description[:60]}...")
        
        return tool_manager
        
    except Exception as e:
        logger.error(f"ToolManager test failed: {e}")
        return None

async def test_tool_execution(tool_manager: ToolManager):
    """Test tool execution with the new protocol system."""
    print("\n\n⚡ Testing Tool Execution")
    print("=" * 50)
    
    try:
        # Get a tool to test
        discovered_tools = tool_manager.get_all_tools()
        
        if not discovered_tools:
            print("❌ No tools available for execution testing")
            return
        
        # Pick the first tool for testing
        tool_name = list(discovered_tools.keys())[0]
        tool = discovered_tools[tool_name]
        
        print(f"🔧 Testing execution of tool: {tool_name}")
        print(f"   Server: {tool.server_id}")
        print(f"   Description: {tool.description}")
        
        # Test with minimal parameters (this might fail, but should show the pipeline works)
        test_params = {}
        
        from utils.dynamic_tool_handler import DynamicToolHandler
        handler = DynamicToolHandler(tool_manager)
        
        result = await handler.execute_tool(tool_name, test_params)
        
        if result.success:
            print(f"✅ Tool executed successfully!")
            print(f"   Result: {str(result.result)[:100]}...")
        else:
            print(f"⚠️ Tool execution failed (expected for test): {result.error}")
        
        print(f"   Execution time: {result.execution_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Tool execution test failed: {e}")

async def main():
    """Main test function."""
    print("🚀 MCP Protocol Testing Suite")
    print("Testing the new protocol-aware MCP architecture")
    print("=" * 60)
    
    try:
        # Test 1: Individual server protocol detection
        await test_individual_servers()
        
        # Test 2: Unified tool discovery
        tool_manager = await test_tool_manager()
        
        # Test 3: Tool execution (if tools were found)
        if tool_manager and tool_manager.get_all_tools():
            await test_tool_execution(tool_manager)
        
        # Clean up
        if tool_manager:
            await tool_manager.cleanup_clients()
        
        print("\n🎉 Testing complete!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())