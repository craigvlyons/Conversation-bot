"""
Domain Expertise Injection System
Automatically enhances any agent with domain-specific knowledge based on available MCP tools.
"""

import logging
from typing import Dict, List, Optional, Any, Type, Callable
from dataclasses import dataclass
from agents.base_agent import BaseAgent
from agents.dynamic_specialized_agent import DomainExpertise
from utils.tool_manager import ToolManager, MCPTool

logger = logging.getLogger(__name__)

@dataclass 
class ExpertiseInjection:
    """Represents an expertise injection into an agent."""
    agent_name: str
    domain: DomainExpertise
    injection_method: str
    confidence: float
    timestamp: float

class DomainExpertiseInjector:
    """
    System that can inject domain expertise into any agent dynamically.
    Creates specialized capabilities without modifying the base agent.
    """
    
    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager
        self.active_injections: Dict[str, List[ExpertiseInjection]] = {}
        self.expertise_templates: Dict[str, Dict[str, Any]] = {}
        
    async def analyze_and_inject_expertise(self, agent: BaseAgent) -> List[ExpertiseInjection]:
        """
        Analyze available tools and inject relevant domain expertise into an agent.
        """
        logger.info(f"🧠 Analyzing expertise injection for agent: {agent.name}")
        
        # Get available tools
        all_tools = self.tool_manager.get_all_tools()
        if not all_tools:
            logger.warning("No tools available for expertise injection")
            return []
        
        # Discover potential domains
        domains = await self._discover_domains_for_agent(agent, all_tools)
        
        injections = []
        for domain in domains:
            injection = await self._inject_domain_expertise(agent, domain)
            if injection:
                injections.append(injection)
        
        # Store injections
        self.active_injections[agent.name] = injections
        
        logger.info(f"✅ Injected {len(injections)} domain expertises into {agent.name}")
        return injections
    
    async def _discover_domains_for_agent(self, agent: BaseAgent, tools: Dict[str, MCPTool]) -> List[DomainExpertise]:
        """Discover which domains are relevant for this specific agent."""
        
        # For now, consider all available domains relevant
        # Could be enhanced to analyze agent's existing capabilities, name, etc.
        
        from agents.dynamic_specialized_agent import DynamicSpecializedAgent
        temp_specialist = DynamicSpecializedAgent(self.tool_manager, name="temp_analyzer")
        domains = await temp_specialist.initialize_domain_expertise()
        
        return list(domains.values())
    
    async def _inject_domain_expertise(self, agent: BaseAgent, domain: DomainExpertise) -> Optional[ExpertiseInjection]:
        """Inject specific domain expertise into an agent."""
        try:
            # Method 1: Enhance agent's MCP tools with domain context
            self._inject_contextualized_tools(agent, domain)
            
            # Method 2: Add domain-specific response enhancement
            self._inject_response_enhancement(agent, domain)
            
            # Method 3: Add domain-specific prompt templates
            self._inject_prompt_templates(agent, domain)
            
            injection = ExpertiseInjection(
                agent_name=agent.name,
                domain=domain,
                injection_method="multi_layer",
                confidence=domain.confidence_score,
                timestamp=__import__('time').time()
            )
            
            logger.info(f"✅ Injected {domain.domain_name} expertise into {agent.name}")
            return injection
            
        except Exception as e:
            logger.error(f"Failed to inject {domain.domain_name} into {agent.name}: {e}")
            return None
    
    def _inject_contextualized_tools(self, agent: BaseAgent, domain: DomainExpertise):
        """Add domain-contextualized tool information to the agent."""
        
        # Create domain-specific tool descriptions
        for tool in domain.tools:
            contextualized_description = f"[{domain.domain_name}] {tool.description}"
            
            # Enhanced tool metadata with domain context
            domain_metadata = {
                **tool.metadata,
                'domain': domain.domain_name,
                'domain_keywords': list(domain.keywords),
                'specialization_context': f"This is a {domain.domain_name} tool for {', '.join(list(domain.keywords)[:3])}"
            }
            
            # Register with enhanced context
            agent.register_mcp_tool(tool.name, {
                'description': contextualized_description,
                'schema': tool.schema,
                'server_id': tool.server_id,
                'metadata': domain_metadata
            })
    
    def _inject_response_enhancement(self, agent: BaseAgent, domain: DomainExpertise):
        """Enhance agent's response generation with domain awareness."""
        
        # Store original get_response method
        if not hasattr(agent, '_original_get_response'):
            agent._original_get_response = agent.get_response
        
        # Create domain-enhanced response method
        async def domain_enhanced_response(user_input: str, history: Optional[str] = None):
            # Check if this request matches the domain
            user_keywords = self._extract_keywords_from_text(user_input)
            domain_relevance = len(user_keywords & domain.keywords) / max(len(user_keywords), 1)
            
            if domain_relevance > 0.3:  # 30% keyword match threshold
                # Add domain context to the response
                domain_context = f"\n\n🎯 **{domain.domain_name} Context**: I have specialized knowledge in {', '.join(list(domain.keywords)[:5])} with {len(domain.tools)} tools available."
                
                # Get original response
                original_response = await agent._original_get_response(user_input, history)
                
                # Enhance with domain context
                return f"{original_response}{domain_context}"
            else:
                # Use original response for non-domain requests
                return await agent._original_get_response(user_input, history)
        
        # Replace agent's get_response method
        agent.get_response = domain_enhanced_response
    
    def _inject_prompt_templates(self, agent: BaseAgent, domain: DomainExpertise):
        """Add domain-specific prompt templates for better responses."""
        
        # Create domain-specific templates
        templates = {
            'domain_intro': f"I specialize in {domain.domain_name} with expertise in {', '.join(list(domain.keywords)[:5])}.",
            'tool_suggestion': f"For {domain.domain_name} tasks, I can help with: {', '.join([tool.name for tool in domain.tools[:3]])}",
            'domain_capabilities': f"My {domain.domain_name} capabilities include {len(domain.tools)} tools for {', '.join(list(domain.keywords)[:3])}"
        }
        
        # Store templates in agent
        if not hasattr(agent, 'domain_templates'):
            agent.domain_templates = {}
        
        agent.domain_templates[domain.domain_name] = templates
    
    def _extract_keywords_from_text(self, text: str) -> set:
        """Extract keywords from text (reused from DynamicSpecializedAgent)."""
        words = text.lower().replace('_', ' ').replace('-', ' ').split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return {word for word in words if len(word) > 2 and word not in stop_words}
    
    def get_injection_status(self, agent_name: str) -> Dict[str, Any]:
        """Get the current injection status for an agent."""
        injections = self.active_injections.get(agent_name, [])
        
        return {
            'agent_name': agent_name,
            'total_injections': len(injections),
            'domains': [inj.domain.domain_name for inj in injections],
            'average_confidence': sum(inj.confidence for inj in injections) / len(injections) if injections else 0,
            'injection_details': [
                {
                    'domain': inj.domain.domain_name,
                    'confidence': inj.confidence,
                    'tools_count': len(inj.domain.tools),
                    'method': inj.injection_method
                }
                for inj in injections
            ]
        }
    
    async def remove_expertise_injection(self, agent: BaseAgent, domain_name: str) -> bool:
        """Remove a specific domain expertise injection from an agent."""
        try:
            injections = self.active_injections.get(agent.name, [])
            
            # Find and remove the injection
            updated_injections = [inj for inj in injections if inj.domain.domain_name != domain_name]
            
            if len(updated_injections) < len(injections):
                self.active_injections[agent.name] = updated_injections
                
                # Restore original response method if no more injections
                if not updated_injections and hasattr(agent, '_original_get_response'):
                    agent.get_response = agent._original_get_response
                    delattr(agent, '_original_get_response')
                
                logger.info(f"✅ Removed {domain_name} expertise from {agent.name}")
                return True
            else:
                logger.warning(f"Domain {domain_name} not found in {agent.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing expertise injection: {e}")
            return False
    
    def get_all_injections(self) -> Dict[str, Any]:
        """Get all active expertise injections across all agents."""
        return {
            'total_agents_enhanced': len(self.active_injections),
            'agents': {
                agent_name: self.get_injection_status(agent_name)
                for agent_name in self.active_injections.keys()
            }
        }

class ExpertiseInjectionManager:
    """
    Higher-level manager for coordinating expertise injections across multiple agents.
    """
    
    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager
        self.injector = DomainExpertiseInjector(tool_manager)
        self.managed_agents: Dict[str, BaseAgent] = {}
    
    async def register_and_enhance_agent(self, agent: BaseAgent) -> List[ExpertiseInjection]:
        """Register an agent and automatically enhance it with relevant expertise."""
        self.managed_agents[agent.name] = agent
        
        # Inject expertise
        injections = await self.injector.analyze_and_inject_expertise(agent)
        
        logger.info(f"🚀 Agent {agent.name} registered and enhanced with {len(injections)} domain expertises")
        return injections
    
    async def refresh_all_expertises(self) -> Dict[str, List[ExpertiseInjection]]:
        """Refresh expertise injections for all managed agents (useful when new tools are added)."""
        results = {}
        
        for agent_name, agent in self.managed_agents.items():
            logger.info(f"🔄 Refreshing expertise for {agent_name}")
            injections = await self.injector.analyze_and_inject_expertise(agent)
            results[agent_name] = injections
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the expertise injection system."""
        return {
            'managed_agents': len(self.managed_agents),
            'total_tools_available': len(self.tool_manager.get_all_tools()),
            'tool_discovery_complete': self.tool_manager.is_discovery_complete(),
            'injections': self.injector.get_all_injections()
        }