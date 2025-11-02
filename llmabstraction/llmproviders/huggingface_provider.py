"""
Hugging Face Provider Implementation
Provides access to models via Hugging Face Inference API

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime

from ..llmcore.llm_provider import LLMProvider
from ..llmcore.llm_facade import LLMFacade, LLMResponse


class HuggingFaceFacade(LLMFacade):
    """Facade for Hugging Face models."""
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using Hugging Face Inference API."""
        try:
            from huggingface_hub import InferenceClient
            
            client = InferenceClient(token=self.api_key)
            
            max_tokens = kwargs.get('max_tokens', 512)
            temperature = kwargs.get('temperature', 0.7)
            
            response = client.text_generation(
                prompt=prompt,
                model=self.model_name,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=kwargs.get('top_p', 0.9),
                repetition_penalty=kwargs.get('repetition_penalty', 1.0),
                return_full_text=False
            )
            
            content = response if isinstance(response, str) else response.get('generated_text', '')
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                usage={'input_tokens': len(prompt.split()), 'output_tokens': len(content.split())},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in HuggingFace generate: {str(e)}")
            return LLMResponse(
                content="",
                model=self.model_name,
                provider=self.provider_name,
                error=str(e)
            )
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate a streaming response."""
        try:
            from huggingface_hub import InferenceClient
            
            client = InferenceClient(token=self.api_key)
            
            max_tokens = kwargs.get('max_tokens', 512)
            temperature = kwargs.get('temperature', 0.7)
            
            for token in client.text_generation(
                prompt=prompt,
                model=self.model_name,
                max_new_tokens=max_tokens,
                temperature=temperature,
                stream=True
            ):
                yield token
                
        except Exception as e:
            self.logger.error(f"Error in HuggingFace stream: {str(e)}")
            yield f"Error: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate a chat completion."""
        try:
            from huggingface_hub import InferenceClient
            
            client = InferenceClient(token=self.api_key)
            
            max_tokens = kwargs.get('max_tokens', 512)
            temperature = kwargs.get('temperature', 0.7)
            
            response = client.chat_completion(
                messages=messages,
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content if response.choices else ""
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                usage={
                    'input_tokens': response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                    'output_tokens': response.usage.completion_tokens if hasattr(response, 'usage') else 0
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in HuggingFace chat: {str(e)}")
            # Fallback to text generation
            prompt = self._format_chat_prompt(messages)
            return self.generate(prompt, **kwargs)
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Generate a streaming chat completion."""
        try:
            from huggingface_hub import InferenceClient
            
            client = InferenceClient(token=self.api_key)
            
            max_tokens = kwargs.get('max_tokens', 512)
            
            for chunk in client.chat_completion(
                messages=messages,
                model=self.model_name,
                max_tokens=max_tokens,
                stream=True
            ):
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"Error in HuggingFace chat stream: {str(e)}")
            prompt = self._format_chat_prompt(messages)
            return self.generate_stream(prompt, **kwargs)
    
    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format messages into a prompt."""
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"{role.capitalize()}: {content}")
        return "\n".join(formatted)


class HuggingFaceProvider(LLMProvider):
    """Provider for Hugging Face models."""
    
    def __init__(self, provider_name: str = "huggingface", api_key: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name, api_key, config)
        
        # Define available Hugging Face models
        self._available_models = {
            'meta-llama/Meta-Llama-3.1-70B-Instruct': {
                'name': 'meta-llama/Meta-Llama-3.1-70B-Instruct',
                'description': 'Meta Llama 3.1 70B via Hugging Face',
                'version': '3.1',
                'max_tokens': 8192,
                'strengths': ['General purpose', 'Instruction following', 'Open source'],
                'cost_per_1m_input': 0.65,
                'cost_per_1m_output': 0.65
            },
            'meta-llama/Meta-Llama-3.1-8B-Instruct': {
                'name': 'meta-llama/Meta-Llama-3.1-8B-Instruct',
                'description': 'Meta Llama 3.1 8B via Hugging Face',
                'version': '3.1',
                'max_tokens': 8192,
                'strengths': ['Fast', 'Efficient', 'Cost-effective'],
                'cost_per_1m_input': 0.05,
                'cost_per_1m_output': 0.05
            },
            'mistralai/Mistral-7B-Instruct-v0.3': {
                'name': 'mistralai/Mistral-7B-Instruct-v0.3',
                'description': 'Mistral 7B Instruct v0.3',
                'version': '0.3',
                'max_tokens': 32768,
                'strengths': ['Efficient', 'Multi-lingual', 'Open source'],
                'cost_per_1m_input': 0.05,
                'cost_per_1m_output': 0.05
            },
            'mistralai/Mixtral-8x7B-Instruct-v0.1': {
                'name': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
                'description': 'Mixtral 8x7B - MoE architecture',
                'version': '0.1',
                'max_tokens': 32768,
                'strengths': ['MoE', 'Multi-lingual', 'Efficient'],
                'cost_per_1m_input': 0.25,
                'cost_per_1m_output': 0.25
            },
            'microsoft/Phi-3-mini-4k-instruct': {
                'name': 'microsoft/Phi-3-mini-4k-instruct',
                'description': 'Microsoft Phi-3 Mini - Compact and efficient',
                'version': '3',
                'max_tokens': 4096,
                'strengths': ['Small', 'Fast', 'Edge deployment'],
                'cost_per_1m_input': 0.02,
                'cost_per_1m_output': 0.02
            },
            'Qwen/Qwen2.5-72B-Instruct': {
                'name': 'Qwen/Qwen2.5-72B-Instruct',
                'description': 'Qwen 2.5 72B - Strong multilingual',
                'version': '2.5',
                'max_tokens': 32768,
                'strengths': ['Multilingual', 'Math', 'Code'],
                'cost_per_1m_input': 0.40,
                'cost_per_1m_output': 0.40
            },
            'google/gemma-2-9b-it': {
                'name': 'google/gemma-2-9b-it',
                'description': 'Google Gemma 2 9B - Open source from Google',
                'version': '2',
                'max_tokens': 8192,
                'strengths': ['Open source', 'Efficient', 'Google research'],
                'cost_per_1m_input': 0.05,
                'cost_per_1m_output': 0.05
            },
            'tiiuae/falcon-180B-chat': {
                'name': 'tiiuae/falcon-180B-chat',
                'description': 'Falcon 180B - Large open source model',
                'version': '180B',
                'max_tokens': 2048,
                'strengths': ['Large scale', 'Open source', 'Research'],
                'cost_per_1m_input': 1.80,
                'cost_per_1m_output': 1.80
            }
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of available Hugging Face models."""
        return list(self._available_models.keys())
    
    def create_facade(self, model_name: str, **kwargs) -> LLMFacade:
        """Create a facade for the specified Hugging Face model."""
        if model_name not in self._available_models:
            raise ValueError(
                f"Model '{model_name}' not available. "
                f"Available models: {self.get_available_models()}"
            )
        
        model_config = self._available_models[model_name].copy()
        model_config.update(kwargs)
        
        return HuggingFaceFacade(
            model_name=model_name,
            provider_name=self.provider_name,
            api_key=self.api_key,
            config=model_config
        )
    
    def validate_api_key(self) -> bool:
        """Validate the Hugging Face API key."""
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(token=self.api_key)
            # Try a simple inference call
            return True
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            return False
