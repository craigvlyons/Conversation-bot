"""
Dynamic Specialized Agent
Automatically adapts to any tool domain based on available MCP tools.
Creates domain expertise dynamically without hard-coded specializations.
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from agents.base_agent import BaseAgent
from utils.tool_manager import ToolManager, MCPTool
from utils.dynamic_tool_handler import DynamicToolHandler

logger = logging.getLogger(__name__)

@dataclass
class DomainExpertise:
    """Represents dynamically learned domain expertise."""
    domain_name: str
    keywords: Set[str]
    tools: List[MCPTool]
    description_patterns: List[str]
    confidence_score: float
    usage_count: int = 0

class DynamicSpecializedAgent(BaseAgent):
    """
    Agent that automatically specializes in tool domains based on available MCP tools.
    Dynamically builds expertise without hard-coded domain knowledge.
    """
    
    def __init__(self, tool_manager: ToolManager, name: str = "dynamic_specialist"):
        super().__init__(name)
        self.tool_manager = tool_manager
        self.tool_handler = DynamicToolHandler(tool_manager)
        
        # Dynamic domain expertise
        self.discovered_domains: Dict[str, DomainExpertise] = {}
        self.specialization_threshold = 0.7  # Confidence threshold for specialization
        
        # Learning and optimization
        self.interaction_history: List[Dict[str, Any]] = []
        self.domain_performance: Dict[str, Dict[str, float]] = {}
        
        self.enable_mcp()
        
    async def initialize_domain_expertise(self) -> Dict[str, DomainExpertise]:
        """
        Automatically discover and create domain expertise based on available tools.
        """
        logger.info("🧠 Initializing dynamic domain expertise...")
        
        # Get all available tools
        all_tools = self.tool_manager.get_all_tools()
        
        if not all_tools:
            logger.warning("No tools available for domain expertise creation")
            return {}
        
        # Analyze tools to discover domains
        domains = self._analyze_tools_for_domains(all_tools)
        
        # Create expertise for each domain
        for domain_name, domain_data in domains.items():
            expertise = DomainExpertise(
                domain_name=domain_name,
                keywords=domain_data['keywords'],
                tools=domain_data['tools'],
                description_patterns=domain_data['patterns'],
                confidence_score=domain_data['confidence']
            )
            
            self.discovered_domains[domain_name] = expertise
            logger.info(f"✅ Created domain expertise: {domain_name} ({len(domain_data['tools'])} tools)")
        
        logger.info(f"🎯 Specialized in {len(self.discovered_domains)} domains: {list(self.discovered_domains.keys())}")
        return self.discovered_domains
    
    def _analyze_tools_for_domains(self, tools: Dict[str, MCPTool]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze available tools to automatically discover domain specializations.
        """
        domains = {}
        
        # Group tools by server first (servers often represent domains)
        tools_by_server = {}
        for tool_name, tool in tools.items():
            server_id = tool.server_id
            if server_id not in tools_by_server:
                tools_by_server[server_id] = []
            tools_by_server[server_id].append(tool)
        
        # Analyze each server's tools to extract domain expertise
        for server_id, server_tools in tools_by_server.items():
            domain_analysis = self._extract_domain_from_tools(server_id, server_tools)
            if domain_analysis:
                domains[domain_analysis['domain_name']] = domain_analysis
        
        # Look for cross-server patterns (e.g., multiple servers with similar tool types)
        cross_server_domains = self._find_cross_server_domains(tools)
        domains.update(cross_server_domains)
        
        return domains
    
    def _extract_domain_from_tools(self, server_id: str, tools: List[MCPTool]) -> Optional[Dict[str, Any]]:
        """Extract domain characteristics from a group of tools."""
        if not tools:
            return None
        
        # Extract keywords from tool names and descriptions
        all_keywords = set()
        description_patterns = []
        
        for tool in tools:
            # Extract keywords from tool name
            tool_keywords = self._extract_keywords_from_text(tool.name)
            all_keywords.update(tool_keywords)
            
            # Extract keywords from description
            desc_keywords = self._extract_keywords_from_text(tool.description)
            all_keywords.update(desc_keywords)
            
            # Store description patterns
            description_patterns.append(tool.description.lower())
        
        # Determine domain name based on server or tool patterns
        domain_name = self._determine_domain_name(server_id, tools, all_keywords)
        
        # Calculate confidence based on tool coherence
        confidence = self._calculate_domain_confidence(tools, all_keywords)
        
        return {
            'domain_name': domain_name,
            'keywords': all_keywords,
            'tools': tools,
            'patterns': description_patterns,
            'confidence': confidence,
            'server_id': server_id
        }
    
    def _extract_keywords_from_text(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text."""
        # Simple keyword extraction - could be enhanced with NLP
        words = text.lower().replace('_', ' ').replace('-', ' ').split()
        
        # Filter out common words and keep meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = {word for word in words if len(word) > 2 and word not in stop_words}
        
        return keywords
    
    def _determine_domain_name(self, server_id: str, tools: List[MCPTool], keywords: Set[str]) -> str:
        """Determine an appropriate domain name."""
        # Use server ID as base
        domain_name = server_id.replace('-', '_').replace('_', ' ').title()
        
        # Enhance with keyword analysis
        domain_indicators = {
            'devops': ['work', 'item', 'project', 'task', 'issue', 'azure', 'devops'],
            'browser': ['browser', 'page', 'navigate', 'click', 'screenshot', 'playwright'],
            'search': ['search', 'query', 'find', 'results', 'brave'],
            'file': ['file', 'read', 'write', 'directory', 'path'],
            'api': ['api', 'request', 'response', 'http', 'endpoint'],
            'database': ['database', 'query', 'table', 'sql', 'data']
        }
        
        # Find best matching domain
        for domain_type, indicators in domain_indicators.items():
            if any(indicator in keywords for indicator in indicators):
                return f"{domain_type.title()} Specialist"
        
        return f"{domain_name} Specialist"
    
    def _calculate_domain_confidence(self, tools: List[MCPTool], keywords: Set[str]) -> float:
        """Calculate confidence score for domain coherence."""
        if not tools:
            return 0.0
        
        # Factors that increase confidence:
        # 1. Number of tools (more tools = higher confidence)
        tool_count_factor = min(len(tools) / 5.0, 1.0)  # Max at 5 tools
        
        # 2. Keyword consistency across tools
        keyword_consistency = len(keywords) / max(len(tools) * 3, 1)  # Expect ~3 keywords per tool
        keyword_consistency = min(keyword_consistency, 1.0)
        
        # 3. Tool name/description quality
        description_quality = sum(1 for tool in tools if len(tool.description) > 20) / len(tools)
        
        # Combined confidence score
        confidence = (tool_count_factor * 0.4 + keyword_consistency * 0.4 + description_quality * 0.2)
        return min(confidence, 1.0)
    
    def _find_cross_server_domains(self, tools: Dict[str, MCPTool]) -> Dict[str, Dict[str, Any]]:
        """Find domain patterns that span multiple servers."""
        # This could identify patterns like "All HTTP/API tools" or "All file manipulation tools"
        # For now, return empty - could be enhanced later
        return {}
    
    async def get_response(self, user_input: str, history: Optional[str] = None) -> str:
        """
        Provide specialized response based on dynamic domain expertise.
        """
        try:
            # Initialize domain expertise if not done
            if not self.discovered_domains:
                await self.initialize_domain_expertise()
            
            # Determine if this is a specialized request
            relevant_domain = self._identify_relevant_domain(user_input)
            
            if relevant_domain:
                logger.info(f"🎯 Specializing in {relevant_domain.domain_name} for: {user_input}")
                response = await self._handle_specialized_request(user_input, relevant_domain, history)
            else:
                logger.info(f"💬 General conversation request: {user_input}")
                response = await self._handle_general_request(user_input, history)
            
            # Record interaction for learning
            self._record_interaction(user_input, relevant_domain, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in specialized agent response: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _identify_relevant_domain(self, user_input: str) -> Optional[DomainExpertise]:
        """Identify which domain expertise is most relevant to the user input."""
        if not self.discovered_domains:
            return None
        
        user_keywords = self._extract_keywords_from_text(user_input)
        best_match = None
        best_score = 0.0
        
        for domain in self.discovered_domains.values():
            # Calculate keyword overlap
            keyword_overlap = len(user_keywords & domain.keywords)
            keyword_score = keyword_overlap / max(len(user_keywords), 1)
            
            # Check for tool name matches
            tool_name_matches = sum(1 for tool in domain.tools if any(word in tool.name.lower() for word in user_keywords))
            tool_score = tool_name_matches / max(len(domain.tools), 1)
            
            # Combined score
            total_score = (keyword_score * 0.6 + tool_score * 0.4) * domain.confidence_score
            
            if total_score > best_score and total_score > self.specialization_threshold:
                best_score = total_score
                best_match = domain
        
        return best_match
    
    async def _handle_specialized_request(self, user_input: str, domain: DomainExpertise, history: Optional[str]) -> str:
        """Handle request using domain-specific expertise."""
        try:
            # Update usage count
            domain.usage_count += 1
            
            # Try to execute relevant tools
            from utils.dynamic_tool_handler import ToolRouter
            router = ToolRouter(self.tool_manager)
            
            # Bias tool selection towards this domain
            result = await self._execute_domain_specific_tools(user_input, domain, router)
            
            if result and result.success:
                response = f"✅ **{domain.domain_name} Specialist**: {result.result}"
            else:
                # Provide domain-specific guidance
                response = self._generate_domain_guidance(user_input, domain)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in specialized request handling: {e}")
            return self._generate_domain_guidance(user_input, domain)
    
    async def _execute_domain_specific_tools(self, user_input: str, domain: DomainExpertise, router) -> Optional[Any]:
        """Execute tools with domain-specific preference."""
        # Override router's tool selection to prefer domain tools
        domain_tool_names = [tool.name for tool in domain.tools]
        
        # Find best matching tool from domain
        for tool in domain.tools:
            tool_keywords = self._extract_keywords_from_text(f"{tool.name} {tool.description}")
            user_keywords = self._extract_keywords_from_text(user_input)
            
            if tool_keywords & user_keywords:
                # Try executing this tool
                try:
                    result = await self.tool_handler.execute_tool(tool.name, {})
                    if result.success:
                        return result
                except Exception as e:
                    logger.warning(f"Tool execution failed for {tool.name}: {e}")
                    continue
        
        # Fall back to general routing within domain tools
        return await router.route_and_execute(user_input)
    
    def _generate_domain_guidance(self, user_input: str, domain: DomainExpertise) -> str:
        """Generate helpful guidance for domain-specific requests."""
        tool_list = "\n".join([f"• **{tool.name}**: {tool.description}" for tool in domain.tools])
        
        return f"""🤖 **{domain.domain_name}** here! I specialize in {', '.join(list(domain.keywords)[:5])}.

I have access to these tools:
{tool_list}

To help you better, try being more specific about what you'd like to do."""
    
    async def _handle_general_request(self, user_input: str, history: Optional[str]) -> str:
        """Handle general conversation requests."""
        if self.discovered_domains:
            domains_summary = ", ".join([d.domain_name for d in self.discovered_domains.values()])
            return f"""I'm a dynamic specialist with expertise in: {domains_summary}

I can help you with:
{self._get_capabilities_summary()}

What would you like to work on?"""
        else:
            return "I'm ready to help! Let me analyze the available tools to build my expertise."
    
    def _get_capabilities_summary(self) -> str:
        """Get a summary of all capabilities across domains."""
        capabilities = []
        for domain in self.discovered_domains.values():
            domain_caps = f"**{domain.domain_name}**: {len(domain.tools)} tools available"
            capabilities.append(domain_caps)
        
        return "\n".join(capabilities)
    
    def _record_interaction(self, user_input: str, domain: Optional[DomainExpertise], response: str):
        """Record interaction for learning and optimization."""
        interaction = {
            'timestamp': __import__('time').time(),
            'user_input': user_input,
            'domain': domain.domain_name if domain else 'general',
            'response_length': len(response),
            'tools_used': [],  # Could be enhanced to track specific tools
        }
        
        self.interaction_history.append(interaction)
        
        # Keep only recent interactions (last 100)
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
    
    def get_specialization_stats(self) -> Dict[str, Any]:
        """Get statistics about current specializations."""
        stats = {
            'total_domains': len(self.discovered_domains),
            'domains': {},
            'total_interactions': len(self.interaction_history),
            'specialization_threshold': self.specialization_threshold
        }
        
        for domain_name, domain in self.discovered_domains.items():
            stats['domains'][domain_name] = {
                'tools_count': len(domain.tools),
                'confidence': domain.confidence_score,
                'usage_count': domain.usage_count,
                'keywords': list(domain.keywords)[:10]  # First 10 keywords
            }
        
        return stats