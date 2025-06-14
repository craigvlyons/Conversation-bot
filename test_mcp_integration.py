#!/usr/bin/env python3
"""
Test script for MCP tool integration.
This script tests the end-to-end flow of MCP tool discovery and execution.
"""
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.mcp_server_manager import MCPServerManager
from utils.mcp_client import MCPClient
from utils.mcp_tool_registry import MCPToolRegistry
from agents.mcp_agent import MCPAgent
from agents.registry import AgentRegistry
from utils.mcp_agent_integration import get_mcp_integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_mcp_integration():
    """Test the complete MCP integration flow"""
    logger.info("=== Testing MCP Integration ===")
    
    try:
        # 1. Test MCP server connection
        logger.info("1. Testing MCP server connection...")
        server_manager = MCPServerManager()
        logger.info(f"Loaded {len(server_manager.servers)} servers from config")
        
        # Quick connection test (with short timeout)
        server_manager.connect_to_servers(timeout=5)
        connected_count = len(server_manager.connected_servers)
        logger.info(f"Connected to {connected_count} MCP servers")
        
        if connected_count == 0:
            logger.warning("No MCP servers connected. Check your configuration.")
            return False
        
        # 2. Test tool discovery
        logger.info("2. Testing tool discovery...")
        mcp_client = MCPClient(server_manager.servers)
        tool_registry = MCPToolRegistry(mcp_client)
        
        tool_count = tool_registry.register_from_mcp_client()
        logger.info(f"Discovered {tool_count} tools")
        
        all_tools = mcp_client.get_all_tools()
        logger.info(f"Available tools: {list(all_tools.keys())}")
        
        if not all_tools:
            logger.warning("No tools discovered from MCP servers")
            return False
        
        # 3. Test MCP agent creation
        logger.info("3. Testing MCP agent creation...")
        mcp_agent = MCPAgent("test_agent", server_manager, tool_registry)
        mcp_tools = mcp_agent.get_all_mcp_tools()
        logger.info(f"MCP agent has {len(mcp_tools)} tools")
        
        # 4. Test integration setup
        logger.info("4. Testing integration setup...")
        integration = get_mcp_integration()
        integration.set_mcp_executor(mcp_agent.execute_mcp_tool)
        logger.info("MCP integration configured")
        
        # 5. Test tool execution (if we have tools)
        if mcp_tools:
            logger.info("5. Testing tool execution...")
            first_tool = list(mcp_tools.keys())[0]
            logger.info(f"Testing execution of tool: {first_tool}")
            
            try:
                # Test with empty parameters for now
                result = await mcp_agent.execute_mcp_tool(first_tool, {})
                logger.info(f"Tool execution result: {result}")
                
                if isinstance(result, dict) and result.get('error'):
                    logger.warning(f"Tool execution returned error: {result['error']}")
                else:
                    logger.info("Tool execution succeeded")
                    
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # 6. Test agent registration
        logger.info("6. Testing agent registration...")
        AgentRegistry.register("test_mcp", mcp_agent)
        registered_agent = AgentRegistry.get("test_mcp")
        
        if registered_agent:
            logger.info("Agent registration successful")
        else:
            logger.error("Agent registration failed")
            return False
        
        logger.info("=== MCP Integration Test Completed Successfully ===")
        return True
        
    except Exception as e:
        logger.error(f"MCP integration test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    finally:
        # Clean up
        try:
            if 'server_manager' in locals() and server_manager:
                await server_manager.stop_all_servers()
                logger.info("Cleaned up MCP servers")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

async def test_agent_tool_integration():
    """Test that agents can properly detect and use MCP tools"""
    logger.info("=== Testing Agent Tool Integration ===")
    
    try:
        # Import agents
        from agents.gemini_agent import GeminiAIAgent
        from utils.constants import GEMINI_KEY
        
        if not GEMINI_KEY:
            logger.warning("GEMINI_KEY not set, skipping agent integration test")
            return True
        
        # Create a test agent
        agent = GeminiAIAgent(api_key=GEMINI_KEY)
        
        # Add some mock MCP tools
        mock_tools = {
            "test_tool": {
                "description": "A test tool for browser automation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to navigate to"}
                    }
                }
            }
        }
        
        # Register tools
        for tool_name, tool_info in mock_tools.items():
            agent.register_mcp_tool(tool_name, tool_info)
        
        agent.enable_mcp()
        
        # Test tool trigger detection
        test_inputs = [
            "open google.com",
            "take a screenshot", 
            "navigate to example.com",
            "what tools are available",
            "hello world"  # This should not trigger tools
        ]
        
        for test_input in test_inputs:
            trigger = agent.check_for_mcp_tool_trigger(test_input)
            logger.info(f"Input: '{test_input}' -> Tool trigger: {trigger}")
        
        logger.info("Agent tool integration test completed")
        return True
        
    except Exception as e:
        logger.error(f"Agent tool integration test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Main test function"""
    logger.info("Starting MCP Integration Tests")
    
    # Test 1: Basic MCP integration
    test1_result = await test_mcp_integration()
    
    # Test 2: Agent tool integration
    test2_result = await test_agent_tool_integration()
    
    # Summary
    logger.info("=== Test Summary ===")
    logger.info(f"MCP Integration Test: {'PASS' if test1_result else 'FAIL'}")
    logger.info(f"Agent Tool Integration Test: {'PASS' if test2_result else 'FAIL'}")
    
    overall_result = test1_result and test2_result
    logger.info(f"Overall Result: {'PASS' if overall_result else 'FAIL'}")
    
    return 0 if overall_result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)