"""
Grok (xAI) Provider Implementation
Provides access to Grok models from xAI

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime
import requests

from ..llmcore.llm_provider import LLMProvider
from ..llmcore.llm_facade import LLMFacade, LLMResponse


class GrokFacade(LLMFacade):
    """Facade for Grok models."""
    
    def __init__(self, model_name: str, provider_name: str = "grok",
                 api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name, provider_name, api_key, config)
        self.api_base = config.get('api_base', 'https://api.x.ai/v1')
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using Grok API."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model_name,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 1024),
                'stream': False
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                usage=result.get('usage', {}),
                metadata={'finish_reason': result['choices'][0].get('finish_reason')},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in Grok generate: {str(e)}")
            return LLMResponse(
                content="",
                model=self.model_name,
                provider=self.provider_name,
                error=str(e)
            )
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate a streaming response."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model_name,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 1024),
                'stream': True
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=data,
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data != '[DONE]':
                            import json
                            chunk = json.loads(data)
                            if chunk['choices'][0]['delta'].get('content'):
                                yield chunk['choices'][0]['delta']['content']
                                
        except Exception as e:
            self.logger.error(f"Error in Grok stream: {str(e)}")
            yield f"Error: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate a chat completion."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model_name,
                'messages': messages,
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 1024),
                'stream': False
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                usage=result.get('usage', {}),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in Grok chat: {str(e)}")
            return LLMResponse(
                content="",
                model=self.model_name,
                provider=self.provider_name,
                error=str(e)
            )
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Generate a streaming chat completion."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model_name,
                'messages': messages,
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 1024),
                'stream': True
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=data,
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data != '[DONE]':
                            import json
                            chunk = json.loads(data)
                            if chunk['choices'][0]['delta'].get('content'):
                                yield chunk['choices'][0]['delta']['content']
                                
        except Exception as e:
            self.logger.error(f"Error in Grok chat stream: {str(e)}")
            yield f"Error: {str(e)}"


class GrokProvider(LLMProvider):
    """Provider for xAI Grok models."""
    
    def __init__(self, provider_name: str = "grok", api_key: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name, api_key, config)
        
        # Define available Grok models
        self._available_models = {
            'grok-beta': {
                'name': 'grok-beta',
                'description': 'Grok Beta - xAI\'s conversational AI model',
                'version': 'beta',
                'max_tokens': 131072,
                'strengths': ['Real-time info', 'Conversational', 'X integration'],
                'cost_per_1m_input': 5.00,
                'cost_per_1m_output': 15.00
            },
            'grok-vision-beta': {
                'name': 'grok-vision-beta',
                'description': 'Grok Vision Beta - Multimodal Grok',
                'version': 'beta',
                'max_tokens': 8192,
                'strengths': ['Vision', 'Multimodal', 'Image understanding'],
                'cost_per_1m_input': 5.00,
                'cost_per_1m_output': 15.00
            }
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of available Grok models."""
        return list(self._available_models.keys())
    
    def create_facade(self, model_name: str, **kwargs) -> LLMFacade:
        """Create a facade for the specified Grok model."""
        if model_name not in self._available_models:
            raise ValueError(
                f"Model '{model_name}' not available. "
                f"Available models: {self.get_available_models()}"
            )
        
        model_config = self._available_models[model_name].copy()
        model_config.update(kwargs)
        model_config.update(self.config)
        
        return GrokFacade(
            model_name=model_name,
            provider_name=self.provider_name,
            api_key=self.api_key,
            config=model_config
        )
    
    def validate_api_key(self) -> bool:
        """Validate the Grok API key."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Try a minimal API call
            response = requests.get(
                f'{self.config.get("api_base", "https://api.x.ai/v1")}/models',
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            return False
