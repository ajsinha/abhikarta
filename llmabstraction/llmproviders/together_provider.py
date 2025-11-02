"""
Together AI Provider Implementation
Provides access to models via Together AI platform

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime

from ..llmcore.llm_provider import LLMProvider
from ..llmcore.llm_facade import LLMFacade, LLMResponse


class TogetherFacade(LLMFacade):
    """Facade for Together AI models."""
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using Together AI."""
        try:
            import together
            
            together.api_key = self.api_key
            
            max_tokens = kwargs.get('max_tokens', 512)
            temperature = kwargs.get('temperature', 0.7)
            
            response = together.Complete.create(
                model=self.model_name,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=kwargs.get('top_p', 0.7),
                top_k=kwargs.get('top_k', 50),
                repetition_penalty=kwargs.get('repetition_penalty', 1.0)
            )
            
            content = response['output']['choices'][0]['text']
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                usage=response.get('usage', {}),
                metadata={'raw_response': response},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in Together generate: {str(e)}")
            return LLMResponse(
                content="",
                model=self.model_name,
                provider=self.provider_name,
                error=str(e)
            )
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate a streaming response."""
        try:
            import together
            
            together.api_key = self.api_key
            
            max_tokens = kwargs.get('max_tokens', 512)
            temperature = kwargs.get('temperature', 0.7)
            
            for chunk in together.Complete.create_streaming(
                model=self.model_name,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            ):
                if 'choices' in chunk and chunk['choices']:
                    yield chunk['choices'][0].get('text', '')
                    
        except Exception as e:
            self.logger.error(f"Error in Together stream: {str(e)}")
            yield f"Error: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate a chat completion."""
        try:
            import together
            
            together.api_key = self.api_key
            
            max_tokens = kwargs.get('max_tokens', 512)
            temperature = kwargs.get('temperature', 0.7)
            
            response = together.Complete.create(
                model=self.model_name,
                prompt=self._format_chat_prompt(messages),
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response['output']['choices'][0]['text']
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                usage=response.get('usage', {}),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in Together chat: {str(e)}")
            return LLMResponse(
                content="",
                model=self.model_name,
                provider=self.provider_name,
                error=str(e)
            )
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Generate a streaming chat completion."""
        prompt = self._format_chat_prompt(messages)
        return self.generate_stream(prompt, **kwargs)
    
    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format messages into a prompt."""
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                formatted.append(f"System: {content}")
            elif role == 'user':
                formatted.append(f"User: {content}")
            elif role == 'assistant':
                formatted.append(f"Assistant: {content}")
        formatted.append("Assistant:")
        return "\n\n".join(formatted)


class TogetherProvider(LLMProvider):
    """Provider for Together AI models."""
    
    def __init__(self, provider_name: str = "together", api_key: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name, api_key, config)
        
        # Define available Together AI models
        self._available_models = {
            'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo': {
                'name': 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo',
                'description': 'Meta Llama 3.1 405B - Largest Llama model via Together',
                'version': '3.1',
                'max_tokens': 16384,
                'strengths': ['Complex reasoning', 'Code generation', 'Long context'],
                'cost_per_1m_input': 3.50,
                'cost_per_1m_output': 3.50
            },
            'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo': {
                'name': 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo',
                'description': 'Meta Llama 3.1 70B Turbo',
                'version': '3.1',
                'max_tokens': 32768,
                'strengths': ['Balanced', 'Fast', 'Cost-effective'],
                'cost_per_1m_input': 0.88,
                'cost_per_1m_output': 0.88
            },
            'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo': {
                'name': 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo',
                'description': 'Meta Llama 3.1 8B Turbo - Fast and efficient',
                'version': '3.1',
                'max_tokens': 8192,
                'strengths': ['Speed', 'Low cost', 'Simple tasks'],
                'cost_per_1m_input': 0.18,
                'cost_per_1m_output': 0.18
            },
            'mistralai/Mixtral-8x7B-Instruct-v0.1': {
                'name': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
                'description': 'Mixtral 8x7B - MoE model',
                'version': '0.1',
                'max_tokens': 32768,
                'strengths': ['Efficient', 'Multi-lingual', 'Code'],
                'cost_per_1m_input': 0.60,
                'cost_per_1m_output': 0.60
            },
            'mistralai/Mistral-7B-Instruct-v0.2': {
                'name': 'mistralai/Mistral-7B-Instruct-v0.2',
                'description': 'Mistral 7B Instruct v0.2',
                'version': '0.2',
                'max_tokens': 32768,
                'strengths': ['Fast', 'Efficient', 'General purpose'],
                'cost_per_1m_input': 0.20,
                'cost_per_1m_output': 0.20
            },
            'Qwen/Qwen2.5-72B-Instruct-Turbo': {
                'name': 'Qwen/Qwen2.5-72B-Instruct-Turbo',
                'description': 'Qwen 2.5 72B - Strong multilingual model',
                'version': '2.5',
                'max_tokens': 32768,
                'strengths': ['Multilingual', 'Math', 'Code'],
                'cost_per_1m_input': 0.88,
                'cost_per_1m_output': 0.88
            },
            'deepseek-ai/deepseek-llm-67b-chat': {
                'name': 'deepseek-ai/deepseek-llm-67b-chat',
                'description': 'DeepSeek LLM 67B - Strong at code and reasoning',
                'version': '1.0',
                'max_tokens': 4096,
                'strengths': ['Code', 'Math', 'Reasoning'],
                'cost_per_1m_input': 0.90,
                'cost_per_1m_output': 0.90
            }
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of available Together AI models."""
        return list(self._available_models.keys())
    
    def create_facade(self, model_name: str, **kwargs) -> LLMFacade:
        """Create a facade for the specified Together AI model."""
        if model_name not in self._available_models:
            raise ValueError(
                f"Model '{model_name}' not available. "
                f"Available models: {self.get_available_models()}"
            )
        
        model_config = self._available_models[model_name].copy()
        model_config.update(kwargs)
        
        return TogetherFacade(
            model_name=model_name,
            provider_name=self.provider_name,
            api_key=self.api_key,
            config=model_config
        )
    
    def validate_api_key(self) -> bool:
        """Validate the Together AI API key."""
        try:
            import together
            together.api_key = self.api_key
            # Try a simple API call
            together.Models.list()
            return True
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            return False
