"""
AWS Bedrock Claude API Example
===============================
This example shows how to use Claude through AWS Bedrock.

Requirements:
    pip install boto3

Setup:
    1. Configure AWS credentials (one of the following):
       - AWS CLI: aws configure
       - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
       - IAM role (if running on EC2/ECS/Lambda)
    
    2. Ensure you have access to Claude models in Bedrock:
       - Go to AWS Bedrock console
       - Request model access for Claude models
       - Wait for approval (usually instant)

Available Claude Models on Bedrock:
    - anthropic.claude-3-5-sonnet-20241022-v2:0
    - anthropic.claude-3-5-sonnet-20240620-v1:0
    - anthropic.claude-3-opus-20240229-v1:0
    - anthropic.claude-3-sonnet-20240229-v1:0
    - anthropic.claude-3-haiku-20240307-v1:0
"""

import json
import boto3
from typing import Dict, Any

def create_bedrock_client(region: str = "us-east-1"):
    """Create and return a Bedrock Runtime client"""
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=region
    )


def invoke_claude(
    client,
    prompt: str,
    model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
    max_tokens: int = 1024,
    temperature: float = 1.0
) -> Dict[str, Any]:
    """
    Invoke Claude model on AWS Bedrock
    
    Args:
        client: Bedrock runtime client
        prompt: The user's message
        model_id: Claude model ID
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0-1)
    
    Returns:
        Response dictionary
    """
    # Prepare the request body
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    # Invoke the model
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body)
    )
    
    # Parse the response
    response_body = json.loads(response['body'].read())
    return response_body


def stream_claude(
    client,
    prompt: str,
    model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
    max_tokens: int = 1024
):
    """
    Stream Claude responses from AWS Bedrock
    
    Args:
        client: Bedrock runtime client
        prompt: The user's message
        model_id: Claude model ID
        max_tokens: Maximum tokens to generate
    """
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    # Invoke model with streaming
    response = client.invoke_model_with_response_stream(
        modelId=model_id,
        body=json.dumps(request_body)
    )
    
    # Process the stream
    stream = response.get('body')
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                chunk_data = json.loads(chunk.get('bytes').decode())
                
                # Handle different event types
                if chunk_data['type'] == 'content_block_delta':
                    if 'delta' in chunk_data and 'text' in chunk_data['delta']:
                        print(chunk_data['delta']['text'], end='', flush=True)
                elif chunk_data['type'] == 'message_stop':
                    print()  # New line at the end


def multi_turn_conversation_bedrock(client):
    """Example of multi-turn conversation on Bedrock"""
    messages = []
    
    # First turn
    messages.append({
        "role": "user",
        "content": "What are the three primary colors?"
    })
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": messages
    }
    
    response = client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(request_body)
    )
    
    response_body = json.loads(response['body'].read())
    assistant_message = response_body['content'][0]['text']
    
    print("User: What are the three primary colors?")
    print(f"Claude: {assistant_message}\n")
    
    # Add assistant's response to conversation
    messages.append({
        "role": "assistant",
        "content": [{"type": "text", "text": assistant_message}]
    })
    
    # Second turn
    messages.append({
        "role": "user",
        "content": "What colors do you get when you mix them?"
    })
    
    request_body["messages"] = messages
    
    response = client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(request_body)
    )
    
    response_body = json.loads(response['body'].read())
    assistant_message = response_body['content'][0]['text']
    
    print("User: What colors do you get when you mix them?")
    print(f"Claude: {assistant_message}")


def main():
    # Initialize Bedrock client
    print("Initializing AWS Bedrock client...")
    client = create_bedrock_client(region="us-east-1")
    
    # Basic invocation
    print("\n=== Basic Example ===")
    response = invoke_claude(
        client,
        prompt="Explain machine learning in one paragraph.",
        max_tokens=512
    )
    
    print("Claude's response:")
    print(response['content'][0]['text'])
    
    print(f"\n--- Usage Statistics ---")
    print(f"Input tokens: {response['usage']['input_tokens']}")
    print(f"Output tokens: {response['usage']['output_tokens']}")
    print(f"Model: {response.get('model', 'N/A')}")
    
    # Streaming example
    print("\n\n=== Streaming Example ===")
    print("Claude's streaming response:")
    stream_claude(
        client,
        prompt="Write a haiku about cloud computing."
    )
    
    # Multi-turn conversation
    print("\n\n=== Multi-turn Conversation ===")
    multi_turn_conversation_bedrock(client)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Configured AWS credentials")
        print("2. Requested access to Claude models in AWS Bedrock")
        print("3. Set the correct AWS region")
