#!/usr/bin/env python3
"""
Simple tool discovery test that handles port conflicts automatically.
"""

import subprocess
import time
import sys
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def is_port_in_use(port):
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def test_custom_server():
    """Test our custom Azure DevOps server"""
    logger.info("=== Testing Custom MCP Server ===")
    
    # Check port availability
    if is_port_in_use(8001):
        logger.error("Port 8001 is in use. Please stop any server running on port 8001")
        return False
    
    if is_port_in_use(8000):
        logger.warning("Port 8000 is in use (likely your production server)")
        logger.info("This is fine - we'll use port 8001 for testing")
    
    process = None
    try:
        # Start our custom server
        logger.info("Starting custom Azure DevOps MCP server on port 8001...")
        process = subprocess.Popen(
            [sys.executable, "azure_devops_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it time to start
        time.sleep(3)
        
        # Check if process is running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            logger.error(f"Server failed to start:")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return False
        
        logger.info(f"✅ Server started (PID: {process.pid})")
        
        # Test basic connectivity
        base_url = "http://127.0.0.1:8001"
        
        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Health check passed")
            else:
                logger.error(f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
        
        # Test capabilities endpoint  
        try:
            response = requests.get(f"{base_url}/capabilities", timeout=5)
            if response.status_code == 200:
                capabilities = response.json()
                tools = capabilities.get("tools", {})
                logger.info(f"✅ Capabilities endpoint working: {len(tools)} tools")
                for tool_name in tools:
                    logger.info(f"  - {tool_name}")
            else:
                logger.error(f"Capabilities check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Capabilities check failed: {e}")
            return False
        
        # Test JSON-RPC initialization
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"capabilities": {}}
            }
            response = requests.post(f"{base_url}/jsonrpc", 
                                   json=payload, 
                                   headers={"Content-Type": "application/json"},
                                   timeout=5)
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ JSON-RPC initialization successful")
                logger.info(f"  Server info: {result.get('result', {}).get('serverInfo', {})}")
            else:
                logger.error(f"JSON-RPC init failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"JSON-RPC init failed: {e}")
            return False
        
        # Test tool discovery via JSON-RPC
        try:
            payload = {
                "jsonrpc": "2.0", 
                "id": 2,
                "method": "getTools",
                "params": {}
            }
            response = requests.post(f"{base_url}/jsonrpc",
                                   json=payload,
                                   headers={"Content-Type": "application/json"},
                                   timeout=5)
            if response.status_code == 200:
                result = response.json()
                tools = result.get("result", [])
                logger.info(f"✅ Tool discovery successful: {len(tools)} tools")
                for tool in tools:
                    tool_name = tool.get("name", "unknown")
                    description = tool.get("description", "No description")
                    logger.info(f"  - {tool_name}: {description}")
                
                if len(tools) > 0:
                    logger.info("🎉 TOOL DISCOVERY WORKING!")
                    return True
                else:
                    logger.error("No tools returned from server")
                    return False
            else:
                logger.error(f"Tool discovery failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Tool discovery failed: {e}")
            return False
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False
    finally:
        if process:
            try:
                logger.info("Stopping test server...")
                process.terminate()
                process.wait(timeout=5)
                logger.info("✅ Test server stopped")
            except:
                try:
                    process.kill()
                except:
                    pass

def main():
    logger.info("Simple MCP Tool Discovery Test")
    logger.info("This test uses our custom server on port 8001")
    logger.info("Your production server on port 8000 will not be affected")
    logger.info("")
    
    success = test_custom_server()
    
    print(f"\nTest Result: {'PASS' if success else 'FAIL'}")
    
    if success:
        print("\n🎉 SUCCESS! MCP tool discovery is working correctly!")
        print("✅ Custom server starts properly")
        print("✅ HTTP endpoints respond correctly") 
        print("✅ JSON-RPC protocol works")
        print("✅ Tools are discovered successfully")
        print("\nYour MCP integration is ready!")
    else:
        print("\n❌ Test failed. Check the logs above for details.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())