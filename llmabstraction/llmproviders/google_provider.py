"""
Google Provider Implementation
Provides access to Google Gemini and PaLM models

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime

from ..llmcore.llm_provider import LLMProvider
from ..llmcore.llm_facade import LLMFacade, LLMResponse


class GoogleFacade(LLMFacade):
    """Facade for Google models."""
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using Google AI."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            
            generation_config = {
                'max_output_tokens': kwargs.get('max_tokens', 2048),
                'temperature': kwargs.get('temperature', 0.9),
                'top_p': kwargs.get('top_p', 1.0),
                'top_k': kwargs.get('top_k', 40)
            }
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            content = response.text if response.text else ""
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                usage={
                    'prompt_tokens': response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    'completion_tokens': response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
                },
                metadata={'finish_reason': response.candidates[0].finish_reason if response.candidates else None},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in Google generate: {str(e)}")
            return LLMResponse(
                content="",
                model=self.model_name,
                provider=self.provider_name,
                error=str(e)
            )
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate a streaming response."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            
            generation_config = {
                'max_output_tokens': kwargs.get('max_tokens', 2048),
                'temperature': kwargs.get('temperature', 0.9)
            }
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            self.logger.error(f"Error in Google stream: {str(e)}")
            yield f"Error: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate a chat completion."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            
            # Start chat with history
            history = []
            for i, msg in enumerate(messages[:-1]):
                role = 'user' if msg['role'] in ['user', 'system'] else 'model'
                history.append({'role': role, 'parts': [msg['content']]})
            
            chat = model.start_chat(history=history)
            
            generation_config = {
                'max_output_tokens': kwargs.get('max_tokens', 2048),
                'temperature': kwargs.get('temperature', 0.9)
            }
            
            # Send last message
            response = chat.send_message(
                messages[-1]['content'],
                generation_config=generation_config
            )
            
            content = response.text if response.text else ""
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                usage={
                    'prompt_tokens': response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    'completion_tokens': response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in Google chat: {str(e)}")
            return LLMResponse(
                content="",
                model=self.model_name,
                provider=self.provider_name,
                error=str(e)
            )
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Generate a streaming chat completion."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            
            history = []
            for msg in messages[:-1]:
                role = 'user' if msg['role'] in ['user', 'system'] else 'model'
                history.append({'role': role, 'parts': [msg['content']]})
            
            chat = model.start_chat(history=history)
            
            response = chat.send_message(
                messages[-1]['content'],
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            self.logger.error(f"Error in Google chat stream: {str(e)}")
            yield f"Error: {str(e)}"


class GoogleProvider(LLMProvider):
    """Provider for Google AI models."""
    
    def __init__(self, provider_name: str = "google", api_key: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name, api_key, config)
        
        # Define available Google models
        self._available_models = {
            'gemini-1.5-pro-latest': {
                'name': 'gemini-1.5-pro-latest',
                'description': 'Gemini 1.5 Pro - Most capable model for complex tasks',
                'version': '1.5',
                'max_tokens': 8192,
                'context_window': 2000000,
                'strengths': ['Long context', 'Complex reasoning', 'Multimodal'],
                'cost_per_1m_input': 1.25,
                'cost_per_1m_output': 5.00
            },
            'gemini-1.5-flash-latest': {
                'name': 'gemini-1.5-flash-latest',
                'description': 'Gemini 1.5 Flash - Fast and efficient',
                'version': '1.5',
                'max_tokens': 8192,
                'context_window': 1000000,
                'strengths': ['Speed', 'Cost-effective', 'Long context'],
                'cost_per_1m_input': 0.075,
                'cost_per_1m_output': 0.30
            },
            'gemini-1.0-pro': {
                'name': 'gemini-1.0-pro',
                'description': 'Gemini 1.0 Pro - General purpose model',
                'version': '1.0',
                'max_tokens': 8192,
                'context_window': 32000,
                'strengths': ['General purpose', 'Reliable', 'Efficient'],
                'cost_per_1m_input': 0.50,
                'cost_per_1m_output': 1.50
            },
            'gemini-pro': {
                'name': 'gemini-pro',
                'description': 'Gemini Pro - Optimized for text tasks',
                'version': '1.0',
                'max_tokens': 8192,
                'context_window': 32000,
                'strengths': ['Text generation', 'Balanced', 'Versatile'],
                'cost_per_1m_input': 0.50,
                'cost_per_1m_output': 1.50
            },
            'gemini-1.5-flash-8b': {
                'name': 'gemini-1.5-flash-8b',
                'description': 'Gemini 1.5 Flash 8B - Ultra-fast and low cost',
                'version': '1.5',
                'max_tokens': 8192,
                'context_window': 1000000,
                'strengths': ['Ultra-fast', 'Very low cost', 'High volume'],
                'cost_per_1m_input': 0.0375,
                'cost_per_1m_output': 0.15
            }
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of available Google models."""
        return list(self._available_models.keys())
    
    def create_facade(self, model_name: str, **kwargs) -> LLMFacade:
        """Create a facade for the specified Google model."""
        if model_name not in self._available_models:
            raise ValueError(
                f"Model '{model_name}' not available. "
                f"Available models: {self.get_available_models()}"
            )
        
        model_config = self._available_models[model_name].copy()
        model_config.update(kwargs)
        
        return GoogleFacade(
            model_name=model_name,
            provider_name=self.provider_name,
            api_key=self.api_key,
            config=model_config
        )
    
    def validate_api_key(self) -> bool:
        """Validate the Google AI API key."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            # Try listing models as validation
            list(genai.list_models())
            return True
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            return False
