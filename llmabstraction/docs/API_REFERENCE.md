# API Reference

**Copyright © 2025-2030 All rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Core Classes

### LLMSystem

Main system class for initialization and management.

#### Methods

**`initialize(config_dir=None, log_level="INFO")`**
- Initialize the system
- Args:
  - `config_dir`: Configuration directory path
  - `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**`create_client(provider_name=None, model_name=None, **kwargs)`**
- Create an LLM client
- Args:
  - `provider_name`: Provider name (uses default if None)
  - `model_name`: Model name (uses default if None)
  - `**kwargs`: Additional configuration
- Returns: `LLMClient` instance

**`list_providers()`**
- List all available providers
- Returns: List of provider names

**`list_models(provider_name=None)`**
- List available models
- Args:
  - `provider_name`: Provider name (None for all)
- Returns: List of model names

**`get_model_info(model_name)`**
- Get detailed model information
- Args:
  - `model_name`: Name of the model
- Returns: Dictionary with model metadata

**`get_provider_info(provider_name)`**
- Get provider information
- Args:
  - `provider_name`: Name of the provider
- Returns: Dictionary with provider metadata

### LLMClient

Main client for interacting with LLM models.

#### Initialization

```python
client = system.create_client(
    provider_name='anthropic',
    model_name='claude-3-5-sonnet-20241022',
    history_size=50
)
```

#### Methods

**`generate(prompt, use_history=False, save_to_history=True, **kwargs)`**
- Generate a response
- Args:
  - `prompt`: Input prompt string
  - `use_history`: Include conversation history
  - `save_to_history`: Save interaction to history
  - `**kwargs`: Additional parameters (temperature, max_tokens, etc.)
- Returns: `LLMResponse` object

**`generate_stream(prompt, use_history=False, save_to_history=True, **kwargs)`**
- Generate a streaming response
- Args: Same as `generate()`
- Yields: String chunks

**`chat(messages, save_to_history=True, **kwargs)`**
- Chat completion with message list
- Args:
  - `messages`: List of message dictionaries `[{"role": "user", "content": "..."}]`
  - `save_to_history`: Save interaction
  - `**kwargs`: Additional parameters
- Returns: `LLMResponse` object

**`chat_stream(messages, save_to_history=True, **kwargs)`**
- Streaming chat completion
- Args: Same as `chat()`
- Yields: String chunks

**`multi_shot_generate(prompt, n_shots=3, **kwargs)`**
- Multi-shot learning from history
- Args:
  - `prompt`: Input prompt
  - `n_shots`: Number of history interactions to include
  - `**kwargs`: Additional parameters
- Returns: `LLMResponse` object

**`set_default_params(**kwargs)`**
- Set default generation parameters
- Args: Parameter key-value pairs

**`get_history(n=None)`**
- Get interaction history
- Args:
  - `n`: Number of recent interactions (None for all)
- Returns: List of interaction dictionaries

**`clear_history()`**
- Clear all interaction history

**`get_model_info()`**
- Get underlying model information
- Returns: Model info dictionary

### LLMResponse

Response object from LLM interactions.

#### Attributes

- `content` (str): Generated text content
- `model` (str): Model that generated the response
- `provider` (str): Provider name
- `usage` (dict): Token usage statistics
  - `input_tokens`: Number of input tokens
  - `output_tokens`: Number of output tokens
- `metadata` (dict): Additional response metadata
- `timestamp` (datetime): When response was generated
- `error` (str): Error message if request failed

#### Usage

```python
response = client.generate("Your prompt")

if response.error:
    print(f"Error: {response.error}")
else:
    print(f"Content: {response.content}")
    print(f"Model: {response.model}")
    print(f"Tokens used: {response.usage}")
```

### LLMInteractionHistory

Manages conversation history for multi-shot learning.

#### Methods

**`add_interaction(prompt, response)`**
- Add an interaction to history
- Args:
  - `prompt`: Input prompt
  - `response`: LLMResponse object

**`get_history(n=None)`**
- Get interaction history
- Args:
  - `n`: Number of recent interactions
- Returns: List of interaction dictionaries

**`get_as_messages(n=None)`**
- Get history as chat messages
- Args:
  - `n`: Number of recent interactions
- Returns: List of message dictionaries

**`clear()`**
- Clear all history

**`size()`**
- Get current history size
- Returns: Integer

**`is_empty()`**
- Check if history is empty
- Returns: Boolean

## Configuration

### Models Configuration (JSON)

Structure of `config/models_config.json`:

```json
{
  "defaults": {
    "provider": "mock",
    "model": "mock-model",
    "history_size": 50,
    "fallback_to_mock": true
  },
  "providers": {
    "provider_name": {
      "name": "provider_name",
      "description": "Provider description",
      "enabled": true,
      "requires_api_key": true,
      "api_key_env": "PROVIDER_API_KEY",
      "models": ["model1", "model2"]
    }
  },
  "models": {
    "model_name": {
      "provider": "provider_name",
      "name": "model_name",
      "description": "Model description",
      "version": "1.0",
      "context_window": 4096,
      "max_output_tokens": 2048,
      "strengths": ["strength1", "strength2"],
      "use_cases": ["use_case1"],
      "cost_per_1m_input_tokens": 1.0,
      "cost_per_1m_output_tokens": 2.0,
      "free_tier": false
    }
  }
}
```

### Application Properties

Common properties in `config/application.properties`:

```properties
# Application
app.name=LLM Abstraction System
app.version=1.0.0

# Defaults
default.provider=mock
default.model=mock-model
default.history_size=50

# API Keys (or use environment variables)
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
TOGETHER_API_KEY=

# Performance
max_retries=3
timeout_seconds=60
```

## Generation Parameters

Common parameters for `generate()`, `chat()`, and related methods:

- `temperature` (float): Randomness in generation (0.0-2.0)
  - Lower = more deterministic
  - Higher = more creative/random
  - Default varies by provider

- `max_tokens` (int): Maximum tokens to generate
  - Default varies by model

- `top_p` (float): Nucleus sampling (0.0-1.0)
  - Alternative to temperature
  - Default: 1.0

- `top_k` (int): Top-K sampling
  - Limits vocabulary to top K tokens
  - Provider-specific

- `stop` (list): Stop sequences
  - Generation stops when these sequences are encountered

- `frequency_penalty` (float): Penalize frequent tokens
  - Reduces repetition
  - Provider-specific

- `presence_penalty` (float): Penalize tokens that have appeared
  - Encourages topic diversity
  - Provider-specific

### Example

```python
response = client.generate(
    "Write a creative story",
    temperature=1.2,
    max_tokens=1000,
    top_p=0.9,
    stop=["The End"]
)
```

## Error Handling

All methods return `LLMResponse` objects that may contain errors:

```python
response = client.generate("Your prompt")

if response.error:
    # Handle error
    print(f"Error: {response.error}")
    # Fallback logic here
else:
    # Process successful response
    print(response.content)
```

Common error scenarios:
- Invalid API key
- Rate limiting
- Model not available
- Network errors
- Invalid parameters

## Provider-Specific Notes

### Anthropic
- Requires `ANTHROPIC_API_KEY`
- Best for: Complex reasoning, code generation
- Models support up to 200K context window

### AWS Bedrock
- Requires AWS credentials (boto3 configuration)
- Access to Meta Llama, Mistral, Claude, Titan
- Set region in configuration

### Google AI
- Requires `GOOGLE_API_KEY`
- Gemini models support up to 2M context window
- Free tier available for Flash models

### Together AI
- Requires `TOGETHER_API_KEY`
- Fast inference for open source models
- Cost-effective for high volume

### Hugging Face
- Requires `HUGGINGFACE_API_KEY`
- Access to thousands of models
- Free tier available

### Grok
- Requires `GROK_API_KEY`
- Real-time information capability
- X platform integration

## Best Practices

1. **Always check for errors**
   ```python
   if response.error:
       # Handle error
   ```

2. **Use history for context**
   ```python
   response = client.generate(prompt, use_history=True)
   ```

3. **Set appropriate parameters**
   ```python
   client.set_default_params(temperature=0.7, max_tokens=1000)
   ```

4. **Monitor token usage**
   ```python
   print(f"Tokens used: {response.usage}")
   ```

5. **Clear history periodically**
   ```python
   if client.history.size() > 100:
       client.clear_history()
   ```

## Examples

See `examples/` directory for:
- `basic_usage.py`: Getting started examples
- `advanced_usage.py`: Advanced patterns
- Provider-specific examples

---

**Copyright © 2025-2030 All rights reserved Ashutosh Sinha**
