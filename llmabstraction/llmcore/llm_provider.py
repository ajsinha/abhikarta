"""
LLM Provider Abstract Base Class
Defines the interface for all LLM llmproviders in the system

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging


class LLMProvider(ABC):
    """
    Abstract base class for LLM llmproviders.
    
    A provider manages API keys, access rights, and model instantiation
    for a specific LLM service provider (e.g., OpenAI, Anthropic, AWS Bedrock).
    
    Each provider implementation knows which models it can provide and
    creates appropriate LLMFacade instances for those models.
    """
    
    def __init__(self, provider_name: str, api_key: Optional[str] = None, 
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM provider.
        
        Args:
            provider_name: Name of the provider (e.g., 'anthropic', 'openai')
            api_key: API key for authentication (optional if using env vars)
            config: Additional provider-specific configuration
        """
        self.provider_name = provider_name
        self.api_key = api_key
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{provider_name}")
        self._available_models: Dict[str, Dict[str, Any]] = {}
        
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of model names available from this provider.
        
        Returns:
            List of model identifiers
        """
        pass
    
    @abstractmethod
    def create_facade(self, model_name: str, **kwargs) -> 'LLMFacade':
        """
        Create an LLMFacade instance for the specified model.
        
        Args:
            model_name: Name of the model to create facade for
            **kwargs: Additional model-specific parameters
            
        Returns:
            LLMFacade instance for the model
            
        Raises:
            ValueError: If model is not supported by this provider
        """
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Validate the API key for this provider.
        
        Returns:
            True if API key is valid, False otherwise
        """
        pass
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary containing model metadata or None if not found
        """
        return self._available_models.get(model_name)
    
    def supports_model(self, model_name: str) -> bool:
        """
        Check if this provider supports the specified model.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model is supported, False otherwise
        """
        return model_name in self.get_available_models()
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name
        """
        return self.provider_name
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(provider={self.provider_name}, models={len(self._available_models)})>"
