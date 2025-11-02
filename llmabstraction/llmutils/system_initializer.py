"""
LLM System Initializer
Initializes and configures the LLM abstraction system

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

import os
import logging
from typing import Optional

from ..llmcore import LLMProviderFactory, LLMClientFactory
from ..llmproviders import (
    MockProvider,
    AnthropicProvider,
    BedrockProvider,
    TogetherProvider,
    GoogleProvider,
    HuggingFaceProvider,
    GrokProvider
)
from .config_loader import ConfigLoader


class LLMSystem:
    """
    Main system class for initializing and managing the LLM abstraction system.
    
    This class:
    - Loads configuration
    - Registers all llmproviders
    - Provides easy access to client factory
    - Sets up logging
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMSystem, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the LLM system (singleton)."""
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self.config_loader: Optional[ConfigLoader] = None
            self.provider_factory: Optional[LLMProviderFactory] = None
            self.client_factory: Optional[LLMClientFactory] = None
            self._initialized = False
    
    def initialize(self, config_dir: Optional[str] = None, log_level: str = "INFO"):
        """
        Initialize the system.
        
        Args:
            config_dir: Directory containing configuration files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if self._initialized:
            self.logger.warning("System already initialized")
            return
        
        # Setup logging
        self._setup_logging(log_level)
        
        # Load configuration
        self.config_loader = ConfigLoader(config_dir)
        self.logger.info("Configuration loaded")
        
        # Initialize factories
        self.provider_factory = LLMProviderFactory()
        self.client_factory = LLMClientFactory()
        
        # Register all llmproviders
        self._register_providers()
        
        # Load models configuration into client factory
        config_file = os.path.join(
            self.config_loader.config_dir,
            'models_config.json'
        )
        self.client_factory.load_config(config_file)
        
        self._initialized = True
        self.logger.info("LLM System initialized successfully")
    
    def _setup_logging(self, log_level: str):
        """Setup logging configuration."""
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
    
    def _register_providers(self):
        """Register all provider classes."""
        providers = [
            ('mock', MockProvider),
            ('anthropic', AnthropicProvider),
            ('bedrock', BedrockProvider),
            ('together', TogetherProvider),
            ('google', GoogleProvider),
            ('huggingface', HuggingFaceProvider),
            ('grok', GrokProvider)
        ]
        
        for name, provider_class in providers:
            self.provider_factory.register_provider(name, provider_class)
            self.logger.info(f"Registered provider: {name}")
    
    def create_client(self, provider_name: Optional[str] = None,
                     model_name: Optional[str] = None, **kwargs):
        """
        Create an LLM client.
        
        Args:
            provider_name: Provider name (uses default if None)
            model_name: Model name (uses default if None)
            **kwargs: Additional configuration
            
        Returns:
            LLMClient instance
        """
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        # Get API key from llmconfig if not provided
        if provider_name and 'api_key' not in kwargs:
            api_key = self.config_loader.get_api_key(provider_name)
            if api_key:
                kwargs['api_key'] = api_key
        
        return self.client_factory.create_client(
            provider_name=provider_name,
            model_name=model_name,
            **kwargs
        )
    
    def list_providers(self) -> list:
        """List all available llmproviders."""
        if not self._initialized:
            raise RuntimeError("System not initialized")
        return self.provider_factory.get_available_providers()
    
    def list_models(self, provider_name: Optional[str] = None) -> list:
        """
        List available models.
        
        Args:
            provider_name: Provider name (lists all if None)
            
        Returns:
            List of model names
        """
        if not self._initialized:
            raise RuntimeError("System not initialized")
        
        if provider_name:
            return self.client_factory.get_provider_models(provider_name)
        else:
            # Return all models
            return list(self.config_loader.get_all_models().keys())
    
    def get_model_info(self, model_name: str) -> dict:
        """
        Get information about a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dictionary
        """
        if not self._initialized:
            raise RuntimeError("System not initialized")
        
        return self.config_loader.get_model_config(model_name) or {}
    
    def get_provider_info(self, provider_name: str) -> dict:
        """
        Get information about a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider information dictionary
        """
        if not self._initialized:
            raise RuntimeError("System not initialized")
        
        return self.config_loader.get_provider_config(provider_name) or {}
    
    def is_initialized(self) -> bool:
        """Check if system is initialized."""
        return self._initialized
    
    def reload_config(self):
        """Reload configuration."""
        if not self._initialized:
            raise RuntimeError("System not initialized")
        
        self.config_loader.reload()
        config_file = os.path.join(
            self.config_loader.config_dir,
            'models_config.json'
        )
        self.client_factory.load_config(config_file)
        self.logger.info("Configuration reloaded")
    
    def __repr__(self) -> str:
        status = "initialized" if self._initialized else "not initialized"
        return f"<LLMSystem({status})>"


# Convenience function for quick initialization
def initialize_system(config_dir: Optional[str] = None, 
                     log_level: str = "INFO") -> LLMSystem:
    """
    Initialize and return the LLM system instance.
    
    Args:
        config_dir: Directory containing configuration files
        log_level: Logging level
        
    Returns:
        Initialized LLMSystem instance
    """
    system = LLMSystem()
    system.initialize(config_dir, log_level)
    return system
