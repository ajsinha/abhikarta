"""
Mock Provider Implementation
Provides mock LLM functionality for testing without real API calls

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from typing import Dict, List, Optional, Any, Iterator
import time
from datetime import datetime

from ..llmcore.llm_provider import LLMProvider
from ..llmcore.llm_facade import LLMFacade, LLMResponse


class MockFacade(LLMFacade):
    """Mock implementation of LLMFacade for testing."""
    
    def __init__(self, model_name: str, provider_name: str = "mock",
                 api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name, provider_name, api_key, config)
        self.response_template = self.config.get(
            'response_template',
            "Mock response to: {prompt}"
        )
        self.response_delay = self.config.get('response_delay', 0.1)
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a mock response."""
        time.sleep(self.response_delay)
        
        content = self.response_template.format(prompt=prompt[:100])
        
        return LLMResponse(
            content=content,
            model=self.model_name,
            provider=self.provider_name,
            usage={'input_tokens': len(prompt.split()), 'output_tokens': len(content.split())},
            metadata={'mock': True, 'temperature': kwargs.get('temperature', 1.0)},
            timestamp=datetime.now()
        )
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate a mock streaming response."""
        time.sleep(self.response_delay)
        
        content = self.response_template.format(prompt=prompt[:100])
        words = content.split()
        
        for word in words:
            yield word + " "
            time.sleep(0.01)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate a mock chat response."""
        time.sleep(self.response_delay)
        
        last_msg = messages[-1]['content'] if messages else "No message"
        content = f"Mock chat response to: {last_msg[:100]}"
        
        return LLMResponse(
            content=content,
            model=self.model_name,
            provider=self.provider_name,
            usage={
                'input_tokens': sum(len(m['content'].split()) for m in messages),
                'output_tokens': len(content.split())
            },
            metadata={'mock': True, 'messages_count': len(messages)},
            timestamp=datetime.now()
        )
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Generate a mock streaming chat response."""
        time.sleep(self.response_delay)
        
        last_msg = messages[-1]['content'] if messages else "No message"
        content = f"Mock chat response to: {last_msg[:100]}"
        words = content.split()
        
        for word in words:
            yield word + " "
            time.sleep(0.01)


class MockProvider(LLMProvider):
    """
    Mock provider implementation for testing.
    
    This provider doesn't make any actual API calls and returns
    mock responses. Useful for testing and development.
    """
    
    def __init__(self, provider_name: str = "mock", api_key: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name, api_key, config)
        
        # Define available mock models
        self._available_models = {
            'mock-model': {
                'name': 'mock-model',
                'description': 'Basic mock model for testing',
                'version': '1.0',
                'max_tokens': 4096,
                'cost_per_1k_input': 0.0,
                'cost_per_1k_output': 0.0
            },
            'mock-model-large': {
                'name': 'mock-model-large',
                'description': 'Large mock model for testing',
                'version': '1.0',
                'max_tokens': 8192,
                'cost_per_1k_input': 0.0,
                'cost_per_1k_output': 0.0
            },
            'mock-model-fast': {
                'name': 'mock-model-fast',
                'description': 'Fast mock model with minimal delay',
                'version': '1.0',
                'max_tokens': 2048,
                'cost_per_1k_input': 0.0,
                'cost_per_1k_output': 0.0
            }
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of available mock models."""
        return list(self._available_models.keys())
    
    def create_facade(self, model_name: str, **kwargs) -> LLMFacade:
        """Create a mock facade for the specified model."""
        if model_name not in self._available_models:
            raise ValueError(
                f"Model '{model_name}' not available. "
                f"Available models: {self.get_available_models()}"
            )
        
        model_config = self._available_models[model_name].copy()
        model_config.update(kwargs)
        
        # Set response delay based on model type
        if 'fast' in model_name:
            model_config.setdefault('response_delay', 0.01)
        else:
            model_config.setdefault('response_delay', 0.1)
        
        return MockFacade(
            model_name=model_name,
            provider_name=self.provider_name,
            api_key=self.api_key,
            config=model_config
        )
    
    def validate_api_key(self) -> bool:
        """Mock validation always succeeds."""
        return True
