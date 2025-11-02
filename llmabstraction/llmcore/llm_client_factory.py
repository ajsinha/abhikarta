"""
LLM Client Factory
Singleton factory for creating LLM client instances

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from typing import Optional, Dict, Any
import logging
import json
import os

from .llm_client import LLMClient
from .llm_provider_factory import LLMProviderFactory


class LLMClientFactory:
    """
    Singleton factory for creating LLM client instances.
    
    This factory uses configuration to create clients with appropriate
    llmproviders and models. It supports default provider/model fallback
    and maintains client instances.
    """
    
    _instance = None
    _config: Optional[Dict[str, Any]] = None
    _default_provider: Optional[str] = None
    _default_model: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMClientFactory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the factory (only once)."""
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self.provider_factory = LLMProviderFactory()
            self._initialized = True
    
    def load_config(self, config_path: str):
        """
        Load configuration from JSON file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                self._config = json.load(f)
            
            # Set default provider and model
            defaults = self._config.get('defaults', {})
            self._default_provider = defaults.get('provider', 'mock')
            self._default_model = defaults.get('model', 'mock-model')
            
            self.logger.info(f"Loaded configuration from {config_path}")
            self.logger.info(f"Default provider: {self._default_provider}, model: {self._default_model}")
            
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            raise
    
    def set_defaults(self, provider: str, model: str):
        """
        Set default provider and model.
        
        Args:
            provider: Default provider name
            model: Default model name
        """
        self._default_provider = provider
        self._default_model = model
        self.logger.info(f"Set defaults - provider: {provider}, model: {model}")
    
    def create_client(self, provider_name: Optional[str] = None,
                     model_name: Optional[str] = None,
                     api_key: Optional[str] = None,
                     history_size: int = 50,
                     **kwargs) -> LLMClient:
        """
        Create an LLM client instance.
        
        Args:
            provider_name: Provider name (uses default if None)
            model_name: Model name (uses default if None)
            api_key: API key (optional)
            history_size: Size of interaction history
            **kwargs: Additional configuration
            
        Returns:
            LLMClient instance
            
        Raises:
            ValueError: If provider/model cannot be created
        """
        # Use defaults if not specified
        if provider_name is None:
            provider_name = self._default_provider
            if provider_name is None:
                raise ValueError("No provider specified and no default configured")
        
        if model_name is None:
            model_name = self._default_model
            if model_name is None:
                raise ValueError("No model specified and no default configured")
        
        try:
            # Get provider instance
            provider = self.provider_factory.get_provider(
                provider_name=provider_name,
                api_key=api_key,
                config=kwargs.get('provider_config')
            )
            
            # Validate model is supported
            if not provider.supports_model(model_name):
                available = provider.get_available_models()
                raise ValueError(
                    f"Model '{model_name}' not supported by provider '{provider_name}'. "
                    f"Available models: {available}"
                )
            
            # Create facade
            facade = provider.create_facade(model_name, **kwargs)
            
            # Create client
            client = LLMClient(facade, history_size=history_size)
            
            self.logger.info(f"Created client: provider={provider_name}, model={model_name}")
            return client
            
        except Exception as e:
            self.logger.error(f"Error creating client: {str(e)}")
            
            # Fallback to mock if available and configured
            if (self._config and 
                self._config.get('fallback_to_mock', False) and 
                provider_name != 'mock'):
                self.logger.warning(f"Falling back to mock provider")
                return self.create_client(
                    provider_name='mock',
                    model_name='mock-model',
                    history_size=history_size
                )
            
            raise
    
    def get_default_provider(self) -> Optional[str]:
        """Get the default provider name."""
        return self._default_provider
    
    def get_default_model(self) -> Optional[str]:
        """Get the default model name."""
        return self._default_model
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """Get the loaded configuration."""
        return self._config
    
    def list_available_providers(self) -> list:
        """
        List all available llmproviders.
        
        Returns:
            List of provider names
        """
        return self.provider_factory.get_available_providers()
    
    def get_provider_models(self, provider_name: str) -> list:
        """
        Get available models for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            List of model names
        """
        try:
            provider = self.provider_factory.get_provider(provider_name)
            return provider.get_available_models()
        except Exception as e:
            self.logger.error(f"Error getting models for {provider_name}: {str(e)}")
            return []
    
    def __repr__(self) -> str:
        return (f"<LLMClientFactory(default_provider={self._default_provider}, "
                f"default_model={self._default_model})>")
