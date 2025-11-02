"""
AWS Bedrock Advanced Examples - Streaming, Embeddings, and Image Generation

Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com

Advanced features demonstrated:
- Streaming responses with Llama and Claude models
- Text embeddings with Amazon Titan
- Image generation with Stability AI
- Multi-turn conversations
- Token counting and cost estimation
"""

import boto3
import json
from typing import Dict, Any, Generator
import base64


class BedrockAdvancedExamples:
    """
    Advanced AWS Bedrock examples including streaming and embeddings
    
    Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name
        )
    
    # ==================== STREAMING EXAMPLES ====================
    
    def stream_llama_3_response(self, prompt: str) -> None:
        """
        Example 1: Streaming response from Llama 3 model
        Useful for real-time applications
        """
        model_id = "meta.llama3-70b-instruct-v1:0"
        
        payload = {
            "prompt": prompt,
            "max_gen_len": 1024,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        print(f"\n{'='*60}")
        print(f"STREAMING: Llama 3 70B Instruct")
        print(f"{'='*60}")
        print("Response: ", end='', flush=True)
        
        try:
            response = self.bedrock_runtime.invoke_model_with_response_stream(
                modelId=model_id,
                body=json.dumps(payload)
            )
            
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_data = json.loads(chunk.get('bytes').decode())
                        if 'generation' in chunk_data:
                            print(chunk_data['generation'], end='', flush=True)
            print("\n")
        except Exception as e:
            print(f"\nError: {str(e)}")
    
    def stream_claude_response(self, prompt: str) -> None:
        """
        Example 2: Streaming response from Claude 3
        """
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        print(f"\n{'='*60}")
        print(f"STREAMING: Claude 3 Sonnet")
        print(f"{'='*60}")
        print("Response: ", end='', flush=True)
        
        try:
            response = self.bedrock_runtime.invoke_model_with_response_stream(
                modelId=model_id,
                body=json.dumps(payload)
            )
            
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_data = json.loads(chunk.get('bytes').decode())
                        if chunk_data.get('type') == 'content_block_delta':
                            if 'delta' in chunk_data and 'text' in chunk_data['delta']:
                                print(chunk_data['delta']['text'], end='', flush=True)
            print("\n")
        except Exception as e:
            print(f"\nError: {str(e)}")
    
    # ==================== EMBEDDINGS EXAMPLES ====================
    
    def generate_titan_embeddings(self, text: str) -> list:
        """
        Example 3: Generate text embeddings using Amazon Titan
        Useful for semantic search, clustering, and similarity matching
        """
        model_id = "amazon.titan-embed-text-v1"
        
        payload = {
            "inputText": text
        }
        
        print(f"\n{'='*60}")
        print(f"EMBEDDINGS: Amazon Titan Embed Text")
        print(f"{'='*60}")
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(payload)
            )
            
            response_body = json.loads(response['body'].read())
            embeddings = response_body.get('embedding', [])
            
            print(f"Input text: {text}")
            print(f"Embedding dimension: {len(embeddings)}")
            print(f"First 10 values: {embeddings[:10]}")
            
            return embeddings
        except Exception as e:
            print(f"Error: {str(e)}")
            return []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Example 4: Calculate semantic similarity between two texts
        """
        import numpy as np
        
        emb1 = self.generate_titan_embeddings(text1)
        emb2 = self.generate_titan_embeddings(text2)
        
        if emb1 and emb2:
            # Calculate cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            similarity = dot_product / (norm1 * norm2)
            
            print(f"\n{'='*60}")
            print(f"SIMILARITY CALCULATION")
            print(f"{'='*60}")
            print(f"Text 1: {text1}")
            print(f"Text 2: {text2}")
            print(f"Cosine Similarity: {similarity:.4f}")
            
            return similarity
        return 0.0
    
    # ==================== IMAGE GENERATION ====================
    
    def generate_image_stable_diffusion(self, prompt: str, output_path: str = "generated_image.png") -> str:
        """
        Example 5: Generate images using Stability AI Stable Diffusion
        """
        model_id = "stability.stable-diffusion-xl-v1"
        
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1.0
                }
            ],
            "cfg_scale": 10,
            "seed": 42,
            "steps": 50,
            "width": 1024,
            "height": 1024
        }
        
        print(f"\n{'='*60}")
        print(f"IMAGE GENERATION: Stable Diffusion XL")
        print(f"{'='*60}")
        print(f"Prompt: {prompt}")
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(payload)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract and decode the image
            artifacts = response_body.get('artifacts', [])
            if artifacts:
                image_data = base64.b64decode(artifacts[0].get('base64'))
                
                # Save the image
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                
                print(f"Image saved to: {output_path}")
                return output_path
            else:
                print("No image generated")
                return ""
        except Exception as e:
            print(f"Error: {str(e)}")
            return ""
    
    # ==================== MULTI-TURN CONVERSATION ====================
    
    def multi_turn_conversation_llama(self) -> None:
        """
        Example 6: Multi-turn conversation with Llama maintaining context
        """
        model_id = "meta.llama3-8b-instruct-v1:0"
        
        conversation_history = []
        
        print(f"\n{'='*60}")
        print(f"MULTI-TURN CONVERSATION: Llama 3")
        print(f"{'='*60}")
        
        turns = [
            "What is machine learning?",
            "Can you give me an example?",
            "How is it different from traditional programming?"
        ]
        
        for i, user_input in enumerate(turns, 1):
            print(f"\nTurn {i}")
            print(f"User: {user_input}")
            
            # Build context from conversation history
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
            full_prompt = f"{context}\nUser: {user_input}\nAssistant:"
            
            payload = {
                "prompt": full_prompt,
                "max_gen_len": 512,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            try:
                response = self.bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps(payload)
                )
                
                response_body = json.loads(response['body'].read())
                assistant_response = response_body.get('generation', '')
                
                print(f"Assistant: {assistant_response}")
                
                # Update conversation history
                conversation_history.append({"role": "User", "content": user_input})
                conversation_history.append({"role": "Assistant", "content": assistant_response})
                
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def multi_turn_conversation_claude(self) -> None:
        """
        Example 7: Multi-turn conversation with Claude (native support)
        """
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        messages = []
        
        print(f"\n{'='*60}")
        print(f"MULTI-TURN CONVERSATION: Claude 3 Haiku")
        print(f"{'='*60}")
        
        turns = [
            "What is quantum computing?",
            "How does it differ from classical computing?",
            "What are some practical applications?"
        ]
        
        for i, user_input in enumerate(turns, 1):
            print(f"\nTurn {i}")
            print(f"User: {user_input}")
            
            # Add user message
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "messages": messages,
                "temperature": 0.7
            }
            
            try:
                response = self.bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps(payload)
                )
                
                response_body = json.loads(response['body'].read())
                assistant_response = response_body.get('content', [{}])[0].get('text', '')
                
                print(f"Assistant: {assistant_response}")
                
                # Add assistant response to messages
                messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                
            except Exception as e:
                print(f"Error: {str(e)}")
    
    # ==================== TOKEN COUNTING AND COST ESTIMATION ====================
    
    def estimate_tokens_and_cost(self, text: str, model_id: str) -> Dict[str, Any]:
        """
        Example 8: Estimate token count and cost for a given text
        Note: This is a rough estimate
        """
        # Approximate token count (rough estimate: 1 token ≈ 4 characters)
        estimated_tokens = len(text) // 4
        
        # Approximate costs per 1000 tokens (as of 2024, check AWS for current pricing)
        pricing = {
            "meta.llama3-8b-instruct-v1:0": {"input": 0.0003, "output": 0.0006},
            "meta.llama3-70b-instruct-v1:0": {"input": 0.00195, "output": 0.00256},
            "anthropic.claude-3-sonnet-20240229-v1:0": {"input": 0.003, "output": 0.015},
            "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.00025, "output": 0.00125},
            "amazon.titan-text-express-v1": {"input": 0.0002, "output": 0.0006},
        }
        
        model_pricing = pricing.get(model_id, {"input": 0.001, "output": 0.002})
        estimated_input_cost = (estimated_tokens / 1000) * model_pricing["input"]
        estimated_output_cost = (estimated_tokens / 1000) * model_pricing["output"]
        
        result = {
            "text_length": len(text),
            "estimated_tokens": estimated_tokens,
            "estimated_input_cost_usd": round(estimated_input_cost, 6),
            "estimated_output_cost_usd": round(estimated_output_cost, 6),
            "model_id": model_id
        }
        
        print(f"\n{'='*60}")
        print(f"TOKEN AND COST ESTIMATION")
        print(f"{'='*60}")
        print(f"Model: {model_id}")
        print(f"Text length: {result['text_length']} characters")
        print(f"Estimated tokens: {result['estimated_tokens']}")
        print(f"Estimated input cost: ${result['estimated_input_cost_usd']}")
        print(f"Estimated output cost: ${result['estimated_output_cost_usd']}")
        
        return result
    
    # ==================== BATCH PROCESSING ====================
    
    def batch_process_with_llama(self, prompts: list) -> list:
        """
        Example 9: Batch process multiple prompts with Llama
        """
        model_id = "meta.llama3-8b-instruct-v1:0"
        results = []
        
        print(f"\n{'='*60}")
        print(f"BATCH PROCESSING: Llama 3 8B")
        print(f"{'='*60}")
        print(f"Processing {len(prompts)} prompts...")
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\nProcessing prompt {i}/{len(prompts)}: {prompt[:50]}...")
            
            payload = {
                "prompt": prompt,
                "max_gen_len": 256,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            try:
                response = self.bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps(payload)
                )
                
                response_body = json.loads(response['body'].read())
                result = response_body.get('generation', '')
                results.append({
                    "prompt": prompt,
                    "response": result,
                    "status": "success"
                })
                print(f"Response: {result[:100]}...")
                
            except Exception as e:
                results.append({
                    "prompt": prompt,
                    "response": "",
                    "status": "error",
                    "error": str(e)
                })
                print(f"Error: {str(e)}")
        
        return results


def main():
    """
    Demonstrate advanced Bedrock features
    
    Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
    """
    print("="*80)
    print("AWS BEDROCK ADVANCED EXAMPLES")
    print("Copyright 2025-2030 all rights reserved")
    print("Ashutosh Sinha")
    print("Email: ajsinha@gmail.com")
    print("="*80)
    
    bedrock = BedrockAdvancedExamples(region_name='us-east-1')
    
    try:
        # Example 1: Streaming with Llama
        bedrock.stream_llama_3_response(
            "Write a short poem about artificial intelligence."
        )
        
        # Example 2: Streaming with Claude
        bedrock.stream_claude_response(
            "Explain the concept of neural networks in 3 sentences."
        )
        
        # Example 3 & 4: Embeddings and similarity
        bedrock.generate_titan_embeddings("Machine learning is fascinating")
        bedrock.calculate_similarity(
            "I love programming",
            "I enjoy coding"
        )
        
        # Example 5: Image generation
        bedrock.generate_image_stable_diffusion(
            "A futuristic city with flying cars at sunset",
            "/home/claude/generated_image.png"
        )
        
        # Example 6 & 7: Multi-turn conversations
        bedrock.multi_turn_conversation_llama()
        bedrock.multi_turn_conversation_claude()
        
        # Example 8: Cost estimation
        bedrock.estimate_tokens_and_cost(
            "This is a sample text for token counting and cost estimation.",
            "meta.llama3-8b-instruct-v1:0"
        )
        
        # Example 9: Batch processing
        batch_prompts = [
            "What is Python?",
            "What is JavaScript?",
            "What is Java?"
        ]
        bedrock.batch_process_with_llama(batch_prompts)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nMake sure you have:")
        print("1. AWS credentials configured")
        print("2. Bedrock model access enabled")
        print("3. Required IAM permissions")
    
    print("\n" + "="*80)
    print("ADVANCED EXAMPLES COMPLETED")
    print("Copyright 2025-2030 all rights reserved")
    print("Ashutosh Sinha, Email: ajsinha@gmail.com")
    print("="*80)


if __name__ == "__main__":
    main()
