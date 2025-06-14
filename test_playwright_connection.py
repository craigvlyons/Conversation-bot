#!/usr/bin/env python3
"""
Quick test for Playwright MCP server connection specifically.
"""
import sys
import os
import logging
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.mcp_server_manager import MCPServerManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_playwright_connection():
    """Test just the Playwright MCP connection"""
    logger.info("=== Testing Playwright MCP Connection ===")
    
    try:
        # Create server manager
        server_manager = MCPServerManager()
        
        # Check if playwright is configured
        if "playwright" not in server_manager.servers:
            logger.error("Playwright server not found in configuration")
            return False
        
        playwright_server = server_manager.servers["playwright"]
        logger.info(f"Playwright server config: {playwright_server}")
        
        # Try to connect
        logger.info("Attempting to connect to Playwright server...")
        result = server_manager._connect_to_server(playwright_server)
        
        if result:
            logger.info("✅ Successfully connected to Playwright!")
            logger.info(f"Server URL: {playwright_server.url}")
            logger.info(f"Process PID: {playwright_server.process.pid if playwright_server.process else 'None'}")
            
            # Check if process is still running
            if playwright_server.process:
                if playwright_server.process.poll() is None:
                    logger.info("✅ Playwright process is running")
                else:
                    logger.warning("⚠️ Playwright process has exited")
            
            return True
        else:
            logger.error("❌ Failed to connect to Playwright")
            return False
            
    except Exception as e:
        logger.error(f"Error testing Playwright connection: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    finally:
        # Clean up
        try:
            if 'server_manager' in locals():
                import asyncio
                asyncio.run(server_manager.stop_all_servers())
                logger.info("Cleaned up servers")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    success = test_playwright_connection()
    print(f"\nTest Result: {'PASS' if success else 'FAIL'}")
    sys.exit(0 if success else 1)