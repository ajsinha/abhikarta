"""
Configuration Loader Utility
Loads and manages system configuration from various sources

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import sys

# Import the properties configurator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from core.properties_configurator import PropertiesConfigurator
except ImportError:
    # Fallback if properties_configurator is not available
    class PropertiesConfigurator:
        def __init__(self):
            self._properties = {}
        
        def load_properties(self, filepath: str):
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self._properties[key.strip()] = value.strip()
        
        def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
            return os.environ.get(key, self._properties.get(key, default))
        
        def get_int(self, key: str, default: int = 0) -> int:
            val = self.get(key)
            return int(val) if val else default
        
        def get_bool(self, key: str, default: bool = False) -> bool:
            val = self.get(key)
            return val.lower() in ('true', 'yes', '1') if val else default


class ConfigLoader:
    """
    Centralized configuration loader for the LLM abstraction system.
    
    Loads configuration from:
    1. models_config.json - Model and provider definitions
    2. application.properties - System properties and API keys
    3. Environment variables
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Directory containing configuration files
        """
        if config_dir is None:
            config_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'llmconfig'
            )
        
        self.config_dir = config_dir
        self.logger = logging.getLogger(__name__)
        
        # Configuration storage
        self._models_config: Optional[Dict[str, Any]] = None
        self._properties: Optional[PropertiesConfigurator] = None
        
        # Load configurations
        self._load_properties()
        self._load_models_config()
    
    def _load_properties(self):
        """Load application properties."""
        try:
            properties_file = os.path.join(self.config_dir, 'application.properties')
            
            if os.path.exists(properties_file):
                self._properties = PropertiesConfigurator()
                self._properties.load_properties(properties_file)
                self.logger.info(f"Loaded properties from {properties_file}")
            else:
                self.logger.warning(f"Properties file not found: {properties_file}")
                self._properties = PropertiesConfigurator()
                
        except Exception as e:
            self.logger.error(f"Error loading properties: {str(e)}")
            self._properties = PropertiesConfigurator()
    
    def _load_models_config(self):
        """Load models configuration."""
        try:
            config_file = os.path.join(self.config_dir, 'models_config.json')
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self._models_config = json.load(f)
                self.logger.info(f"Loaded models llmconfig from {config_file}")
            else:
                self.logger.warning(f"Models llmconfig not found: {config_file}")
                self._models_config = {
                    'defaults': {'provider': 'mock', 'model': 'mock-model'},
                    'llmproviders': {},
                    'models': {}
                }
                
        except Exception as e:
            self.logger.error(f"Error loading models llmconfig: {str(e)}")
            self._models_config = {
                'defaults': {'provider': 'mock', 'model': 'mock-model'},
                'llmproviders': {},
                'models': {}
            }
    
    def get_property(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a property value."""
        return self._properties.get(key, default)
    
    def get_int_property(self, key: str, default: int = 0) -> int:
        """Get an integer property."""
        return self._properties.get_int(key, default)
    
    def get_bool_property(self, key: str, default: bool = False) -> bool:
        """Get a boolean property."""
        return self._properties.get_bool(key, default)
    
    def get_models_config(self) -> Dict[str, Any]:
        """Get the complete models configuration."""
        return self._models_config
    
    def get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider configuration dictionary or None
        """
        return self._models_config.get('llmproviders', {}).get(provider_name)
    
    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model configuration dictionary or None
        """
        return self._models_config.get('models', {}).get(model_name)
    
    def get_default_provider(self) -> str:
        """Get the default provider name."""
        return self._models_config.get('defaults', {}).get('provider', 'mock')
    
    def get_default_model(self) -> str:
        """Get the default model name."""
        return self._models_config.get('defaults', {}).get('model', 'mock-model')
    
    def get_api_key(self, provider_name: str) -> Optional[str]:
        """
        Get API key for a provider.
        
        Checks:
        1. Environment variable (PROVIDER_API_KEY)
        2. Properties file
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            API key or None
        """
        env_key = f"{provider_name.upper()}_API_KEY"
        
        # Check environment variable first
        api_key = os.environ.get(env_key)
        if api_key:
            return api_key
        
        # Check properties file
        api_key = self._properties.get(env_key)
        if api_key:
            return api_key
        
        # Check provider llmconfig for api_key_env
        provider_config = self.get_provider_config(provider_name)
        if provider_config and 'api_key_env' in provider_config:
            env_key = provider_config['api_key_env']
            api_key = os.environ.get(env_key)
            if api_key:
                return api_key
        
        return None
    
    def list_available_providers(self) -> list:
        """List all configured llmproviders."""
        return list(self._models_config.get('llmproviders', {}).keys())
    
    def list_provider_models(self, provider_name: str) -> list:
        """
        List all models for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            List of model names
        """
        provider_config = self.get_provider_config(provider_name)
        if provider_config:
            return provider_config.get('models', [])
        return []
    
    def get_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Get all model configurations."""
        return self._models_config.get('models', {})
    
    def reload(self):
        """Reload all configurations."""
        self._load_properties()
        self._load_models_config()
        self.logger.info("Configuration reloaded")
    
    def __repr__(self) -> str:
        return (f"<ConfigLoader(llmproviders={len(self.list_available_providers())}, "
                f"models={len(self.get_all_models())})>")
