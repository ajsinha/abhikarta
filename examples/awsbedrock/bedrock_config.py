"""
AWS Bedrock Configuration File

Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com

This file contains configuration settings for AWS Bedrock examples.
Copy this to config.py and update with your settings.
"""

# AWS Configuration
AWS_CONFIG = {
    'region_name': 'us-east-1',  # Available: us-east-1, us-west-2, eu-west-1, etc.
    'profile_name': 'default',    # AWS CLI profile name
}

# Model IDs (Current as of 2025)
MODEL_IDS = {
    # Meta Llama Models
    'llama_3_8b': 'meta.llama3-8b-instruct-v1:0',
    'llama_3_70b': 'meta.llama3-70b-instruct-v1:0',
    'llama_2_13b': 'meta.llama2-13b-chat-v1',
    'llama_2_70b': 'meta.llama2-70b-chat-v1',
    
    # Anthropic Claude Models
    'claude_3_opus': 'anthropic.claude-3-opus-20240229-v1:0',
    'claude_3_sonnet': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'claude_3_haiku': 'anthropic.claude-3-haiku-20240307-v1:0',
    'claude_instant': 'anthropic.claude-instant-v1',
    
    # Amazon Titan Models
    'titan_express': 'amazon.titan-text-express-v1',
    'titan_lite': 'amazon.titan-text-lite-v1',
    'titan_embed': 'amazon.titan-embed-text-v1',
    'titan_embed_v2': 'amazon.titan-embed-text-v2:0',
    
    # AI21 Labs Models
    'jurassic_ultra': 'ai21.j2-ultra-v1',
    'jurassic_mid': 'ai21.j2-mid-v1',
    
    # Cohere Models
    'cohere_command': 'cohere.command-text-v14',
    'cohere_command_light': 'cohere.command-light-text-v14',
    'cohere_embed_english': 'cohere.embed-english-v3',
    'cohere_embed_multilingual': 'cohere.embed-multilingual-v3',
    
    # Mistral AI Models
    'mistral_7b': 'mistral.mistral-7b-instruct-v0:2',
    'mistral_8x7b': 'mistral.mixtral-8x7b-instruct-v0:1',
    'mistral_large': 'mistral.mistral-large-2402-v1:0',
    
    # Stability AI Models
    'stable_diffusion_xl': 'stability.stable-diffusion-xl-v1',
    'stable_diffusion': 'stability.stable-diffusion-xl-v0',
}

# Default Generation Parameters
DEFAULT_PARAMS = {
    'llama': {
        'max_gen_len': 512,
        'temperature': 0.7,
        'top_p': 0.9,
    },
    'claude': {
        'max_tokens': 512,
        'temperature': 0.7,
        'top_p': 0.9,
        'anthropic_version': 'bedrock-2023-05-31',
    },
    'titan': {
        'maxTokenCount': 512,
        'temperature': 0.7,
        'topP': 0.9,
    },
    'ai21': {
        'maxTokens': 512,
        'temperature': 0.7,
        'topP': 0.9,
    },
    'cohere': {
        'max_tokens': 512,
        'temperature': 0.7,
        'p': 0.9,
    },
    'mistral': {
        'max_tokens': 512,
        'temperature': 0.7,
        'top_p': 0.9,
    },
    'stability': {
        'cfg_scale': 10,
        'seed': 42,
        'steps': 50,
        'width': 1024,
        'height': 1024,
    }
}

# Pricing Information (USD per 1000 tokens, approximate as of 2025)
PRICING = {
    'llama_3_8b': {'input': 0.0003, 'output': 0.0006},
    'llama_3_70b': {'input': 0.00195, 'output': 0.00256},
    'llama_2_13b': {'input': 0.00075, 'output': 0.001},
    'claude_3_opus': {'input': 0.015, 'output': 0.075},
    'claude_3_sonnet': {'input': 0.003, 'output': 0.015},
    'claude_3_haiku': {'input': 0.00025, 'output': 0.00125},
    'titan_express': {'input': 0.0002, 'output': 0.0006},
    'titan_lite': {'input': 0.00015, 'output': 0.0002},
    'titan_embed': {'input': 0.0001, 'output': 0},
    'jurassic_ultra': {'input': 0.0188, 'output': 0.0188},
    'jurassic_mid': {'input': 0.0125, 'output': 0.0125},
    'cohere_command': {'input': 0.0015, 'output': 0.002},
    'cohere_command_light': {'input': 0.0005, 'output': 0.0015},
    'mistral_7b': {'input': 0.00025, 'output': 0.00025},
    'mistral_8x7b': {'input': 0.00045, 'output': 0.0007},
    'mistral_large': {'input': 0.002, 'output': 0.006},
    'stable_diffusion_xl': {'per_image': 0.04},
}

# Use Case Recommendations
USE_CASES = {
    'general_purpose': ['llama_3_8b', 'claude_3_haiku', 'titan_express'],
    'high_quality': ['llama_3_70b', 'claude_3_sonnet', 'claude_3_opus'],
    'cost_effective': ['titan_lite', 'cohere_command_light', 'mistral_7b'],
    'embeddings': ['titan_embed', 'cohere_embed_english'],
    'code_generation': ['llama_3_70b', 'claude_3_sonnet'],
    'creative_writing': ['claude_3_opus', 'llama_3_70b'],
    'fast_responses': ['claude_3_haiku', 'llama_3_8b', 'titan_lite'],
    'multilingual': ['cohere_embed_multilingual', 'claude_3_sonnet'],
}

# Rate Limits (approximate, check AWS documentation)
RATE_LIMITS = {
    'requests_per_minute': {
        'default': 100,
        'claude_3_opus': 50,
        'stable_diffusion': 10,
    },
    'tokens_per_minute': {
        'default': 100000,
        'claude_3_opus': 40000,
    }
}

# Retry Configuration
RETRY_CONFIG = {
    'max_attempts': 3,
    'initial_delay': 1,  # seconds
    'backoff_multiplier': 2,
    'max_delay': 60,  # seconds
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': 'bedrock_examples.log',
    'console_output': True,
}

# Output Configuration
OUTPUT_CONFIG = {
    'save_responses': True,
    'output_directory': './outputs',
    'response_format': 'json',  # json, text, or both
    'include_metadata': True,
}

# Copyright Information
COPYRIGHT = """
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

def get_model_id(model_name: str) -> str:
    """
    Get the full model ID from a short name
    
    Args:
        model_name: Short model name (e.g., 'llama_3_8b')
        
    Returns:
        Full model ID string
    """
    return MODEL_IDS.get(model_name, '')

def get_default_params(model_family: str) -> dict:
    """
    Get default parameters for a model family
    
    Args:
        model_family: Model family name (e.g., 'llama', 'claude')
        
    Returns:
        Dictionary of default parameters
    """
    return DEFAULT_PARAMS.get(model_family, {})

def estimate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """
    Estimate the cost for a model invocation
    
    Args:
        model_name: Short model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Estimated cost in USD
    """
    pricing = PRICING.get(model_name, {'input': 0.001, 'output': 0.002})
    
    if 'per_image' in pricing:
        return pricing['per_image']
    
    input_cost = (input_tokens / 1000) * pricing.get('input', 0)
    output_cost = (output_tokens / 1000) * pricing.get('output', 0)
    
    return input_cost + output_cost

def get_recommended_models(use_case: str) -> list:
    """
    Get recommended models for a specific use case
    
    Args:
        use_case: Use case name (e.g., 'general_purpose', 'high_quality')
        
    Returns:
        List of recommended model names
    """
    return USE_CASES.get(use_case, [])


if __name__ == "__main__":
    print(COPYRIGHT)
    print("\nAvailable Model Families:")
    for family in DEFAULT_PARAMS.keys():
        print(f"  - {family}")
    
    print("\nAvailable Use Cases:")
    for use_case in USE_CASES.keys():
        print(f"  - {use_case}")
    
    print("\nExample Cost Calculation:")
    cost = estimate_cost('llama_3_8b', 1000, 500)
    print(f"  Llama 3 8B (1000 input, 500 output tokens): ${cost:.6f}")
