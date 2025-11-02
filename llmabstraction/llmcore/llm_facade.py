"""
LLM Facade Abstract Base Class
Provides a unified interface for interacting with LLM models

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class LLMResponse:
    """
    Standardized response from LLM interactions.
    
    Attributes:
        content: The generated text content
        model: Model that generated the response
        provider: Provider name
        usage: Token usage statistics
        metadata: Additional response metadata
        timestamp: When the response was generated
        error: Error message if request failed
    """
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class LLMFacade(ABC):
    """
    Abstract facade for LLM model interactions.
    
    This provides a unified interface for all LLM models regardless of provider.
    Each provider implements this facade for their specific models.
    """
    
    def __init__(self, model_name: str, provider_name: str, 
                 api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM facade.
        
        Args:
            model_name: Name/identifier of the model
            provider_name: Name of the provider
            api_key: API key for authentication
            config: Model-specific configuration
        """
        self.model_name = model_name
        self.provider_name = provider_name
        self.api_key = api_key
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{provider_name}.{model_name}")
        
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Generate a response from the model.
        
        Args:
            prompt: Input prompt for the model
            **kwargs: Additional generation parameters (temperature, max_tokens, etc.)
            
        Returns:
            LLMResponse containing the generated content
        """
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Generate a streaming response from the model.
        
        Args:
            prompt: Input prompt for the model
            **kwargs: Additional generation parameters
            
        Yields:
            Chunks of generated text
        """
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        Generate a chat completion response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional generation parameters
            
        Returns:
            LLMResponse containing the generated content
        """
        pass
    
    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """
        Generate a streaming chat completion response.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional generation parameters
            
        Yields:
            Chunks of generated text
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about this model.
        
        Returns:
            Dictionary containing model metadata
        """
        return {
            'model_name': self.model_name,
            'provider': self.provider_name,
            'llmconfig': self.config
        }
    
    def supports_streaming(self) -> bool:
        """
        Check if this model supports streaming responses.
        
        Returns:
            True if streaming is supported
        """
        return True
    
    def supports_chat(self) -> bool:
        """
        Check if this model supports chat format.
        
        Returns:
            True if chat format is supported
        """
        return True
    
    def get_max_tokens(self) -> int:
        """
        Get the maximum token limit for this model.
        
        Returns:
            Maximum number of tokens
        """
        return self.config.get('max_tokens', 4096)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(model={self.model_name}, provider={self.provider_name})>"
