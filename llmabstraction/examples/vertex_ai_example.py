"""
Google Cloud Vertex AI Claude API Example
==========================================
This example shows how to use Claude through Google Cloud Vertex AI.

Requirements:
    pip install google-cloud-aiplatform anthropic[vertex]

Setup:
    1. Create a Google Cloud project
    2. Enable Vertex AI API
    3. Set up authentication (one of the following):
       - gcloud auth application-default login
       - Set GOOGLE_APPLICATION_CREDENTIALS environment variable to service account key
    
    4. Request access to Claude models in Vertex AI Model Garden
    
    5. Set your project ID and region:
       export GOOGLE_CLOUD_PROJECT='your-project-id'
       export GOOGLE_CLOUD_REGION='us-east5'

Available Claude Models on Vertex AI:
    - claude-3-5-sonnet-v2@20241022
    - claude-3-5-sonnet@20240620
    - claude-3-opus@20240229
    - claude-3-sonnet@20240229
    - claude-3-haiku@20240307
"""

import os
from anthropic import AnthropicVertex


def create_vertex_client(
    project_id: str = None,
    region: str = "us-east5"
):
    """
    Create and return a Vertex AI client for Claude
    
    Args:
        project_id: Google Cloud project ID (defaults to GOOGLE_CLOUD_PROJECT env var)
        region: Google Cloud region (defaults to us-east5)
    
    Returns:
        AnthropicVertex client
    """
    if project_id is None:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("Project ID must be provided or set in GOOGLE_CLOUD_PROJECT")
    
    return AnthropicVertex(
        project_id=project_id,
        region=region
    )


def basic_example():
    """Basic example of using Claude on Vertex AI"""
    # Initialize client
    client = create_vertex_client()
    
    # Create a message
    print("Sending request to Claude on Vertex AI...")
    message = client.messages.create(
        model="claude-3-5-sonnet-v2@20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Explain what Google Cloud Vertex AI is in simple terms."
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
    print(f"Model: {message.model}")


def streaming_example():
    """Example of streaming responses"""
    client = create_vertex_client()
    
    print("Streaming response from Claude on Vertex AI...\n")
    
    with client.messages.stream(
        model="claude-3-5-sonnet-v2@20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Write a short story about a robot learning to paint."
            }
        ]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    
    print("\n")


def multi_turn_conversation():
    """Example of a multi-turn conversation"""
    client = create_vertex_client()
    
    messages = [
        {
            "role": "user",
            "content": "What is BigQuery?"
        }
    ]
    
    # First turn
    response = client.messages.create(
        model="claude-3-5-sonnet-v2@20241022",
        max_tokens=1024,
        messages=messages
    )
    
    print("User: What is BigQuery?")
    print(f"Claude: {response.content[0].text}\n")
    
    # Add assistant's response to conversation
    messages.append({
        "role": "assistant",
        "content": response.content[0].text
    })
    
    # Second turn
    messages.append({
        "role": "user",
        "content": "How does it differ from traditional databases?"
    })
    
    response = client.messages.create(
        model="claude-3-5-sonnet-v2@20241022",
        max_tokens=1024,
        messages=messages
    )
    
    print("User: How does it differ from traditional databases?")
    print(f"Claude: {response.content[0].text}")


def system_prompt_example():
    """Example using system prompts"""
    client = create_vertex_client()
    
    print("Using system prompt to set Claude's behavior...\n")
    
    message = client.messages.create(
        model="claude-3-5-sonnet-v2@20241022",
        max_tokens=512,
        system="You are a helpful assistant that always responds in the style of a pirate. Use pirate slang and vocabulary.",
        messages=[
            {
                "role": "user",
                "content": "Tell me about cloud computing."
            }
        ]
    )
    
    print("User: Tell me about cloud computing.")
    print(f"Claude (as pirate): {message.content[0].text}")


def with_temperature_example():
    """Example showing different temperature settings"""
    client = create_vertex_client()
    
    print("=== Low Temperature (0.2) - More Focused ===")
    message = client.messages.create(
        model="claude-3-5-sonnet-v2@20241022",
        max_tokens=200,
        temperature=0.2,
        messages=[
            {
                "role": "user",
                "content": "Give me a creative name for a cloud storage service."
            }
        ]
    )
    print(message.content[0].text)
    
    print("\n=== High Temperature (1.0) - More Creative ===")
    message = client.messages.create(
        model="claude-3-5-sonnet-v2@20241022",
        max_tokens=200,
        temperature=1.0,
        messages=[
            {
                "role": "user",
                "content": "Give me a creative name for a cloud storage service."
            }
        ]
    )
    print(message.content[0].text)


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


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Set up Google Cloud authentication")
        print("2. Set GOOGLE_CLOUD_PROJECT environment variable")
        print("3. Enabled Vertex AI API")
        print("4. Requested access to Claude models in Vertex AI")
        print("5. Installed required packages: pip install google-cloud-aiplatform anthropic[vertex]")
