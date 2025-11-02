"""
LLM Provider Factory
Singleton factory for creating and managing LLM provider instances

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from typing import Dict, Optional, Any, Type
import logging
import os

from .llm_provider import LLMProvider


class LLMProviderFactory:
    """
    Singleton factory for creating LLM provider instances.
    
    This factory maintains a registry of provider classes and creates
    instances based on configuration. It supports lazy loading and
    caching of provider instances.
    """
    
    _instance = None
    _provider_registry: Dict[str, Type[LLMProvider]] = {}
    _provider_instances: Dict[str, LLMProvider] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMProviderFactory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the factory (only once)."""
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self._initialized = True
    
    def register_provider(self, provider_name: str, provider_class: Type[LLMProvider]):
        """
        Register a provider class.
        
        Args:
            provider_name: Unique name for the provider
            provider_class: Provider class to register
        """
        self._provider_registry[provider_name.lower()] = provider_class
        self.logger.info(f"Registered provider: {provider_name}")
    
    def get_provider(self, provider_name: str, api_key: Optional[str] = None,
                     config: Optional[Dict[str, Any]] = None, 
                     use_cache: bool = True) -> LLMProvider:
        """
        Get a provider instance.
        
        Args:
            provider_name: Name of the provider
            api_key: API key (optional if in env or llmconfig)
            config: Additional configuration
            use_cache: Whether to use cached instance
            
        Returns:
            LLMProvider instance
            
        Raises:
            ValueError: If provider is not registered
        """
        provider_key = provider_name.lower()
        
        # Check cache if requested
        if use_cache and provider_key in self._provider_instances:
            return self._provider_instances[provider_key]
        
        # Get provider class
        if provider_key not in self._provider_registry:
            raise ValueError(
                f"Provider '{provider_name}' not registered. "
                f"Available providers: {list(self._provider_registry.keys())}"
            )
        
        provider_class = self._provider_registry[provider_key]
        
        # Try to get API key from environment if not provided
        if api_key is None:
            env_key = f"{provider_name.upper()}_API_KEY"
            api_key = os.environ.get(env_key)
        
        # Create provider instance
        provider = provider_class(
            provider_name=provider_name,
            api_key=api_key,
            config=config
        )
        
        # Cache if requested
        if use_cache:
            self._provider_instances[provider_key] = provider
        
        return provider
    
    def get_available_providers(self) -> list:
        """
        Get list of registered provider names.
        
        Returns:
            List of provider names
        """
        return list(self._provider_registry.keys())
    
    def is_provider_registered(self, provider_name: str) -> bool:
        """
        Check if a provider is registered.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            True if registered, False otherwise
        """
        return provider_name.lower() in self._provider_registry
    
    def clear_cache(self, provider_name: Optional[str] = None):
        """
        Clear cached provider instances.
        
        Args:
            provider_name: Specific provider to clear, or None for all
        """
        if provider_name:
            self._provider_instances.pop(provider_name.lower(), None)
        else:
            self._provider_instances.clear()
    
    def __repr__(self) -> str:
        return f"<LLMProviderFactory(providers={len(self._provider_registry)})>"
