# LLM Abstraction System

**Copyright © 2025-2030 All rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Overview

The LLM Abstraction System is a comprehensive, production-ready framework for interacting with Large Language Models (LLMs) from multiple providers through a unified, configuration-driven interface. It abstracts away provider-specific implementation details while providing powerful features like interaction history, multi-shot learning, and seamless provider switching.

### Key Features

- **🔌 Multi-Provider Support**: Works with Anthropic, AWS Bedrock, Together AI, Google, Hugging Face, Grok, and more
- **🎯 Unified Interface**: Single API for all LLM interactions regardless of provider
- **📝 Configuration-Driven**: JSON configuration for models and providers, properties files for settings
- **💾 Interaction History**: Built-in conversation history management for multi-shot learning
- **🔄 Seamless Switching**: Easy switching between providers and models
- **🛡️ Robust Error Handling**: Comprehensive error handling with fallback mechanisms
- **🧪 Mock Provider**: Built-in mock provider for testing without API calls
- **🏗️ Design Patterns**: Implements Factory, Singleton, Facade, and Delegate patterns
- **📊 Rich Model Metadata**: Detailed information about models including costs, strengths, and use cases
- **🔐 Secure Configuration**: API keys from environment variables or properties files, never in code

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LLM Client                           │
│  (User-facing API with convenience methods)             │
└─────────────────┬───────────────────────────────────────┘
                  │
         ┌────────▼────────┐
         │   LLM Facade    │
         │  (Unified API)  │
         └────────┬────────┘
                  │
    ┌─────────────┴──────────────┐
    │      LLM Provider          │
    │ (Provider-specific logic)   │
    └─────────────┬──────────────┘
                  │
    ┌─────────────▼──────────────────────────────┐
    │  Anthropic │ AWS │ Google │ Together │ ... │
    └────────────────────────────────────────────┘
```

### Core Components

1. **LLMProvider**: Abstract base class for provider implementations
2. **LLMFacade**: Unified interface for model interactions
3. **LLMClient**: Main client with convenience methods and history
4. **LLMProviderFactory**: Singleton factory for creating providers
5. **LLMClientFactory**: Singleton factory for creating clients
6. **ConfigLoader**: Configuration management
7. **LLMSystem**: System initializer and manager

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd llm_abstraction_system

# Install dependencies
pip install anthropic boto3 google-generativeai huggingface-hub together requests
```

### Basic Usage

```python
from llm_abstraction_system.utils import initialize_system

# Initialize the system
system = initialize_system()

# Create a client (uses default mock provider)
client = system.create_client()

# Generate a response
response = client.generate("What is machine learning?")
print(response.content)

# Use with conversation history
response = client.generate("Tell me more", use_history=True)
print(response.content)

# Streaming response
for chunk in client.generate_stream("Write a poem about AI"):
    print(chunk, end="", flush=True)
```

### Using Real Providers

```python
# Set your API key (or use environment variable)
import os
os.environ['ANTHROPIC_API_KEY'] = 'your-api-key'

# Create a client with specific provider and model
client = system.create_client(
    provider_name='anthropic',
    model_name='claude-3-5-sonnet-20241022'
)

response = client.generate("Explain quantum computing")
print(response.content)
```

## Supported Providers and Models

### Anthropic (Claude)
- claude-3-5-sonnet-20241022
- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307

### AWS Bedrock
- **Meta Llama**: llama3-3-70b, llama3-1-405b, llama3-1-70b, llama3-1-8b
- **Amazon Titan**: titan-text-premier, titan-text-express
- **Mistral**: mistral-large, mixtral-8x7b
- **Claude via Bedrock**: Available

### Google AI
- gemini-1.5-pro-latest
- gemini-1.5-flash-latest
- gemini-1.5-flash-8b
- gemini-1.0-pro

### Together AI
- Meta Llama 3.1 (405B, 70B, 8B)
- Mixtral 8x7B
- Qwen 2.5 72B
- DeepSeek LLM 67B

### Hugging Face
- Meta Llama models
- Mistral models
- Microsoft Phi-3
- Qwen models
- Google Gemma

### Grok (xAI)
- grok-beta
- grok-vision-beta

### Mock Provider
- mock-model
- mock-model-large
- mock-model-fast

## Configuration

### API Keys

Set API keys via environment variables or properties file:

```bash
# Environment variables (recommended)
export ANTHROPIC_API_KEY=your-key
export GOOGLE_API_KEY=your-key
export TOGETHER_API_KEY=your-key
export HUGGINGFACE_API_KEY=your-key
export GROK_API_KEY=your-key
```

Or in `config/application.properties`:
```properties
ANTHROPIC_API_KEY=your-key
GOOGLE_API_KEY=your-key
```

### Models Configuration

Edit `config/models_config.json` to:
- Set default provider and model
- Configure model metadata
- Enable/disable providers
- Set cost information

## Advanced Features

### Multi-Shot Learning

```python
client = system.create_client()

# Build context through interactions
client.generate("Python is a programming language")
client.generate("It's known for simplicity")

# Use context for better responses
response = client.multi_shot_generate(
    "What are its main advantages?",
    n_shots=2  # Use last 2 interactions
)
```

### Custom Parameters

```python
# Set default parameters
client.set_default_params(temperature=0.7, max_tokens=1000)

# Override for specific generation
response = client.generate(
    "Write a creative story",
    temperature=1.2,  # More creative
    max_tokens=2000
)
```

### Chat Format

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Explain photosynthesis"},
]

response = client.chat(messages)
```

### History Management

```python
# View history
history = client.get_history(n=5)  # Last 5 interactions

# Get as chat messages
messages = client.history.get_as_messages(n=3)

# Clear history
client.clear_history()
```

### Error Handling

```python
response = client.generate("Your prompt")

if response.error:
    print(f"Error occurred: {response.error}")
else:
    print(f"Response: {response.content}")
    print(f"Usage: {response.usage}")
```

## Model Information

```python
# Get detailed model information
info = system.get_model_info('claude-3-5-sonnet-20241022')
print(f"Description: {info['description']}")
print(f"Context Window: {info['context_window']}")
print(f"Strengths: {info['strengths']}")
print(f"Cost: ${info['cost_per_1m_input_tokens']}/1M tokens")

# List all models
all_models = system.list_models()

# List models for specific provider
anthropic_models = system.list_models('anthropic')
```

## Testing

The system includes a mock provider for testing without making real API calls:

```python
# Use mock provider (default)
client = system.create_client()

# Or explicitly
client = system.create_client(
    provider_name='mock',
    model_name='mock-model'
)
```

## Examples

See the `examples/` directory for comprehensive examples:

- `basic_usage.py`: Simple examples to get started
- `advanced_usage.py`: Advanced features and patterns
- `provider_specific.py`: Provider-specific examples

## Project Structure

```
llm_abstraction_system/
├── core/                   # Core abstractions
│   ├── llm_provider.py
│   ├── llm_facade.py
│   ├── llm_client.py
│   ├── llm_provider_factory.py
│   └── llm_client_factory.py
├── providers/              # Provider implementations
│   ├── mock_provider.py
│   ├── anthropic_provider.py
│   ├── bedrock_provider.py
│   ├── together_provider.py
│   ├── google_provider.py
│   ├── huggingface_provider.py
│   └── grok_provider.py
├── config/                 # Configuration files
│   ├── models_config.json
│   └── application.properties
├── utils/                  # Utilities
│   ├── config_loader.py
│   └── system_initializer.py
├── examples/               # Example scripts
│   ├── basic_usage.py
│   └── advanced_usage.py
├── docs/                   # Documentation
└── tests/                  # Test suite
```

## Design Patterns

The system implements several design patterns for maintainability and extensibility:

- **Factory Pattern**: `LLMProviderFactory` and `LLMClientFactory` for object creation
- **Singleton Pattern**: Factories are singletons to ensure single instances
- **Facade Pattern**: `LLMFacade` provides unified interface to diverse models
- **Delegate Pattern**: Client delegates to facade, facade to provider

## Best Practices

1. **API Key Management**: Always use environment variables or secure vaults
2. **Error Handling**: Always check `response.error` before using content
3. **History Management**: Clear history periodically to manage memory
4. **Cost Awareness**: Check model costs before using expensive models
5. **Rate Limiting**: Implement rate limiting for production use
6. **Testing**: Use mock provider for testing

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing patterns
- All tests pass
- Documentation is updated
- Copyright notices are maintained

## License

Copyright © 2025-2030 All rights reserved  
Ashutosh Sinha  
Email: ajsinha@gmail.com

## Support

For questions, issues, or feature requests, please contact:
- Email: ajsinha@gmail.com
- Create an issue in the repository

## Changelog

### Version 1.0.0 (2025)
- Initial release
- Support for 7 major providers
- 50+ models configured
- Comprehensive documentation
- Example code and tests
