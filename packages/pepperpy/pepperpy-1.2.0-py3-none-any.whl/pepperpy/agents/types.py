"""Agent type definitions and protocols."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, TypeVar

from pepperpy.core.utils.errors import PepperpyError


class AgentError(PepperpyError):
    """Agent error."""
    pass


@dataclass
class AgentConfig:
    """Agent configuration."""
    
    name: str
    description: str
    capabilities: List[str]
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]


class AgentState(Protocol):
    """Agent state protocol."""
    
    @property
    def initialized(self) -> bool:
        """Get initialization status."""
        ...
        
    @property
    def running(self) -> bool:
        """Get running status."""
        ...
        
    @property
    def paused(self) -> bool:
        """Get paused status."""
        ...
        
    @property
    def stopped(self) -> bool:
        """Get stopped status."""
        ...
        
    @property
    def error(self) -> bool:
        """Get error status."""
        ...


class AgentContext(Protocol):
    """Agent context protocol."""
    
    @property
    def state(self) -> AgentState:
        """Get agent state."""
        ...
        
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get context metadata."""
        ...
        
    @property
    def parameters(self) -> Dict[str, Any]:
        """Get context parameters."""
        ...


class AgentCapability(Protocol):
    """Agent capability protocol."""
    
    @property
    def name(self) -> str:
        """Get capability name."""
        ...
        
    @property
    def description(self) -> str:
        """Get capability description."""
        ...
        
    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute capability.
        
        Args:
            **kwargs: Capability-specific arguments
            
        Returns:
            Capability execution result
            
        Raises:
            AgentError: If execution fails
        """
        ...


__all__ = [
    "AgentError",
    "AgentConfig",
    "AgentState",
    "AgentContext",
    "AgentCapability",
] 