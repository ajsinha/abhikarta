"""
LLM Client Implementation
Main client interface for interacting with LLM models

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from typing import Dict, List, Optional, Any, Iterator
from collections import deque
from datetime import datetime
import logging

from .llm_facade import LLMFacade, LLMResponse


class LLMInteractionHistory:
    """
    Manages the history of LLM interactions for multi-shot learning.
    
    Maintains a configurable buffer of past interactions that can be
    used for context in subsequent requests.
    """
    
    def __init__(self, max_history: int = 50):
        """
        Initialize interaction history.
        
        Args:
            max_history: Maximum number of interactions to store
        """
        self.max_history = max_history
        self._history: deque = deque(maxlen=max_history)
        
    def add_interaction(self, prompt: str, response: LLMResponse):
        """
        Add an interaction to history.
        
        Args:
            prompt: The input prompt
            response: The model's response
        """
        self._history.append({
            'prompt': prompt,
            'response': response.content,
            'model': response.model,
            'provider': response.provider,
            'timestamp': response.timestamp,
            'usage': response.usage
        })
        
    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get interaction history.
        
        Args:
            n: Number of recent interactions to return (None for all)
            
        Returns:
            List of interaction dictionaries
        """
        if n is None:
            return list(self._history)
        return list(self._history)[-n:]
    
    def get_as_messages(self, n: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get history formatted as chat messages.
        
        Args:
            n: Number of recent interactions to return
            
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        history = self.get_history(n)
        messages = []
        for interaction in history:
            messages.append({'role': 'user', 'content': interaction['prompt']})
            messages.append({'role': 'assistant', 'content': interaction['response']})
        return messages
    
    def clear(self):
        """Clear all history."""
        self._history.clear()
        
    def size(self) -> int:
        """Get current history size."""
        return len(self._history)
    
    def is_empty(self) -> bool:
        """Check if history is empty."""
        return len(self._history) == 0


class LLMClient:
    """
    Main client for interacting with LLM models.
    
    This client wraps an LLMFacade instance and provides convenience methods
    for various interaction patterns. It maintains interaction history and
    supports multi-shot learning.
    """
    
    def __init__(self, facade: LLMFacade, history_size: int = 50):
        """
        Initialize LLM client.
        
        Args:
            facade: LLMFacade instance for the underlying model
            history_size: Maximum number of interactions to keep in history
        """
        self.facade = facade
        self.history = LLMInteractionHistory(max_history=history_size)
        self.logger = logging.getLogger(f"{__name__}.{facade.model_name}")
        self._default_params: Dict[str, Any] = {}
        
    def generate(self, prompt: str, use_history: bool = False, 
                 save_to_history: bool = True, **kwargs) -> LLMResponse:
        """
        Generate a response from the model.
        
        Args:
            prompt: Input prompt
            use_history: Whether to include interaction history in the prompt
            save_to_history: Whether to save this interaction to history
            **kwargs: Additional generation parameters
            
        Returns:
            LLMResponse object
        """
        try:
            # Merge default parameters with kwargs
            params = {**self._default_params, **kwargs}
            
            if use_history and not self.history.is_empty():
                # Use chat format with history
                messages = self.history.get_as_messages()
                messages.append({'role': 'user', 'content': prompt})
                response = self.facade.chat(messages, **params)
            else:
                response = self.facade.generate(prompt, **params)
            
            if save_to_history and response.error is None:
                self.history.add_interaction(prompt, response)
                
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return LLMResponse(
                content="",
                model=self.facade.model_name,
                provider=self.facade.provider_name,
                error=str(e)
            )
    
    def generate_stream(self, prompt: str, use_history: bool = False, 
                       save_to_history: bool = True, **kwargs) -> Iterator[str]:
        """
        Generate a streaming response.
        
        Args:
            prompt: Input prompt
            use_history: Whether to include interaction history
            save_to_history: Whether to save this interaction to history
            **kwargs: Additional generation parameters
            
        Yields:
            Chunks of generated text
        """
        params = {**self._default_params, **kwargs}
        full_response = []
        
        try:
            if use_history and not self.history.is_empty():
                messages = self.history.get_as_messages()
                messages.append({'role': 'user', 'content': prompt})
                stream = self.facade.chat_stream(messages, **params)
            else:
                stream = self.facade.generate_stream(prompt, **params)
            
            for chunk in stream:
                full_response.append(chunk)
                yield chunk
            
            if save_to_history:
                response = LLMResponse(
                    content=''.join(full_response),
                    model=self.facade.model_name,
                    provider=self.facade.provider_name
                )
                self.history.add_interaction(prompt, response)
                
        except Exception as e:
            self.logger.error(f"Error in streaming generation: {str(e)}")
            yield f"Error: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], save_to_history: bool = True, 
             **kwargs) -> LLMResponse:
        """
        Generate a chat completion.
        
        Args:
            messages: List of message dictionaries
            save_to_history: Whether to save this interaction
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse object
        """
        try:
            params = {**self._default_params, **kwargs}
            response = self.facade.chat(messages, **params)
            
            if save_to_history and response.error is None and messages:
                # Save the last user message and response
                user_msg = next((m['content'] for m in reversed(messages) 
                               if m.get('role') == 'user'), '')
                if user_msg:
                    self.history.add_interaction(user_msg, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in chat: {str(e)}")
            return LLMResponse(
                content="",
                model=self.facade.model_name,
                provider=self.facade.provider_name,
                error=str(e)
            )
    
    def multi_shot_generate(self, prompt: str, n_shots: int = 3, **kwargs) -> LLMResponse:
        """
        Generate with multi-shot learning from history.
        
        Args:
            prompt: Input prompt
            n_shots: Number of previous interactions to include
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse object
        """
        messages = self.history.get_as_messages(n_shots)
        messages.append({'role': 'user', 'content': prompt})
        return self.chat(messages, **kwargs)
    
    def set_default_params(self, **kwargs):
        """
        Set default parameters for all generations.
        
        Args:
            **kwargs: Parameters to set as defaults
        """
        self._default_params.update(kwargs)
    
    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get interaction history.
        
        Args:
            n: Number of recent interactions (None for all)
            
        Returns:
            List of interaction dictionaries
        """
        return self.history.get_history(n)
    
    def clear_history(self):
        """Clear all interaction history."""
        self.history.clear()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the underlying model.
        
        Returns:
            Model information dictionary
        """
        return self.facade.get_model_info()
    
    def __repr__(self) -> str:
        return (f"<LLMClient(model={self.facade.model_name}, "
                f"provider={self.facade.provider_name}, "
                f"history_size={self.history.size()})>")
