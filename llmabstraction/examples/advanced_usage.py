"""
Advanced Usage Example
Demonstrates advanced features including multiple llmproviders and models

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
"""

import os
from llmabstraction.llmutils import initialize_system


def compare_models_example(system):
    """Compare responses from different models."""
    print("\n" + "="*60)
    print("Comparing Different Models")
    print("="*60)
    
    prompt = "Explain quantum computing in one sentence."
    
    # Test with different models (using mock for demonstration)
    models_to_test = [
        ('mock', 'mock-model'),
        ('mock', 'mock-model-fast'),
    ]
    
    for provider, model in models_to_test:
        try:
            client = system.create_client(provider_name=provider, model_name=model)
            response = client.generate(prompt)
            
            print(f"\n{provider}/{model}:")
            print(f"  Response: {response.content}")
            print(f"  Usage: {response.usage}")
            
        except Exception as e:
            print(f"\n{provider}/{model}: Error - {str(e)}")


def custom_parameters_example(system):
    """Use custom generation parameters."""
    print("\n" + "="*60)
    print("Custom Generation Parameters")
    print("="*60)
    
    client = system.create_client()
    
    # Set default parameters for all generations
    client.set_default_params(temperature=0.7, max_tokens=100)
    
    prompt = "Write a creative story opener."
    
    # Override with specific parameters
    response = client.generate(
        prompt,
        temperature=1.2,  # More creative
        max_tokens=150
    )
    
    print(f"\nPrompt: {prompt}")
    print(f"Response: {response.content}")


def history_management_example(system):
    """Manage interaction history."""
    print("\n" + "="*60)
    print("History Management")
    print("="*60)
    
    # Create client with custom history size
    client = system.create_client(history_size=10)
    
    # Generate some interactions
    prompts = [
        "What is Python?",
        "What are its main features?",
        "How does it compare to Java?",
        "What are popular Python frameworks?"
    ]
    
    for prompt in prompts:
        response = client.generate(prompt, use_history=True)
        print(f"\nQ: {prompt}")
        print(f"A: {response.content}")
    
    # View history
    print(f"\n\nCurrent history size: {client.history.size()}")
    
    # Get last 2 interactions
    recent_history = client.get_history(n=2)
    print(f"\nLast 2 interactions:")
    for i, interaction in enumerate(recent_history, 1):
        print(f"\n{i}. Prompt: {interaction['prompt'][:50]}...")
        print(f"   Response: {interaction['response'][:50]}...")
    
    # Clear history
    client.clear_history()
    print(f"\nHistory cleared. New size: {client.history.size()}")


def error_handling_example(system):
    """Demonstrate error handling."""
    print("\n" + "="*60)
    print("Error Handling")
    print("="*60)
    
    # Try to use non-existent model
    try:
        client = system.create_client(
            provider_name='mock',
            model_name='non-existent-model'
        )
    except ValueError as e:
        print(f"\nExpected error caught: {str(e)}")
    
    # Create valid client
    client = system.create_client()
    
    # Generate with error (mock won't error, but shows pattern)
    response = client.generate("Test prompt")
    
    if response.error:
        print(f"\nGeneration error: {response.error}")
    else:
        print(f"\nGeneration successful: {response.content}")


def model_information_example(system):
    """Display detailed model information."""
    print("\n" + "="*60)
    print("Detailed Model Information")
    print("="*60)
    
    # Get information about specific models
    models_of_interest = [
        'claude-3-5-sonnet-20241022',
        'meta.llama3-1-405b-instruct-v1:0',
        'gemini-1.5-pro-latest',
        'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'
    ]
    
    for model_name in models_of_interest:
        info = system.get_model_info(model_name)
        if info:
            print(f"\n{'='*50}")
            print(f"Model: {model_name}")
            print(f"{'='*50}")
            print(f"Provider: {info.get('provider')}")
            print(f"Version: {info.get('version')}")
            print(f"Description: {info.get('description')}")
            print(f"Context Window: {info.get('context_window'):,} tokens")
            print(f"Max Output: {info.get('max_output_tokens'):,} tokens")
            print(f"Strengths: {', '.join(info.get('strengths', []))}")
            print(f"Use Cases: {', '.join(info.get('use_cases', []))}")
            print(f"Cost (per 1M tokens):")
            print(f"  Input:  ${info.get('cost_per_1m_input_tokens')}")
            print(f"  Output: ${info.get('cost_per_1m_output_tokens')}")
            print(f"Free Tier: {'Yes' if info.get('free_tier') else 'No'}")


def provider_comparison_example(system):
    """Compare different llmproviders."""
    print("\n" + "="*60)
    print("Provider Comparison")
    print("="*60)
    
    providers = system.list_providers()
    
    for provider_name in providers:
        info = system.get_provider_info(provider_name)
        models = system.list_models(provider_name)
        
        print(f"\n{'='*50}")
        print(f"Provider: {provider_name.upper()}")
        print(f"{'='*50}")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Requires API Key: {info.get('requires_api_key', False)}")
        print(f"Enabled: {info.get('enabled', False)}")
        print(f"Available Models: {len(models)}")
        print(f"Website: {info.get('website', 'N/A')}")
        
        if models:
            print(f"\nSample Models:")
            for model in models[:3]:  # Show first 3
                print(f"  - {model}")
            if len(models) > 3:
                print(f"  ... and {len(models) - 3} more")


def streaming_with_history_example(system):
    """Combine streaming with history."""
    print("\n" + "="*60)
    print("Streaming with Conversation History")
    print("="*60)
    
    client = system.create_client()
    
    # First interaction
    response = client.generate("Tell me about artificial intelligence.")
    print(f"\nQ1: Tell me about artificial intelligence.")
    print(f"A1: {response.content}")
    
    # Second interaction with streaming
    print(f"\nQ2: What are its applications?")
    print(f"A2: ", end="", flush=True)
    
    for chunk in client.generate_stream(
        "What are its applications?",
        use_history=True
    ):
        print(chunk, end="", flush=True)
    
    print(f"\n\nTotal interactions in history: {client.history.size()}")


def main():
    """Run all advanced examples."""
    
    # Initialize system
    print("Initializing LLM Abstraction System...")
    system = initialize_system(log_level="INFO")
    
    print(f"\nSystem initialized with {len(system.list_providers())} llmproviders")
    print(f"Total models available: {len(system.list_models())}")
    
    # Run examples
    compare_models_example(system)
    custom_parameters_example(system)
    history_management_example(system)
    error_handling_example(system)
    model_information_example(system)
    provider_comparison_example(system)
    streaming_with_history_example(system)
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
