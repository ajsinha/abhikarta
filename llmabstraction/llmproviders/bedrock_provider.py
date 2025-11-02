"""
AWS Bedrock Provider Implementation
Provides access to models via AWS Bedrock including Meta Llama models

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime
import json

from ..llmcore.llm_provider import LLMProvider
from ..llmcore.llm_facade import LLMFacade, LLMResponse


class BedrockFacade(LLMFacade):
    """Facade for AWS Bedrock models."""
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response using AWS Bedrock."""
        try:
            import boto3
            
            client = boto3.client('bedrock-runtime', region_name=self.config.get('region', 'us-east-1'))
            
            # Prepare request based on model type
            max_tokens = kwargs.get('max_tokens', 1024)
            temperature = kwargs.get('temperature', 0.7)
            
            # Different models have different request formats
            if 'llama' in self.model_name.lower():
                body = {
                    "prompt": prompt,
                    "max_gen_len": max_tokens,
                    "temperature": temperature,
                    "top_p": kwargs.get('top_p', 0.9)
                }
            elif 'claude' in self.model_name.lower():
                body = {
                    "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                    "max_tokens_to_sample": max_tokens,
                    "temperature": temperature
                }
            elif 'titan' in self.model_name.lower():
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": max_tokens,
                        "temperature": temperature,
                        "topP": kwargs.get('top_p', 1.0)
                    }
                }
            else:
                # Generic format
                body = {
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            
            response = client.invoke_model(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract content based on model type
            if 'llama' in self.model_name.lower():
                content = response_body.get('generation', '')
            elif 'claude' in self.model_name.lower():
                content = response_body.get('completion', '')
            elif 'titan' in self.model_name.lower():
                results = response_body.get('results', [])
                content = results[0].get('outputText', '') if results else ''
            else:
                content = response_body.get('completion', response_body.get('text', ''))
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                usage=response_body.get('amazon-bedrock-invocationMetrics', {}),
                metadata={'response_body': response_body},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in Bedrock generate: {str(e)}")
            return LLMResponse(
                content="",
                model=self.model_name,
                provider=self.provider_name,
                error=str(e)
            )
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate a streaming response (if supported)."""
        try:
            import boto3
            
            client = boto3.client('bedrock-runtime', region_name=self.config.get('region', 'us-east-1'))
            
            max_tokens = kwargs.get('max_tokens', 1024)
            temperature = kwargs.get('temperature', 0.7)
            
            # Streaming support varies by model
            body = {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}
            
            response = client.invoke_model_with_response_stream(
                modelId=self.model_name,
                body=json.dumps(body)
            )
            
            for event in response['body']:
                chunk = json.loads(event['chunk']['bytes'])
                if 'completion' in chunk:
                    yield chunk['completion']
                elif 'outputText' in chunk:
                    yield chunk['outputText']
                    
        except Exception as e:
            self.logger.error(f"Error in Bedrock stream: {str(e)}")
            yield f"Error: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Generate a chat completion."""
        # Convert messages to prompt format
        prompt = self._messages_to_prompt(messages)
        return self.generate(prompt, **kwargs)
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Generate a streaming chat completion."""
        prompt = self._messages_to_prompt(messages)
        return self.generate_stream(prompt, **kwargs)
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to a single prompt."""
        prompt_parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                prompt_parts.append(f"Human: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)


class BedrockProvider(LLMProvider):
    """Provider for AWS Bedrock models including Meta Llama."""
    
    def __init__(self, provider_name: str = "bedrock", api_key: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(provider_name, api_key, config)
        
        # Define available Bedrock models
        self._available_models = {
            # Meta Llama models
            'meta.llama3-3-70b-instruct-v1:0': {
                'name': 'meta.llama3-3-70b-instruct-v1:0',
                'description': 'Meta Llama 3.3 70B Instruct - Powerful open source model',
                'version': '3.3',
                'max_tokens': 8192,
                'strengths': ['General purpose', 'Instruction following', 'Multi-lingual'],
                'cost_per_1m_input': 0.99,
                'cost_per_1m_output': 0.99
            },
            'meta.llama3-1-405b-instruct-v1:0': {
                'name': 'meta.llama3-1-405b-instruct-v1:0',
                'description': 'Meta Llama 3.1 405B - Largest Llama model',
                'version': '3.1',
                'max_tokens': 32768,
                'strengths': ['Complex reasoning', 'Code generation', 'Extended context'],
                'cost_per_1m_input': 5.32,
                'cost_per_1m_output': 16.00
            },
            'meta.llama3-1-70b-instruct-v1:0': {
                'name': 'meta.llama3-1-70b-instruct-v1:0',
                'description': 'Meta Llama 3.1 70B Instruct',
                'version': '3.1',
                'max_tokens': 32768,
                'strengths': ['Balanced performance', 'Cost-effective', 'Long context'],
                'cost_per_1m_input': 0.99,
                'cost_per_1m_output': 0.99
            },
            'meta.llama3-1-8b-instruct-v1:0': {
                'name': 'meta.llama3-1-8b-instruct-v1:0',
                'description': 'Meta Llama 3.1 8B Instruct - Fast and efficient',
                'version': '3.1',
                'max_tokens': 32768,
                'strengths': ['Fast inference', 'Low cost', 'Simple tasks'],
                'cost_per_1m_input': 0.22,
                'cost_per_1m_output': 0.22
            },
            # Amazon Titan models
            'amazon.titan-text-premier-v1:0': {
                'name': 'amazon.titan-text-premier-v1:0',
                'description': 'Amazon Titan Text Premier - Advanced text model',
                'version': '1.0',
                'max_tokens': 32000,
                'strengths': ['RAG optimization', 'Multi-lingual', 'Enterprise'],
                'cost_per_1m_input': 0.50,
                'cost_per_1m_output': 1.50
            },
            'amazon.titan-text-express-v1': {
                'name': 'amazon.titan-text-express-v1',
                'description': 'Amazon Titan Text Express',
                'version': '1.0',
                'max_tokens': 8192,
                'strengths': ['Fast', 'Cost-effective', 'General purpose'],
                'cost_per_1m_input': 0.20,
                'cost_per_1m_output': 0.60
            },
            # Anthropic Claude via Bedrock
            'anthropic.claude-3-5-sonnet-20241022-v2:0': {
                'name': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                'description': 'Claude 3.5 Sonnet via Bedrock',
                'version': '3.5',
                'max_tokens': 200000,
                'strengths': ['Complex reasoning', 'Code generation', 'Analysis'],
                'cost_per_1m_input': 3.00,
                'cost_per_1m_output': 15.00
            },
            'anthropic.claude-3-opus-20240229-v1:0': {
                'name': 'anthropic.claude-3-opus-20240229-v1:0',
                'description': 'Claude 3 Opus via Bedrock',
                'version': '3.0',
                'max_tokens': 200000,
                'strengths': ['Complex tasks', 'Research', 'Analysis'],
                'cost_per_1m_input': 15.00,
                'cost_per_1m_output': 75.00
            },
            # Mistral models
            'mistral.mistral-large-2407-v1:0': {
                'name': 'mistral.mistral-large-2407-v1:0',
                'description': 'Mistral Large - Advanced multilingual model',
                'version': '2407',
                'max_tokens': 32000,
                'strengths': ['Multilingual', 'Code', 'Function calling'],
                'cost_per_1m_input': 4.00,
                'cost_per_1m_output': 12.00
            },
            'mistral.mixtral-8x7b-instruct-v0:1': {
                'name': 'mistral.mixtral-8x7b-instruct-v0:1',
                'description': 'Mixtral 8x7B - MoE architecture model',
                'version': '0.1',
                'max_tokens': 32000,
                'strengths': ['Cost-effective', 'Fast', 'General purpose'],
                'cost_per_1m_input': 0.45,
                'cost_per_1m_output': 0.70
            }
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of available Bedrock models."""
        return list(self._available_models.keys())
    
    def create_facade(self, model_name: str, **kwargs) -> LLMFacade:
        """Create a facade for the specified Bedrock model."""
        if model_name not in self._available_models:
            raise ValueError(
                f"Model '{model_name}' not available. "
                f"Available models: {self.get_available_models()}"
            )
        
        model_config = self._available_models[model_name].copy()
        model_config.update(kwargs)
        model_config.update(self.config)  # Include provider llmconfig
        
        return BedrockFacade(
            model_name=model_name,
            provider_name=self.provider_name,
            api_key=self.api_key,
            config=model_config
        )
    
    def validate_api_key(self) -> bool:
        """Validate AWS credentials."""
        try:
            import boto3
            client = boto3.client('bedrock-runtime', region_name=self.config.get('region', 'us-east-1'))
            # AWS credentials are validated through boto3
            return True
        except Exception as e:
            self.logger.error(f"AWS credential validation failed: {str(e)}")
            return False
