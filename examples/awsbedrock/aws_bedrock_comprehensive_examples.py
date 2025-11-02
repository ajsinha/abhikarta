"""
AWS Bedrock Comprehensive Examples with Multiple Models

Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com

This script demonstrates how to use various AWS Bedrock models including:
- Meta Llama models
- Anthropic Claude models
- Amazon Titan models
- AI21 Labs Jurassic models
- Cohere Command models
- Mistral AI models
- Stability AI models
"""

import boto3
import json
from typing import Dict, Any
import os


class BedrockModelExamples:
    """
    A comprehensive class to demonstrate AWS Bedrock model usage
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize Bedrock client
        
        Args:
            region_name: AWS region where Bedrock is available
        """
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name
        )
        
    def invoke_model(self, model_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic method to invoke any Bedrock model
        
        Args:
            model_id: The model identifier
            payload: The request payload
            
        Returns:
            The model response
        """
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(payload)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body
        except Exception as e:
            print(f"Error invoking model {model_id}: {str(e)}")
            return {"error": str(e)}
    
    # ==================== META LLAMA MODELS ====================
    
    def example_llama_3_8b_instruct(self, prompt: str) -> str:
        """
        Example 1: Meta Llama 3 8B Instruct
        Cost: Pay-per-use
        """
        model_id = "meta.llama3-8b-instruct-v1:0"
        
        payload = {
            "prompt": prompt,
            "max_gen_len": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: Llama 3 8B Instruct")
        print(f"{'='*60}")
        print(f"Response: {response.get('generation', 'No response')}")
        return response.get('generation', '')
    
    def example_llama_3_70b_instruct(self, prompt: str) -> str:
        """
        Example 2: Meta Llama 3 70B Instruct
        Cost: Pay-per-use (higher than 8B)
        """
        model_id = "meta.llama3-70b-instruct-v1:0"
        
        payload = {
            "prompt": prompt,
            "max_gen_len": 512,
            "temperature": 0.5,
            "top_p": 0.9
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: Llama 3 70B Instruct")
        print(f"{'='*60}")
        print(f"Response: {response.get('generation', 'No response')}")
        return response.get('generation', '')
    
    def example_llama_2_13b_chat(self, prompt: str) -> str:
        """
        Example 3: Meta Llama 2 13B Chat
        Cost: Pay-per-use
        """
        model_id = "meta.llama2-13b-chat-v1"
        
        payload = {
            "prompt": prompt,
            "max_gen_len": 512,
            "temperature": 0.6,
            "top_p": 0.9
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: Llama 2 13B Chat")
        print(f"{'='*60}")
        print(f"Response: {response.get('generation', 'No response')}")
        return response.get('generation', '')
    
    # ==================== ANTHROPIC CLAUDE MODELS ====================
    
    def example_claude_3_sonnet(self, prompt: str) -> str:
        """
        Example 4: Anthropic Claude 3 Sonnet
        Cost: Pay-per-use
        """
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: Claude 3 Sonnet")
        print(f"{'='*60}")
        content = response.get('content', [{}])[0].get('text', 'No response')
        print(f"Response: {content}")
        return content
    
    def example_claude_3_haiku(self, prompt: str) -> str:
        """
        Example 5: Anthropic Claude 3 Haiku (Fast and cost-effective)
        Cost: Lower cost option
        """
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: Claude 3 Haiku")
        print(f"{'='*60}")
        content = response.get('content', [{}])[0].get('text', 'No response')
        print(f"Response: {content}")
        return content
    
    # ==================== AMAZON TITAN MODELS ====================
    
    def example_titan_text_express(self, prompt: str) -> str:
        """
        Example 6: Amazon Titan Text Express
        Cost: Pay-per-use (AWS native model)
        """
        model_id = "amazon.titan-text-express-v1"
        
        payload = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: Amazon Titan Text Express")
        print(f"{'='*60}")
        result = response.get('results', [{}])[0].get('outputText', 'No response')
        print(f"Response: {result}")
        return result
    
    def example_titan_text_lite(self, prompt: str) -> str:
        """
        Example 7: Amazon Titan Text Lite (Cost-effective)
        Cost: Lower cost option
        """
        model_id = "amazon.titan-text-lite-v1"
        
        payload = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: Amazon Titan Text Lite")
        print(f"{'='*60}")
        result = response.get('results', [{}])[0].get('outputText', 'No response')
        print(f"Response: {result}")
        return result
    
    # ==================== AI21 LABS MODELS ====================
    
    def example_ai21_jurassic_2_ultra(self, prompt: str) -> str:
        """
        Example 8: AI21 Labs Jurassic-2 Ultra
        Cost: Pay-per-use
        """
        model_id = "ai21.j2-ultra-v1"
        
        payload = {
            "prompt": prompt,
            "maxTokens": 512,
            "temperature": 0.7,
            "topP": 0.9
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: AI21 Jurassic-2 Ultra")
        print(f"{'='*60}")
        result = response.get('completions', [{}])[0].get('data', {}).get('text', 'No response')
        print(f"Response: {result}")
        return result
    
    def example_ai21_jurassic_2_mid(self, prompt: str) -> str:
        """
        Example 9: AI21 Labs Jurassic-2 Mid (Cost-effective)
        Cost: Lower cost option
        """
        model_id = "ai21.j2-mid-v1"
        
        payload = {
            "prompt": prompt,
            "maxTokens": 512,
            "temperature": 0.7,
            "topP": 0.9
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: AI21 Jurassic-2 Mid")
        print(f"{'='*60}")
        result = response.get('completions', [{}])[0].get('data', {}).get('text', 'No response')
        print(f"Response: {result}")
        return result
    
    # ==================== COHERE MODELS ====================
    
    def example_cohere_command_text(self, prompt: str) -> str:
        """
        Example 10: Cohere Command Text
        Cost: Pay-per-use
        """
        model_id = "cohere.command-text-v14"
        
        payload = {
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.7,
            "p": 0.9
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: Cohere Command Text")
        print(f"{'='*60}")
        result = response.get('generations', [{}])[0].get('text', 'No response')
        print(f"Response: {result}")
        return result
    
    def example_cohere_command_light(self, prompt: str) -> str:
        """
        Example 11: Cohere Command Light (Faster and cost-effective)
        Cost: Lower cost option
        """
        model_id = "cohere.command-light-text-v14"
        
        payload = {
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.7,
            "p": 0.9
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: Cohere Command Light")
        print(f"{'='*60}")
        result = response.get('generations', [{}])[0].get('text', 'No response')
        print(f"Response: {result}")
        return result
    
    # ==================== MISTRAL AI MODELS ====================
    
    def example_mistral_7b_instruct(self, prompt: str) -> str:
        """
        Example 12: Mistral 7B Instruct
        Cost: Pay-per-use
        """
        model_id = "mistral.mistral-7b-instruct-v0:2"
        
        payload = {
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: Mistral 7B Instruct")
        print(f"{'='*60}")
        result = response.get('outputs', [{}])[0].get('text', 'No response')
        print(f"Response: {result}")
        return result
    
    def example_mistral_large(self, prompt: str) -> str:
        """
        Example 13: Mistral Large
        Cost: Pay-per-use (premium model)
        """
        model_id = "mistral.mistral-large-2402-v1:0"
        
        payload = {
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = self.invoke_model(model_id, payload)
        print(f"\n{'='*60}")
        print(f"MODEL: Mistral Large")
        print(f"{'='*60}")
        result = response.get('outputs', [{}])[0].get('text', 'No response')
        print(f"Response: {result}")
        return result


def main():
    """
    Main function to demonstrate all models
    
    Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
    """
    print("="*80)
    print("AWS BEDROCK COMPREHENSIVE MODEL EXAMPLES")
    print("Copyright 2025-2030 all rights reserved")
    print("Ashutosh Sinha")
    print("Email: ajsinha@gmail.com")
    print("="*80)
    
    # Initialize the examples class
    bedrock = BedrockModelExamples(region_name='us-east-1')
    
    # Sample prompt to test all models
    prompt = "Explain quantum computing in simple terms."
    
    print("\n\nTesting all available models with prompt:")
    print(f"'{prompt}'")
    print("\n" + "="*80)
    
    # Test all models
    try:
        # Meta Llama Models (REQUIRED)
        print("\n" + "="*80)
        print("TESTING META LLAMA MODELS")
        print("="*80)
        bedrock.example_llama_3_8b_instruct(prompt)
        bedrock.example_llama_3_70b_instruct(prompt)
        bedrock.example_llama_2_13b_chat(prompt)
        
        # Anthropic Claude Models
        print("\n" + "="*80)
        print("TESTING ANTHROPIC CLAUDE MODELS")
        print("="*80)
        bedrock.example_claude_3_sonnet(prompt)
        bedrock.example_claude_3_haiku(prompt)
        
        # Amazon Titan Models
        print("\n" + "="*80)
        print("TESTING AMAZON TITAN MODELS")
        print("="*80)
        bedrock.example_titan_text_express(prompt)
        bedrock.example_titan_text_lite(prompt)
        
        # AI21 Labs Models
        print("\n" + "="*80)
        print("TESTING AI21 LABS MODELS")
        print("="*80)
        bedrock.example_ai21_jurassic_2_ultra(prompt)
        bedrock.example_ai21_jurassic_2_mid(prompt)
        
        # Cohere Models
        print("\n" + "="*80)
        print("TESTING COHERE MODELS")
        print("="*80)
        bedrock.example_cohere_command_text(prompt)
        bedrock.example_cohere_command_light(prompt)
        
        # Mistral AI Models
        print("\n" + "="*80)
        print("TESTING MISTRAL AI MODELS")
        print("="*80)
        bedrock.example_mistral_7b_instruct(prompt)
        bedrock.example_mistral_large(prompt)
        
    except Exception as e:
        print(f"\nError during execution: {str(e)}")
        print("\nNote: Make sure you have:")
        print("1. AWS credentials configured")
        print("2. Appropriate IAM permissions for Bedrock")
        print("3. Model access enabled in AWS Bedrock console")
    
    print("\n" + "="*80)
    print("EXAMPLES COMPLETED")
    print("Copyright 2025-2030 all rights reserved")
    print("Ashutosh Sinha, Email: ajsinha@gmail.com")
    print("="*80)


if __name__ == "__main__":
    main()
