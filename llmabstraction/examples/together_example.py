"""
Together AI API Example
========================
This example shows how to use Together AI's API for accessing open-source models.

Requirements:
    pip install together

Setup:
    1. Get your API key from https://api.together.xyz/settings/api-keys
    2. Set it as an environment variable: export TOGETHER_API_KEY='your-key-here'
    Or pass it directly to the client (not recommended for production)

Popular Models Available:
    Chat Models:
    - meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo
    - meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
    - meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
    - mistralai/Mixtral-8x22B-Instruct-v0.1
    - Qwen/Qwen2.5-72B-Instruct-Turbo
    - google/gemma-2-27b-it
    
    Code Models:
    - Qwen/Qwen2.5-Coder-32B-Instruct
    - codellama/CodeLlama-70b-Instruct-hf
    
    Image Generation:
    - black-forest-labs/FLUX.1-schnell
    - stabilityai/stable-diffusion-xl-base-1.0
"""

import os
from together import Together


def create_together_client():
    """Create and return a Together AI client"""
    return Together(
        api_key=os.environ.get("TOGETHER_API_KEY")
    )


def basic_example():
    """Basic example of using Together AI"""
    client = create_together_client()
    
    print("Sending request to Together AI...")
    
    # Create a chat completion
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Explain quantum computing in simple terms."
            }
        ]
    )
    
    # Print the response
    print("\nModel's response:")
    print(response.choices[0].message.content)
    
    # Print usage information
    print(f"\n--- Usage Statistics ---")
    print(f"Input tokens: {response.usage.prompt_tokens}")
    print(f"Output tokens: {response.usage.completion_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")
    print(f"Model: {response.model}")


def streaming_example():
    """Example of streaming responses for real-time output"""
    client = create_together_client()
    
    print("Streaming response from Together AI...\n")
    
    stream = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        max_tokens=1024,
        stream=True,
        messages=[
            {
                "role": "user",
                "content": "Write a short poem about open-source AI."
            }
        ]
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
    
    print("\n")


def multi_turn_conversation():
    """Example of a multi-turn conversation"""
    client = create_together_client()
    
    messages = [
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ]
    
    # First turn
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        max_tokens=1024,
        messages=messages
    )
    
    assistant_message = response.choices[0].message.content
    
    print("User: What is the capital of France?")
    print(f"Model: {assistant_message}\n")
    
    # Add assistant's response to conversation
    messages.append({
        "role": "assistant",
        "content": assistant_message
    })
    
    # Second turn
    messages.append({
        "role": "user",
        "content": "What is its population?"
    })
    
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        max_tokens=1024,
        messages=messages
    )
    
    print("User: What is its population?")
    print(f"Model: {response.choices[0].message.content}")


def system_prompt_example():
    """Example using system prompts"""
    client = create_together_client()
    
    print("Using system prompt to set model's behavior...\n")
    
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        max_tokens=512,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that always responds like a pirate. Use pirate slang and vocabulary."
            },
            {
                "role": "user",
                "content": "Tell me about machine learning."
            }
        ]
    )
    
    print("User: Tell me about machine learning.")
    print(f"Model (as pirate): {response.choices[0].message.content}")


def compare_models_example():
    """Compare responses from different models"""
    client = create_together_client()
    
    prompt = "Explain recursion in programming in one sentence."
    models = [
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "Qwen/Qwen2.5-72B-Instruct-Turbo"
    ]
    
    print("Comparing different models...\n")
    
    for model in models:
        response = client.chat.completions.create(
            model=model,
            max_tokens=200,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        print(f"=== {model.split('/')[-1]} ===")
        print(response.choices[0].message.content)
        print()


def code_generation_example():
    """Example using a code-specialized model"""
    client = create_together_client()
    
    print("Using code-specialized model...\n")
    
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Write a Python function to calculate the Fibonacci sequence using memoization."
            }
        ]
    )
    
    print("Code generation result:")
    print(response.choices[0].message.content)


def image_generation_example():
    """Example of image generation (if you have access)"""
    client = create_together_client()
    
    print("Generating an image...\n")
    
    try:
        response = client.images.generate(
            prompt="A serene landscape with mountains and a lake at sunset, digital art",
            model="black-forest-labs/FLUX.1-schnell",
            width=1024,
            height=768,
            steps=4,
            n=1
        )
        
        print(f"Image URL: {response.data[0].url}")
        print("Note: Image URL is temporary and will expire")
    except Exception as e:
        print(f"Image generation not available or error occurred: {e}")


def with_temperature_example():
    """Example showing different temperature settings"""
    client = create_together_client()
    
    prompt = "Give me a creative name for a space exploration company."
    
    print("=== Low Temperature (0.1) - More Focused ===")
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        max_tokens=200,
        temperature=0.1,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    print(response.choices[0].message.content)
    
    print("\n=== High Temperature (1.2) - More Creative ===")
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        max_tokens=200,
        temperature=1.2,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    print(response.choices[0].message.content)


def function_calling_example():
    """Example of function calling with Together AI"""
    client = create_together_client()
    
    # Define tools/functions
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"]
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    print("Demonstrating function calling...\n")
    
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        messages=[
            {
                "role": "user",
                "content": "What's the weather like in New York?"
            }
        ],
        tools=tools,
        tool_choice="auto"
    )
    
    # Check if the model wants to call a function
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        print(f"Model wants to call function: {tool_call.function.name}")
        print(f"With arguments: {tool_call.function.arguments}")
    else:
        print(f"Model response: {response.choices[0].message.content}")


def list_available_models():
    """List available models on Together AI"""
    client = create_together_client()
    
    print("Fetching available models...\n")
    
    try:
        models = client.models.list()
        
        print("=== Chat Models ===")
        for model in models:
            if 'instruct' in model.id.lower() or 'chat' in model.id.lower():
                print(f"- {model.id}")
                if hasattr(model, 'context_length'):
                    print(f"  Context length: {model.context_length}")
                print()
                
        print("\n=== Some Popular Models ===")
        popular = [
            "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "mistralai/Mixtral-8x22B-Instruct-v0.1",
            "Qwen/Qwen2.5-72B-Instruct-Turbo"
        ]
        for model_id in popular:
            print(f"- {model_id}")
            
    except Exception as e:
        print(f"Could not fetch models: {e}")


def main():
    """Run all examples"""
    print("=== List Available Models ===")
    list_available_models()
    
    print("\n\n=== Basic Example ===")
    basic_example()
    
    print("\n\n=== Streaming Example ===")
    streaming_example()
    
    print("\n\n=== Multi-turn Conversation ===")
    multi_turn_conversation()
    
    print("\n\n=== System Prompt Example ===")
    system_prompt_example()
    
    print("\n\n=== Temperature Examples ===")
    with_temperature_example()
    
    print("\n\n=== Compare Models ===")
    compare_models_example()
    
    print("\n\n=== Code Generation Example ===")
    code_generation_example()
    
    print("\n\n=== Function Calling Example ===")
    function_calling_example()
    
    print("\n\n=== Image Generation Example ===")
    image_generation_example()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Set TOGETHER_API_KEY environment variable")
        print("2. Installed the together package: pip install together")
        print("3. Have sufficient credits in your Together AI account")
        print("4. Get API key from: https://api.together.xyz/settings/api-keys")
