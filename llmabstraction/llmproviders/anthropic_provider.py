"""
Anthropic Provider Implementation
Provides access to Claude models via Anthropic API

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime

from ..llmcore.llm_provider import LLMProvider
from ..llmcore.llm_facade import LLMFacade, LLMResponse


class AnthropicFacade(LLMFacade):
    """Facade for Anthropic Claude models."""
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using Anthropic API."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Set default parameters
            max_tokens = kwargs.get('max_tokens', 1024)
            temperature = kwargs.get('temperature', 1.0)
            
            # Create message
            message = client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract response
            content = message.content[0].text if message.content else ""
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                usage={
                    'input_tokens': message.usage.input_tokens,
                    'output_tokens': message.usage.output_tokens
                },
                metadata={'stop_reason': message.stop_reason},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in Anthropic generate: {str(e)}")
            return LLMResponse(
                content="",
                model=self.model_name,
                provider=self.provider_name,
                error=str(e)
            )
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate a streaming response."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            max_tokens = kwargs.get('max_tokens', 1024)
            temperature = kwargs.get('temperature', 1.0)
            
            with client.messages.stream(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            self.logger.error(f"Error in Anthropic stream: {str(e)}")
            yield f"Error: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate a chat completion."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            max_tokens = kwargs.get('max_tokens', 1024)
            temperature = kwargs.get('temperature', 1.0)
            
            # Create message
            message = client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages
            )
            
            content = message.content[0].text if message.content else ""
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                usage={
                    'input_tokens': message.usage.input_tokens,
                    'output_tokens': message.usage.output_tokens
                },
                metadata={'stop_reason': message.stop_reason},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in Anthropic chat: {str(e)}")
            return LLMResponse(
                content="",
                model=self.model_name,
                provider=self.provider_name,
                error=str(e)
            )
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Generate a streaming chat completion."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            max_tokens = kwargs.get('max_tokens', 1024)
            temperature = kwargs.get('temperature', 1.0)
            
            with client.messages.stream(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            self.logger.error(f"Error in Anthropic chat stream: {str(e)}")
            yield f"Error: {str(e)}"


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic Claude models."""
    
    def __init__(self, provider_name: str = "anthropic", api_key: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name, api_key, config)
        
        # Define available Anthropic models
        self._available_models = {
            'claude-3-5-sonnet-20241022': {
                'name': 'claude-3-5-sonnet-20241022',
                'description': 'Most intelligent Claude model, balancing intelligence with speed',
                'version': '3.5',
                'max_tokens': 200000,
                'strengths': ['Complex reasoning', 'Code generation', 'Analysis'],
                'cost_per_1m_input': 3.00,
                'cost_per_1m_output': 15.00
            },
            'claude-3-opus-20240229': {
                'name': 'claude-3-opus-20240229',
                'description': 'Most powerful Claude model for complex tasks',
                'version': '3.0',
                'max_tokens': 200000,
                'strengths': ['Complex analysis', 'Research', 'Advanced reasoning'],
                'cost_per_1m_input': 15.00,
                'cost_per_1m_output': 75.00
            },
            'claude-3-sonnet-20240229': {
                'name': 'claude-3-sonnet-20240229',
                'description': 'Balanced Claude model for various tasks',
                'version': '3.0',
                'max_tokens': 200000,
                'strengths': ['General purpose', 'Cost-effective', 'Reliable'],
                'cost_per_1m_input': 3.00,
                'cost_per_1m_output': 15.00
            },
            'claude-3-haiku-20240307': {
                'name': 'claude-3-haiku-20240307',
                'description': 'Fastest Claude model for simple tasks',
                'version': '3.0',
                'max_tokens': 200000,
                'strengths': ['Speed', 'Low cost', 'Simple tasks'],
                'cost_per_1m_input': 0.25,
                'cost_per_1m_output': 1.25
            }
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of available Anthropic models."""
        return list(self._available_models.keys())
    
    def create_facade(self, model_name: str, **kwargs) -> LLMFacade:
        """Create a facade for the specified Anthropic model."""
        if model_name not in self._available_models:
            raise ValueError(
                f"Model '{model_name}' not available. "
                f"Available models: {self.get_available_models()}"
            )
        
        model_config = self._available_models[model_name].copy()
        model_config.update(kwargs)
        
        return AnthropicFacade(
            model_name=model_name,
            provider_name=self.provider_name,
            api_key=self.api_key,
            config=model_config
        )
    
    def validate_api_key(self) -> bool:
        """Validate the Anthropic API key."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            # Try a minimal API call
            client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            return False
