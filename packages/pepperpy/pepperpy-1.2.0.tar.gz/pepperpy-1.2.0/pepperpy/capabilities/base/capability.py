"""
Base capability interface and abstract classes.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, ClassVar, Generic, Awaitable

from pepperpy.core.utils.errors import ProviderError, ValidationError

T = TypeVar('T')  # Type for capability input
R = TypeVar('R')  # Type for capability output


class BaseCapability(Generic[T, R], ABC):
    """Base class for all capabilities.
    
    A capability represents a specific functionality that can be provided by the system.
    It encapsulates the logic for executing specific tasks and managing their lifecycle.
    """
    
    _registry: ClassVar[Dict[str, Type['BaseCapability']]] = {}
    
    @classmethod
    def register(cls, name: str) -> Any:
        """Register a capability class.
        
        Args:
            name: Name to register the capability under.
            
        Returns:
            Decorator function.
        """
        def decorator(capability_cls: Type[T]) -> Type[T]:
            cls._registry[name] = capability_cls
            return capability_cls
        return decorator
    
    @classmethod
    def get_capability(cls, name: str) -> Type['BaseCapability']:
        """Get a registered capability class.
        
        Args:
            name: Name of the capability.
            
        Returns:
            Capability class.
            
        Raises:
            ValueError: If capability is not registered.
        """
        if name not in cls._registry:
            raise ValueError(f"Capability '{name}' not registered")
        return cls._registry[name]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the capability.
        
        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self._initialized = False

    @property
    def name(self) -> str:
        """Get capability name."""
        return self.__class__.__name__
        
    @property
    def is_initialized(self) -> bool:
        """Check if the capability is initialized."""
        return self._initialized
        
    async def initialize(self) -> None:
        """Initialize the capability.
        
        This method should be called before using the capability.
        It should handle any setup required by the capability.
        """
        self._initialized = True
        
    async def cleanup(self) -> None:
        """Clean up capability."""
        if not self.is_initialized:
            return
            
        await self._cleanup_impl()
        self._initialized = False
        
    def validate(self) -> None:
        """Validate capability state."""
        if not self.name:
            raise ValueError("Empty capability name")
            
        self._validate_impl()
        
    @abstractmethod
    async def _initialize_impl(self) -> None:
        """Initialize implementation."""
        pass
        
    @abstractmethod
    async def _cleanup_impl(self) -> None:
        """Clean up implementation."""
        pass
        
    def _validate_impl(self) -> None:
        """Validate implementation."""
        pass

    async def execute(self, input_data: T) -> R:
        """Execute the capability.
        
        Args:
            input_data: Input data for the capability.
            
        Returns:
            The capability's output.
            
        Raises:
            ValidationError: If input validation fails.
        """
        if not self.is_initialized:
            raise ValidationError("Capability not initialized. Call initialize() first.")
        await self.validate_input(input_data)
        result = await self._execute(input_data)
        await self.validate_output(result)
        return result

    @abstractmethod
    async def _execute(self, input_data: T) -> R:
        """Internal execution method to be implemented by subclasses.
        
        Args:
            input_data: Input data for the capability.
            
        Returns:
            The capability's output.
        """
        raise NotImplementedError

    @abstractmethod
    async def validate_input(self, input_data: T) -> None:
        """Validate the input data.
        
        Args:
            input_data: Input data to validate.
            
        Raises:
            ValidationError: If validation fails.
        """
        raise NotImplementedError

    @abstractmethod
    async def validate_output(self, output_data: R) -> None:
        """Validate the output data.
        
        Args:
            output_data: Output data to validate.
            
        Raises:
            ValidationError: If validation fails.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_metadata(self) -> Dict[str, Any]:
        """Get capability metadata.

        Returns:
            Dictionary containing capability metadata
        """
        pass

    @abstractmethod
    async def get_dependencies(self) -> List[str]:
        """Get capability dependencies.

        Returns:
            List of capability names that this capability depends on
        """
        pass

    @abstractmethod
    async def get_required_providers(self) -> List[str]:
        """Get required providers.

        Returns:
            List of provider names required by this capability
        """
        pass

    @abstractmethod
    async def get_supported_inputs(self) -> Dict[str, Any]:
        """Get supported input parameters.

        Returns:
            Dictionary describing supported input parameters and their types
        """
        pass

    @abstractmethod
    async def get_supported_outputs(self) -> Dict[str, Any]:
        """Get supported output parameters.

        Returns:
            Dictionary describing supported output parameters and their types
        """
        pass


class DocumentProcessor(BaseCapability[str, Dict[str, Any]]):
    """Base class for document processing capabilities."""

    async def process(self, document: str) -> Dict[str, Any]:
        """Process a document.
        
        Args:
            document: Document to process.
            
        Returns:
            Processed document data.
        """
        return await self.execute(document)


class TextAnalyzer(BaseCapability[str, Dict[str, Any]]):
    """Base class for text analysis capabilities."""

    async def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            Analysis results.
        """
        return await self.execute(text) 