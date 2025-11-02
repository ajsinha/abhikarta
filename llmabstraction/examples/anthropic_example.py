"""
Anthropic Direct API Example
=============================
This example shows how to use Claude through Anthropic's direct API.

Requirements:
    pip install anthropic

Setup:
    1. Get your API key from https://console.anthropic.com
    2. Set it as an environment variable: export ANTHROPIC_API_KEY='your-key-here'
    Or pass it directly to the client (not recommended for production)
"""

import os
from anthropic import Anthropic

def main():
    # Initialize the Anthropic client
    # The client will automatically use the ANTHROPIC_API_KEY environment variable
    client = Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
    
    # Create a message
    print("Sending request to Claude...")
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",  # Latest Claude Sonnet 4.5
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Explain quantum computing in simple terms."
            }
        ]
    )
    
    # Print the response
    print("\nClaude's response:")
    print(message.content[0].text)
    
    # Print usage information
    print(f"\n--- Usage Statistics ---")
    print(f"Input tokens: {message.usage.input_tokens}")
    print(f"Output tokens: {message.usage.output_tokens}")
    

def streaming_example():
    """Example of streaming responses for real-time output"""
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    print("Streaming response from Claude...\n")
    
    with client.messages.stream(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Write a short poem about artificial intelligence."
            }
        ]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    
    print("\n")


def multi_turn_conversation():
    """Example of a multi-turn conversation"""
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    messages = [
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ]
    
    # First turn
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=messages
    )
    
    print("User: What is the capital of France?")
    print(f"Claude: {response.content[0].text}\n")
    
    # Add assistant's response to conversation
    messages.append({
        "role": "assistant",
        "content": response.content[0].text
    })
    
    # Second turn
    messages.append({
        "role": "user",
        "content": "What is its population?"
    })
    
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=messages
    )
    
    print("User: What is its population?")
    print(f"Claude: {response.content[0].text}")


if __name__ == "__main__":
    print("=== Basic Example ===")
    main()
    
    print("\n\n=== Streaming Example ===")
    streaming_example()
    
    print("\n\n=== Multi-turn Conversation ===")
    multi_turn_conversation()
