"""
OpenAI API Example
==================
This example shows how to use OpenAI's GPT models through their API.

Requirements:
    pip install openai

Setup:
    1. Get your API key from https://platform.openai.com/api-keys
    2. Set it as an environment variable: export OPENAI_API_KEY='your-key-here'
    Or pass it directly to the client (not recommended for production)

Available Models:
    - gpt-4o (GPT-4 Optimized - Latest)
    - gpt-4o-mini (Smaller, faster GPT-4)
    - gpt-4-turbo (GPT-4 Turbo)
    - gpt-4 (GPT-4)
    - gpt-3.5-turbo (GPT-3.5)
"""

import os
from openai import OpenAI


def create_openai_client():
    """Create and return an OpenAI client"""
    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )


def basic_example():
    """Basic example of using OpenAI API"""
    client = create_openai_client()
    
    print("Sending request to OpenAI...")
    
    # Create a chat completion
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Explain quantum computing in simple terms."
            }
        ]
    )
    
    # Print the response
    print("\nGPT's response:")
    print(response.choices[0].message.content)
    
    # Print usage information
    print(f"\n--- Usage Statistics ---")
    print(f"Input tokens: {response.usage.prompt_tokens}")
    print(f"Output tokens: {response.usage.completion_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")
    print(f"Model: {response.model}")


def streaming_example():
    """Example of streaming responses for real-time output"""
    client = create_openai_client()
    
    print("Streaming response from OpenAI...\n")
    
    stream = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        stream=True,
        messages=[
            {
                "role": "user",
                "content": "Write a short poem about artificial intelligence."
            }
        ]
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
    
    print("\n")


def multi_turn_conversation():
    """Example of a multi-turn conversation"""
    client = create_openai_client()
    
    messages = [
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ]
    
    # First turn
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=messages
    )
    
    assistant_message = response.choices[0].message.content
    
    print("User: What is the capital of France?")
    print(f"GPT: {assistant_message}\n")
    
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
        model="gpt-4o",
        max_tokens=1024,
        messages=messages
    )
    
    print("User: What is its population?")
    print(f"GPT: {response.choices[0].message.content}")


def system_prompt_example():
    """Example using system prompts"""
    client = create_openai_client()
    
    print("Using system prompt to set GPT's behavior...\n")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that always responds in the style of Shakespeare. Use Elizabethan English."
            },
            {
                "role": "user",
                "content": "Tell me about machine learning."
            }
        ]
    )
    
    print("User: Tell me about machine learning.")
    print(f"GPT (as Shakespeare): {response.choices[0].message.content}")


def with_temperature_example():
    """Example showing different temperature settings"""
    client = create_openai_client()
    
    print("=== Low Temperature (0.2) - More Focused ===")
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=200,
        temperature=0.2,
        messages=[
            {
                "role": "user",
                "content": "Give me a creative name for a tech startup."
            }
        ]
    )
    print(response.choices[0].message.content)
    
    print("\n=== High Temperature (1.5) - More Creative ===")
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=200,
        temperature=1.5,
        messages=[
            {
                "role": "user",
                "content": "Give me a creative name for a tech startup."
            }
        ]
    )
    print(response.choices[0].message.content)


def function_calling_example():
    """Example of function calling (tool use)"""
    client = create_openai_client()
    
    # Define a function
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
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    print("Demonstrating function calling...\n")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": "What's the weather like in Boston?"
            }
        ],
        tools=tools,
        tool_choice="auto"
    )
    
    # Check if the model wants to call a function
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        print(f"GPT wants to call function: {tool_call.function.name}")
        print(f"With arguments: {tool_call.function.arguments}")
    else:
        print(f"GPT response: {response.choices[0].message.content}")


def vision_example():
    """Example of vision capabilities (image understanding)"""
    client = create_openai_client()
    
    print("Demonstrating vision capabilities...\n")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What's in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                        }
                    }
                ]
            }
        ]
    )
    
    print(f"GPT's description: {response.choices[0].message.content}")


def json_mode_example():
    """Example of JSON mode for structured outputs"""
    client = create_openai_client()
    
    print("Requesting JSON-formatted response...\n")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that outputs in JSON format."
            },
            {
                "role": "user",
                "content": "List 3 programming languages and their use cases in JSON format."
            }
        ]
    )
    
    print(response.choices[0].message.content)


def main():
    """Run all examples"""
    print("=== Basic Example ===")
    basic_example()
    
    print("\n\n=== Streaming Example ===")
    streaming_example()
    
    print("\n\n=== Multi-turn Conversation ===")
    multi_turn_conversation()
    
    print("\n\n=== System Prompt Example ===")
    system_prompt_example()
    
    print("\n\n=== Temperature Examples ===")
    with_temperature_example()
    
    print("\n\n=== Function Calling Example ===")
    function_calling_example()
    
    print("\n\n=== Vision Example ===")
    vision_example()
    
    print("\n\n=== JSON Mode Example ===")
    json_mode_example()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Installed the openai package: pip install openai")
        print("3. Have sufficient credits in your OpenAI account")
