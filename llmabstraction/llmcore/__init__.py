"""
LLM Abstraction System - Core Module
Core abstractions and factories for LLM interactions

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from .llm_provider import LLMProvider
from .llm_facade import LLMFacade, LLMResponse
from .llm_client import LLMClient, LLMInteractionHistory
from .llm_provider_factory import LLMProviderFactory
from .llm_client_factory import LLMClientFactory

__all__ = [
    'LLMProvider',
    'LLMFacade',
    'LLMResponse',
    'LLMClient',
    'LLMInteractionHistory',
    'LLMProviderFactory',
    'LLMClientFactory',
]

__version__ = '1.0.0'
