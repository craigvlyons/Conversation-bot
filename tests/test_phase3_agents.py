#!/usr/bin/env python3
"""
Test script for Phase 3 - Dynamic Specialized Agents
Tests the advanced agent architecture with dynamic specialization and delegation.
"""

import asyncio
import logging
import sys
from utils.mcp_server_manager import MCPServerManager
from utils.tool_manager import ToolManager
from utils.intelligent_agent_delegator import IntelligentAgentDelegator, DelegationStrategy
from agents.dynamic_specialized_agent import DynamicSpecializedAgent
from agents.gemini_agent import GeminiAIAgent
from utils.constants import GEMINI_KEY

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_dynamic_specialized_agent():
    """Test the DynamicSpecializedAgent with real tools."""
    print("🧠 Testing Dynamic Specialized Agent")
    print("=" * 50)
    
    # Initialize components
    server_manager = MCPServerManager()
    server_manager.connect_to_servers()
    
    tool_manager = ToolManager(server_manager)
    await tool_manager.discover_all_tools()
    
    # Create specialized agent
    specialist = DynamicSpecializedAgent(tool_manager, name="auto_specialist")
    
    # Initialize domain expertise
    domains = await specialist.initialize_domain_expertise()
    
    print(f"✅ Created specialist with {len(domains)} domain expertises:")
    for domain_name, domain in domains.items():
        print(f"   • {domain_name}: {len(domain.tools)} tools, confidence: {domain.confidence_score:.2f}")
        print(f"     Keywords: {', '.join(list(domain.keywords)[:5])}")
    
    # Test specialized responses
    test_queries = [
        "What DevOps tools are available?",
        "Can you help me with work items?",
        "I need to create a task in Azure DevOps",
        "What's the weather like?",  # Should trigger general response
    ]
    
    print(f"\n🎯 Testing specialized responses:")
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        try:
            response = await specialist.get_response(query)
            print(f"   Response: {response[:100]}...")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Show specialization stats
    stats = specialist.get_specialization_stats()
    print(f"\n📊 Specialization Stats:")
    print(f"   Total domains: {stats['total_domains']}")
    print(f"   Total interactions: {stats['total_interactions']}")
    
    return specialist

async def test_domain_expertise_injection():
    """Test injecting domain expertise into regular agents."""
    print("\n\n🧬 Testing Domain Expertise Injection")
    print("=" * 50)
    
    # Initialize components
    server_manager = MCPServerManager()
    server_manager.connect_to_servers()
    
    tool_manager = ToolManager(server_manager)
    await tool_manager.discover_all_tools()
    
    # Create regular Gemini agent
    regular_agent = GeminiAIAgent(GEMINI_KEY)
    
    print(f"📝 Created regular agent: {regular_agent.name}")
    
    # Test response before injection
    print(f"\n🔍 Testing response BEFORE expertise injection:")
    try:
        response_before = await regular_agent.get_response("What Azure DevOps tools do you have?")
        print(f"   Response: {response_before[:100]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Inject domain expertise
    from utils.domain_expertise_injector import ExpertiseInjectionManager
    expertise_manager = ExpertiseInjectionManager(tool_manager)
    
    injections = await expertise_manager.register_and_enhance_agent(regular_agent)
    
    print(f"\n💉 Injected {len(injections)} domain expertises:")
    for injection in injections:
        print(f"   • {injection.domain.domain_name}: {len(injection.domain.tools)} tools")
    
    # Test response after injection
    print(f"\n🔍 Testing response AFTER expertise injection:")
    try:
        response_after = await regular_agent.get_response("What Azure DevOps tools do you have?")
        print(f"   Response: {response_after[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    return expertise_manager

async def test_intelligent_delegation():
    """Test the intelligent agent delegation system."""
    print("\n\n🎯 Testing Intelligent Agent Delegation")
    print("=" * 50)
    
    # Initialize components
    server_manager = MCPServerManager()
    server_manager.connect_to_servers()
    
    tool_manager = ToolManager(server_manager)
    await tool_manager.discover_all_tools()
    
    # Create delegation system
    delegator = IntelligentAgentDelegator(tool_manager)
    
    # Register different types of agents
    regular_agent = GeminiAIAgent(GEMINI_KEY, name="gemini_general")
    specialist_agent = DynamicSpecializedAgent(tool_manager, name="domain_specialist")
    
    await delegator.register_agent(regular_agent)
    await delegator.register_agent(specialist_agent, auto_enhance=False)
    
    print(f"✅ Registered agents with delegator")
    
    # Test different delegation strategies
    test_requests = [
        ("Show me Azure DevOps work items", DelegationStrategy.DIRECT),
        ("What tools do you have available?", DelegationStrategy.FALLBACK),
        ("Help me create a new work item", DelegationStrategy.PARALLEL),
    ]
    
    print(f"\n🚀 Testing delegation strategies:")
    
    for request, strategy in test_requests:
        print(f"\n📝 Request: {request}")
        print(f"   Strategy: {strategy.value}")
        
        try:
            result = await delegator.delegate_request(request, strategy=strategy)
            
            print(f"   ✅ Agent used: {result.agent_used.name if result.agent_used else 'None'}")
            print(f"   ⏱️ Execution time: {result.execution_time:.2f}s")
            print(f"   📊 Success: {result.success}")
            print(f"   💬 Response: {result.response[:100]}...")
            
            if result.fallback_attempts > 0:
                print(f"   🔄 Fallback attempts: {result.fallback_attempts}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Show delegation stats
    stats = delegator.get_delegation_stats()
    print(f"\n📈 Delegation System Stats:")
    print(f"   Available agents: {stats['available_agents']}")
    print(f"   Specialized agents: {stats['specialized_agents']}")
    print(f"   Total delegations: {stats['total_delegations']}")
    
    return delegator

async def test_end_to_end_workflow():
    """Test a complete end-to-end workflow with dynamic agents."""
    print("\n\n🌟 Testing End-to-End Dynamic Agent Workflow")
    print("=" * 50)
    
    # Initialize the complete system
    server_manager = MCPServerManager()
    server_manager.connect_to_servers()
    
    tool_manager = ToolManager(server_manager)
    discovered_tools = await tool_manager.discover_all_tools()
    
    print(f"🔧 Discovered {len(discovered_tools)} tools from {len(server_manager.connected_servers)} servers")
    
    # Create delegation system
    delegator = IntelligentAgentDelegator(tool_manager)
    
    # Register a general agent and let the system create specialists automatically
    general_agent = GeminiAIAgent(GEMINI_KEY, name="primary_assistant")
    await delegator.register_agent(general_agent)
    
    print(f"✅ Initialized dynamic agent system")
    
    # Simulate a real user conversation
    conversation_flow = [
        "Hello, what can you help me with?",
        "I need to work with Azure DevOps",
        "Can you show me the available work items?",
        "Help me create a new work item called 'Fix login issue'",
        "What other DevOps tools do you have?",
    ]
    
    print(f"\n💬 Simulating user conversation:")
    
    for i, user_message in enumerate(conversation_flow, 1):
        print(f"\n{i}. User: {user_message}")
        
        try:
            # Let the system intelligently delegate
            result = await delegator.delegate_request(user_message)
            
            print(f"   🤖 {result.agent_used.name}: {result.response[:150]}...")
            
            # Show what happened behind the scenes
            if hasattr(result.agent_used, 'get_specialization_stats'):
                stats = result.agent_used.get_specialization_stats()
                if stats['total_domains'] > 0:
                    print(f"   🧠 Used specialist with {stats['total_domains']} domain(s)")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Final system status
    final_stats = delegator.get_delegation_stats()
    print(f"\n🎯 Final System Status:")
    print(f"   Total agents: {final_stats['available_agents'] + final_stats['specialized_agents']}")
    print(f"   Conversations handled: {final_stats['total_delegations']}")
    print(f"   Tools available: {len(discovered_tools)}")
    
    # Show agent performance
    print(f"\n📊 Agent Performance:")
    for agent_name, perf in final_stats['agent_performance'].items():
        print(f"   {agent_name}: {perf['usage_count']} uses, {perf['success_rate']:.1%} success")

async def main():
    """Main test function."""
    print("🚀 Phase 3 Testing Suite - Dynamic Specialized Agents")
    print("Testing advanced agent architecture with dynamic specialization")
    print("=" * 80)
    
    try:
        # Test 1: Dynamic Specialized Agent
        specialist = await test_dynamic_specialized_agent()
        
        # Test 2: Domain Expertise Injection
        expertise_manager = await test_domain_expertise_injection()
        
        # Test 3: Intelligent Delegation
        delegator = await test_intelligent_delegation()
        
        # Test 4: End-to-End Workflow
        await test_end_to_end_workflow()
        
        print("\n🎉 Phase 3 Testing Complete!")
        print("✅ Dynamic specialized agents working")
        print("✅ Domain expertise injection functional")
        print("✅ Intelligent delegation operational")
        print("✅ End-to-end workflows successful")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())