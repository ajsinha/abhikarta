"""
Basic Usage Example
Demonstrates simple usage of the LLM abstraction system

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

from llmabstraction.llmutils import initialize_system


def main():
    """Demonstrate basic usage of the LLM system."""
    
    # Initialize the system
    print("Initializing LLM System...")
    system = initialize_system(log_level="INFO")
    
    print(f"\nSystem Status: {system}")
    print(f"Available Providers: {system.list_providers()}")
    
    # Create a client with default provider and model (mock)
    print("\n" + "="*50)
    print("Example 1: Using Default (Mock) Provider")
    print("="*50)
    
    client = system.create_client()
    
    # Simple generation
    response = client.generate("What is the capital of France?")
    print(f"\nPrompt: What is the capital of France?")
    print(f"Response: {response.content}")
    print(f"Model: {response.model}")
    print(f"Provider: {response.provider}")
    
    # With history
    response = client.generate("What is its population?", use_history=True)
    print(f"\nPrompt: What is its population?")
    print(f"Response: {response.content}")
    
    # Check history
    print(f"\nHistory Size: {client.history.size()}")
    
    # Multi-shot example
    print("\n" + "="*50)
    print("Example 2: Multi-shot Learning")
    print("="*50)
    
    # Create a new client
    client2 = system.create_client()
    
    # Add some context through interactions
    client2.generate("Translate 'hello' to Spanish")
    client2.generate("Translate 'goodbye' to Spanish")
    
    # Now use multi-shot
    response = client2.multi_shot_generate(
        "Translate 'thank you' to Spanish",
        n_shots=2
    )
    print(f"\nPrompt: Translate 'thank you' to Spanish")
    print(f"Response: {response.content}")
    
    # Streaming example
    print("\n" + "="*50)
    print("Example 3: Streaming Response")
    print("="*50)
    
    print("\nPrompt: Write a haiku about programming")
    print("Response: ", end="", flush=True)
    
    for chunk in client.generate_stream("Write a haiku about programming"):
        print(chunk, end="", flush=True)
    print("\n")
    
    # Chat format example
    print("\n" + "="*50)
    print("Example 4: Chat Format")
    print("="*50)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ]
    
    response = client.chat(messages)
    print(f"\nChat Response: {response.content}")
    
    # List all models
    print("\n" + "="*50)
    print("Available Models")
    print("="*50)
    
    all_models = system.list_models()
    print(f"\nTotal models: {len(all_models)}")
    
    for model_name in all_models[:10]:  # Show first 10
        model_info = system.get_model_info(model_name)
        print(f"\n{model_name}")
        print(f"  Provider: {model_info.get('provider')}")
        print(f"  Description: {model_info.get('description')}")
        print(f"  Cost: ${model_info.get('cost_per_1m_input_tokens')}/1M input, "
              f"${model_info.get('cost_per_1m_output_tokens')}/1M output")


if __name__ == "__main__":
    main()
