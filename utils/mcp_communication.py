from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid

@dataclass
class ToolRequest:
    """
    Represents a request to execute an MCP tool.
    This is sent from the agent to the tool execution system.
    """
    tool_name: str
    parameters: Dict[str, Any]
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "context": self.context,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolRequest":
        """Create from dictionary"""
        return cls(
            tool_name=data.get("tool_name"),
            parameters=data.get("parameters", {}),
            request_id=data.get("request_id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            context=data.get("context", {}),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "ToolRequest":
        """Create from JSON string"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class ToolResult:
    """
    Represents the result of executing an MCP tool.
    This is returned from the tool execution system to the agent.
    """
    request_id: str
    tool_name: str
    result: Any
    is_success: bool
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: Optional[float] = None
    formatted_result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "result": self.result,
            "is_success": self.is_success,
            "error": self.error,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "formatted_result": self.formatted_result,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolResult":
        """Create from dictionary"""
        return cls(
            request_id=data.get("request_id", ""),
            tool_name=data.get("tool_name", ""),
            result=data.get("result"),
            is_success=data.get("is_success", False),
            error=data.get("error"),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            duration_ms=data.get("duration_ms"),
            formatted_result=data.get("formatted_result"),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "ToolResult":
        """Create from JSON string"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class StreamingToolResult:
    """
    Represents a streaming result from an MCP tool execution.
    Used for tools that generate results incrementally.
    """
    request_id: str
    tool_name: str
    result: Any
    is_success: bool
    is_complete: bool
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    sequence: int = 0
    total_sequences: Optional[int] = None
    formatted_result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "result": self.result,
            "is_success": self.is_success,
            "is_complete": self.is_complete,
            "error": self.error,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "total_sequences": self.total_sequences,
            "formatted_result": self.formatted_result,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StreamingToolResult":
        """Create from dictionary"""
        return cls(
            request_id=data.get("request_id", ""),
            tool_name=data.get("tool_name", ""),
            result=data.get("result"),
            is_success=data.get("is_success", False),
            is_complete=data.get("is_complete", False),
            error=data.get("error"),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            sequence=data.get("sequence", 0),
            total_sequences=data.get("total_sequences"),
            formatted_result=data.get("formatted_result"),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "StreamingToolResult":
        """Create from JSON string"""
        return cls.from_dict(json.loads(json_str))


class ToolCommunicationManager:
    """
    Manages communication between agents and tools.
    Provides a standardized interface for tool execution and result handling.
    """
    
    def __init__(self, tool_executor=None):
        self.tool_executor = tool_executor
        self.pending_requests: Dict[str, ToolRequest] = {}
        self.completed_results: Dict[str, ToolResult] = {}
    
    def create_tool_request(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> ToolRequest:
        """Create a tool request"""
        request = ToolRequest(
            tool_name=tool_name,
            parameters=parameters,
            context=context or {}
        )
        self.pending_requests[request.request_id] = request
        return request
    
    async def execute_tool(self, request: ToolRequest) -> ToolResult:
        """Execute a tool and get the result"""
        start_time = datetime.now()
        
        try:
            if not self.tool_executor:
                raise ValueError("No tool executor available")
            
            # Execute the tool
            response = await self.tool_executor.execute(
                request.tool_name,
                **request.parameters
            )
            
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Create the result
            result = ToolResult(
                request_id=request.request_id,
                tool_name=request.tool_name,
                result=response.result,
                is_success=response.is_success,
                error=response.error,
                timestamp=datetime.now().isoformat(),
                duration_ms=duration_ms,
            )
            
            # Store the result
            self.completed_results[request.request_id] = result
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Create an error result
            result = ToolResult(
                request_id=request.request_id,
                tool_name=request.tool_name,
                result=None,
                is_success=False,
                error=str(e),
                timestamp=datetime.now().isoformat(),
                duration_ms=duration_ms,
            )
            
            # Store the result
            self.completed_results[request.request_id] = result
            
            return result
    
    async def execute_streaming_tool(self, request: ToolRequest):
        """Execute a streaming tool and yield results incrementally"""
        start_time = datetime.now()
        sequence = 0
        
        try:
            if not self.tool_executor:
                raise ValueError("No tool executor available")
            
            # Get the tool factory from the executor
            tool_factory = self.tool_executor.factory
            
            # Get the tool
            tool = tool_factory.get_tool(request.tool_name)
            if not tool:
                raise ValueError(f"Tool not found: {request.tool_name}")
            
            # Execute the streaming tool
            async for response in tool.execute_streaming(**request.parameters):
                sequence += 1
                
                # Create the streaming result
                yield StreamingToolResult(
                    request_id=request.request_id,
                    tool_name=request.tool_name,
                    result=response.result,
                    is_success=response.is_success,
                    is_complete=response.is_complete,
                    error=response.error,
                    timestamp=datetime.now().isoformat(),
                    sequence=sequence,
                )
                
                # If complete, store the final result
                if response.is_complete:
                    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                    
                    result = ToolResult(
                        request_id=request.request_id,
                        tool_name=request.tool_name,
                        result=response.result,
                        is_success=response.is_success,
                        error=response.error,
                        timestamp=datetime.now().isoformat(),
                        duration_ms=duration_ms,
                    )
                    
                    self.completed_results[request.request_id] = result
            
        except Exception as e:
            # Yield an error result
            yield StreamingToolResult(
                request_id=request.request_id,
                tool_name=request.tool_name,
                result=None,
                is_success=False,
                is_complete=True,
                error=str(e),
                timestamp=datetime.now().isoformat(),
                sequence=sequence + 1,
            )
            
            # Store the error result
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            result = ToolResult(
                request_id=request.request_id,
                tool_name=request.tool_name,
                result=None,
                is_success=False,
                error=str(e),
                timestamp=datetime.now().isoformat(),
                duration_ms=duration_ms,
            )
            
            self.completed_results[request.request_id] = result
    
    def get_result(self, request_id: str) -> Optional[ToolResult]:
        """Get a completed result by request ID"""
        return self.completed_results.get(request_id)
