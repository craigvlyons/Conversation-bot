"""
Intelligent Agent Delegation System
Automatically detects when specialized agents should handle requests and manages delegation chains.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from agents.base_agent import BaseAgent
from agents.dynamic_specialized_agent import DynamicSpecializedAgent
from utils.domain_expertise_injector import ExpertiseInjectionManager
from utils.tool_manager import ToolManager

logger = logging.getLogger(__name__)

class DelegationStrategy(Enum):
    DIRECT = "direct"  # Direct delegation to best agent
    CHAIN = "chain"    # Chain multiple agents
    PARALLEL = "parallel"  # Run multiple agents in parallel
    FALLBACK = "fallback"  # Try agents in fallback order

@dataclass
class DelegationCandidate:
    """Represents a potential agent delegation target."""
    agent: BaseAgent
    confidence: float
    reasoning: str
    estimated_performance: float
    domain_match: Optional[str] = None

@dataclass
class DelegationResult:
    """Result of an agent delegation."""
    agent_used: BaseAgent
    response: str
    execution_time: float
    success: bool
    strategy_used: DelegationStrategy
    fallback_attempts: int = 0

class IntelligentAgentDelegator:
    """
    System that intelligently delegates requests to the most appropriate agents.
    Automatically detects specialization needs and manages agent orchestration.
    """
    
    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager
        self.expertise_manager = ExpertiseInjectionManager(tool_manager)
        
        # Registered agents
        self.available_agents: Dict[str, BaseAgent] = {}
        self.specialized_agents: Dict[str, DynamicSpecializedAgent] = {}
        
        # Delegation intelligence
        self.delegation_history: List[Dict[str, Any]] = []
        self.agent_performance: Dict[str, Dict[str, float]] = {}
        self.delegation_patterns: Dict[str, List[str]] = {}
        
        # Configuration
        self.confidence_threshold = 0.6
        self.max_delegation_depth = 3
        self.enable_parallel_execution = True
        
    async def register_agent(self, agent: BaseAgent, auto_enhance: bool = True) -> bool:
        """Register an agent with the delegation system."""
        try:
            self.available_agents[agent.name] = agent
            
            # Auto-enhance with domain expertise
            if auto_enhance:
                injections = await self.expertise_manager.register_and_enhance_agent(agent)
                logger.info(f"✅ Registered {agent.name} with {len(injections)} expertise injections")
            else:
                logger.info(f"✅ Registered {agent.name} without auto-enhancement")
            
            # Initialize performance tracking
            self.agent_performance[agent.name] = {
                'success_rate': 1.0,
                'avg_response_time': 1.0,
                'domain_scores': {},
                'usage_count': 0
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent.name}: {e}")
            return False
    
    async def create_specialized_agent(self, domain_hint: Optional[str] = None) -> DynamicSpecializedAgent:
        """Create a new specialized agent on demand."""
        agent_name = f"specialist_{len(self.specialized_agents) + 1}"
        if domain_hint:
            agent_name = f"{domain_hint}_specialist"
        
        specialist = DynamicSpecializedAgent(self.tool_manager, name=agent_name)
        await specialist.initialize_domain_expertise()
        
        self.specialized_agents[agent_name] = specialist
        await self.register_agent(specialist, auto_enhance=False)  # Already specialized
        
        logger.info(f"🚀 Created specialized agent: {agent_name}")
        return specialist
    
    async def delegate_request(self, user_input: str, history: Optional[str] = None, 
                             strategy: DelegationStrategy = DelegationStrategy.DIRECT) -> DelegationResult:
        """
        Intelligently delegate a request to the most appropriate agent(s).
        """
        start_time = __import__('time').time()
        
        try:
            # Analyze request to find best delegation candidates
            candidates = await self._analyze_delegation_candidates(user_input, history)
            
            if not candidates:
                # Create a specialized agent if none are suitable
                specialist = await self.create_specialized_agent()
                candidates = [DelegationCandidate(
                    agent=specialist,
                    confidence=0.8,
                    reasoning="Created new specialist for unhandled request",
                    estimated_performance=0.7
                )]
            
            # Execute delegation based on strategy
            result = await self._execute_delegation(user_input, history, candidates, strategy)
            
            # Record delegation for learning
            self._record_delegation(user_input, result, candidates)
            
            execution_time = __import__('time').time() - start_time
            result.execution_time = execution_time
            
            logger.info(f"✅ Delegation completed in {execution_time:.2f}s using {result.agent_used.name}")
            return result
            
        except Exception as e:
            logger.error(f"Delegation failed: {e}")
            # Fallback to any available agent
            fallback_agent = list(self.available_agents.values())[0] if self.available_agents else None
            if fallback_agent:
                response = await fallback_agent.get_response(user_input, history)
                return DelegationResult(
                    agent_used=fallback_agent,
                    response=response,
                    execution_time=__import__('time').time() - start_time,
                    success=True,
                    strategy_used=DelegationStrategy.FALLBACK,
                    fallback_attempts=1
                )
            else:
                return DelegationResult(
                    agent_used=None,
                    response=f"I'm sorry, I couldn't process your request: {str(e)}",
                    execution_time=__import__('time').time() - start_time,
                    success=False,
                    strategy_used=strategy
                )
    
    async def _analyze_delegation_candidates(self, user_input: str, history: Optional[str] = None) -> List[DelegationCandidate]:
        """Analyze available agents to find the best delegation candidates."""
        candidates = []
        
        # Extract key information from user input
        user_keywords = self._extract_keywords(user_input)
        request_complexity = self._estimate_complexity(user_input)
        
        # Evaluate each available agent
        for agent_name, agent in self.available_agents.items():
            candidate = await self._evaluate_agent_fitness(agent, user_input, user_keywords, request_complexity)
            if candidate:
                candidates.append(candidate)
        
        # Evaluate specialized agents
        for agent_name, agent in self.specialized_agents.items():
            candidate = await self._evaluate_specialist_fitness(agent, user_input, user_keywords)
            if candidate:
                candidates.append(candidate)
        
        # Sort by confidence and estimated performance
        candidates.sort(key=lambda c: c.confidence * c.estimated_performance, reverse=True)
        
        logger.info(f"🎯 Found {len(candidates)} delegation candidates for: {user_input[:50]}...")
        return candidates[:5]  # Top 5 candidates
    
    async def _evaluate_agent_fitness(self, agent: BaseAgent, user_input: str, 
                                    user_keywords: set, complexity: float) -> Optional[DelegationCandidate]:
        """Evaluate how well an agent fits the request."""
        try:
            # Check if agent has relevant MCP tools
            tool_relevance = 0.0
            domain_match = None
            
            if hasattr(agent, 'get_all_mcp_tools'):
                mcp_tools = agent.get_all_mcp_tools()
                if mcp_tools:
                    tool_keywords = set()
                    for tool_name, tool_info in mcp_tools.items():
                        desc = tool_info.get('description', '')
                        tool_keywords.update(self._extract_keywords(f"{tool_name} {desc}"))
                    
                    # Calculate keyword overlap
                    overlap = len(user_keywords & tool_keywords)
                    tool_relevance = overlap / max(len(user_keywords), 1)
                    
                    # Check for domain metadata
                    for tool_name, tool_info in mcp_tools.items():
                        metadata = tool_info.get('metadata', {})
                        if 'domain' in metadata:
                            domain_keywords = set(metadata.get('domain_keywords', []))
                            if user_keywords & domain_keywords:
                                domain_match = metadata['domain']
                                tool_relevance += 0.2  # Bonus for domain match
                                break
            
            # Get agent performance history
            performance = self.agent_performance.get(agent.name, {})
            success_rate = performance.get('success_rate', 0.5)
            avg_time = performance.get('avg_response_time', 1.0)
            
            # Calculate overall confidence
            confidence = (tool_relevance * 0.5 + success_rate * 0.3 + (1.0 - min(avg_time/5.0, 1.0)) * 0.2)
            
            # Only consider agents above threshold
            if confidence < self.confidence_threshold:
                return None
            
            reasoning = f"Tool relevance: {tool_relevance:.2f}, Success rate: {success_rate:.2f}"
            if domain_match:
                reasoning += f", Domain match: {domain_match}"
            
            return DelegationCandidate(
                agent=agent,
                confidence=confidence,
                reasoning=reasoning,
                estimated_performance=success_rate,
                domain_match=domain_match
            )
            
        except Exception as e:
            logger.warning(f"Error evaluating agent {agent.name}: {e}")
            return None
    
    async def _evaluate_specialist_fitness(self, specialist: DynamicSpecializedAgent, 
                                         user_input: str, user_keywords: set) -> Optional[DelegationCandidate]:
        """Evaluate how well a specialized agent fits the request."""
        try:
            # Check domain relevance using specialist's method
            relevant_domain = specialist._identify_relevant_domain(user_input)
            
            if relevant_domain:
                confidence = min(relevant_domain.confidence_score + 0.2, 1.0)  # Bonus for specialization
                
                return DelegationCandidate(
                    agent=specialist,
                    confidence=confidence,
                    reasoning=f"Specialized in {relevant_domain.domain_name} with {len(relevant_domain.tools)} tools",
                    estimated_performance=relevant_domain.confidence_score,
                    domain_match=relevant_domain.domain_name
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Error evaluating specialist {specialist.name}: {e}")
            return None
    
    async def _execute_delegation(self, user_input: str, history: Optional[str], 
                                candidates: List[DelegationCandidate], 
                                strategy: DelegationStrategy) -> DelegationResult:
        """Execute the delegation using the specified strategy."""
        
        if strategy == DelegationStrategy.DIRECT:
            return await self._execute_direct_delegation(user_input, history, candidates[0])
        
        elif strategy == DelegationStrategy.FALLBACK:
            return await self._execute_fallback_delegation(user_input, history, candidates)
        
        elif strategy == DelegationStrategy.PARALLEL and self.enable_parallel_execution:
            return await self._execute_parallel_delegation(user_input, history, candidates[:3])
        
        elif strategy == DelegationStrategy.CHAIN:
            return await self._execute_chain_delegation(user_input, history, candidates[:2])
        
        else:
            # Default to direct delegation
            return await self._execute_direct_delegation(user_input, history, candidates[0])
    
    async def _execute_direct_delegation(self, user_input: str, history: Optional[str], 
                                       candidate: DelegationCandidate) -> DelegationResult:
        """Execute direct delegation to a single agent."""
        try:
            response = await candidate.agent.get_response(user_input, history)
            
            return DelegationResult(
                agent_used=candidate.agent,
                response=response,
                execution_time=0.0,  # Will be set by caller
                success=True,
                strategy_used=DelegationStrategy.DIRECT
            )
            
        except Exception as e:
            logger.error(f"Direct delegation failed: {e}")
            return DelegationResult(
                agent_used=candidate.agent,
                response=f"I encountered an error: {str(e)}",
                execution_time=0.0,
                success=False,
                strategy_used=DelegationStrategy.DIRECT
            )
    
    async def _execute_fallback_delegation(self, user_input: str, history: Optional[str], 
                                         candidates: List[DelegationCandidate]) -> DelegationResult:
        """Execute delegation with fallback to other agents if first fails."""
        fallback_attempts = 0
        
        for candidate in candidates:
            try:
                response = await candidate.agent.get_response(user_input, history)
                
                return DelegationResult(
                    agent_used=candidate.agent,
                    response=response,
                    execution_time=0.0,
                    success=True,
                    strategy_used=DelegationStrategy.FALLBACK,
                    fallback_attempts=fallback_attempts
                )
                
            except Exception as e:
                logger.warning(f"Agent {candidate.agent.name} failed, trying fallback: {e}")
                fallback_attempts += 1
                continue
        
        # All agents failed
        return DelegationResult(
            agent_used=candidates[-1].agent if candidates else None,
            response="All available agents failed to process your request.",
            execution_time=0.0,
            success=False,
            strategy_used=DelegationStrategy.FALLBACK,
            fallback_attempts=fallback_attempts
        )
    
    async def _execute_parallel_delegation(self, user_input: str, history: Optional[str], 
                                         candidates: List[DelegationCandidate]) -> DelegationResult:
        """Execute delegation to multiple agents in parallel and return the best result."""
        
        async def get_agent_response(candidate: DelegationCandidate):
            try:
                start_time = __import__('time').time()
                response = await candidate.agent.get_response(user_input, history)
                execution_time = __import__('time').time() - start_time
                return (candidate, response, execution_time, True)
            except Exception as e:
                return (candidate, str(e), 0.0, False)
        
        # Run agents in parallel
        tasks = [get_agent_response(candidate) for candidate in candidates]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Find the best successful result
        successful_results = [(c, r, t, s) for c, r, t, s in results if s and not isinstance(r, Exception)]
        
        if successful_results:
            # Choose the result from the highest confidence agent that succeeded
            best_result = successful_results[0]  # Already sorted by confidence
            candidate, response, exec_time, success = best_result
            
            return DelegationResult(
                agent_used=candidate.agent,
                response=response,
                execution_time=exec_time,
                success=True,
                strategy_used=DelegationStrategy.PARALLEL
            )
        else:
            # All failed, return first failure
            failed_result = results[0] if results else None
            return DelegationResult(
                agent_used=candidates[0].agent if candidates else None,
                response=str(failed_result[1]) if failed_result else "All parallel executions failed",
                execution_time=0.0,
                success=False,
                strategy_used=DelegationStrategy.PARALLEL
            )
    
    async def _execute_chain_delegation(self, user_input: str, history: Optional[str], 
                                      candidates: List[DelegationCandidate]) -> DelegationResult:
        """Execute delegation as a chain where output of one agent feeds into the next."""
        
        current_input = user_input
        current_history = history
        agents_used = []
        
        for candidate in candidates:
            try:
                response = await candidate.agent.get_response(current_input, current_history)
                agents_used.append(candidate.agent.name)
                
                # Use this response as input for next agent
                current_input = f"Building on previous response: {response}\n\nOriginal request: {user_input}"
                current_history = f"{current_history}\n{candidate.agent.name}: {response}" if current_history else f"{candidate.agent.name}: {response}"
                
            except Exception as e:
                logger.warning(f"Chain delegation failed at {candidate.agent.name}: {e}")
                break
        
        return DelegationResult(
            agent_used=candidates[-1].agent if candidates else None,
            response=current_input if len(agents_used) > 1 else response,
            execution_time=0.0,
            success=len(agents_used) > 0,
            strategy_used=DelegationStrategy.CHAIN
        )
    
    def _extract_keywords(self, text: str) -> set:
        """Extract keywords from text."""
        words = text.lower().replace('_', ' ').replace('-', ' ').split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return {word for word in words if len(word) > 2 and word not in stop_words}
    
    def _estimate_complexity(self, text: str) -> float:
        """Estimate the complexity of a request."""
        # Simple heuristics
        word_count = len(text.split())
        question_marks = text.count('?')
        has_multiple_sentences = len([s for s in text.split('.') if s.strip()]) > 1
        
        complexity = min(word_count / 50.0, 1.0) + (question_marks * 0.1) + (0.2 if has_multiple_sentences else 0)
        return min(complexity, 1.0)
    
    def _record_delegation(self, user_input: str, result: DelegationResult, 
                          candidates: List[DelegationCandidate]):
        """Record delegation for learning and optimization."""
        
        # Update agent performance
        agent_name = result.agent_used.name if result.agent_used else "unknown"
        
        if agent_name in self.agent_performance:
            perf = self.agent_performance[agent_name]
            perf['usage_count'] += 1
            
            # Update success rate with exponential moving average
            alpha = 0.1
            perf['success_rate'] = (1 - alpha) * perf['success_rate'] + alpha * (1.0 if result.success else 0.0)
            
            # Update average response time
            perf['avg_response_time'] = (1 - alpha) * perf['avg_response_time'] + alpha * result.execution_time
        
        # Record delegation history
        delegation_record = {
            'timestamp': __import__('time').time(),
            'user_input': user_input[:100],  # Truncated for storage
            'agent_used': agent_name,
            'strategy': result.strategy_used.value,
            'success': result.success,
            'execution_time': result.execution_time,
            'candidates_count': len(candidates)
        }
        
        self.delegation_history.append(delegation_record)
        
        # Keep only recent history
        if len(self.delegation_history) > 1000:
            self.delegation_history = self.delegation_history[-1000:]
    
    def get_delegation_stats(self) -> Dict[str, Any]:
        """Get statistics about the delegation system."""
        return {
            'available_agents': len(self.available_agents),
            'specialized_agents': len(self.specialized_agents),
            'total_delegations': len(self.delegation_history),
            'agent_performance': self.agent_performance,
            'system_status': self.expertise_manager.get_system_status()
        }