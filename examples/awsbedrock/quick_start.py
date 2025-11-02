"""
AWS Bedrock Quick Start Guide

Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com

This script provides a quick way to get started with AWS Bedrock.
Run this after configuring your AWS credentials.
"""

import boto3
import json
from bedrock_config import MODEL_IDS, get_default_params, estimate_cost


class QuickStart:
    """
    Quick start guide for AWS Bedrock
    
    Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
    """
    
    def __init__(self):
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'
        )
    
    def check_credentials(self):
        """
        Check if AWS credentials are configured correctly
        """
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            print("✓ AWS Credentials verified")
            print(f"  Account ID: {identity['Account']}")
            print(f"  User ARN: {identity['Arn']}")
            return True
        except Exception as e:
            print(f"✗ AWS Credentials error: {str(e)}")
            return False
    
    def test_model(self, model_id: str, prompt: str):
        """
        Test a specific model
        """
        print(f"\nTesting model: {model_id}")
        print(f"Prompt: {prompt}")
        
        try:
            if 'llama' in model_id:
                payload = {
                    "prompt": prompt,
                    "max_gen_len": 256,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
                response = self.bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps(payload)
                )
                result = json.loads(response['body'].read())
                print(f"✓ Response: {result.get('generation', '')[:200]}...")
                
            elif 'claude' in model_id:
                payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 256,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                response = self.bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps(payload)
                )
                result = json.loads(response['body'].read())
                print(f"✓ Response: {result.get('content', [{}])[0].get('text', '')[:200]}...")
                
            elif 'titan' in model_id:
                payload = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": 256,
                        "temperature": 0.7,
                        "topP": 0.9
                    }
                }
                response = self.bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps(payload)
                )
                result = json.loads(response['body'].read())
                print(f"✓ Response: {result.get('results', [{}])[0].get('outputText', '')[:200]}...")
            
            return True
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False
    
    def run_quick_test(self):
        """
        Run a quick test of the most common models
        """
        print("="*80)
        print("AWS BEDROCK QUICK START TEST")
        print("Copyright 2025-2030 all rights reserved")
        print("Ashutosh Sinha, Email: ajsinha@gmail.com")
        print("="*80)
        
        # Step 1: Check credentials
        print("\n[STEP 1] Checking AWS credentials...")
        if not self.check_credentials():
            print("\nPlease configure AWS credentials and try again.")
            print("Run: aws configure")
            return
        
        # Step 2: Test a few models
        print("\n[STEP 2] Testing available models...")
        
        test_prompt = "What is artificial intelligence? Answer in one sentence."
        
        models_to_test = [
            ('llama_3_8b', 'Meta Llama 3 8B'),
            ('claude_3_haiku', 'Claude 3 Haiku'),
            ('titan_express', 'Amazon Titan Express'),
        ]
        
        successful_models = []
        failed_models = []
        
        for model_key, model_name in models_to_test:
            print(f"\n--- Testing {model_name} ---")
            model_id = MODEL_IDS.get(model_key)
            
            if self.test_model(model_id, test_prompt):
                successful_models.append(model_name)
            else:
                failed_models.append(model_name)
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"\n✓ Successful: {len(successful_models)} models")
        for model in successful_models:
            print(f"  - {model}")
        
        if failed_models:
            print(f"\n✗ Failed: {len(failed_models)} models")
            for model in failed_models:
                print(f"  - {model}")
            print("\nNote: Failed models may need access enabled in AWS Bedrock console.")
            print("Visit: https://console.aws.amazon.com/bedrock/")
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("\n1. If models failed, enable them in AWS Bedrock console:")
        print("   - Go to Bedrock > Model access")
        print("   - Request access for desired models")
        
        print("\n2. Run comprehensive examples:")
        print("   python aws_bedrock_comprehensive_examples.py")
        
        print("\n3. Try advanced features:")
        print("   python aws_bedrock_advanced_examples.py")
        
        print("\n4. Read the documentation:")
        print("   cat README.md")
        
        print("\n" + "="*80)
        print("Copyright 2025-2030 all rights reserved")
        print("Ashutosh Sinha, Email: ajsinha@gmail.com")
        print("="*80)


def setup_guide():
    """
    Display setup guide for first-time users
    """
    print("="*80)
    print("AWS BEDROCK SETUP GUIDE")
    print("Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com")
    print("="*80)
    
    print("\n[PREREQUISITE 1] Install required packages")
    print("  pip install -r requirements.txt")
    print("  or")
    print("  pip install boto3 botocore python-dotenv")
    
    print("\n[PREREQUISITE 2] Configure AWS credentials")
    print("  Option A - AWS CLI:")
    print("    aws configure")
    print("  Option B - Environment variables:")
    print("    export AWS_ACCESS_KEY_ID='your-key'")
    print("    export AWS_SECRET_ACCESS_KEY='your-secret'")
    print("    export AWS_DEFAULT_REGION='us-east-1'")
    
    print("\n[PREREQUISITE 3] Enable model access")
    print("  1. Go to AWS Console > Bedrock")
    print("  2. Click 'Model access' in left sidebar")
    print("  3. Click 'Manage model access'")
    print("  4. Select desired models:")
    print("     - Meta Llama 3 8B Instruct (recommended)")
    print("     - Claude 3 Haiku (recommended)")
    print("     - Amazon Titan Express (recommended)")
    print("     - Any other models you want to use")
    print("  5. Click 'Request model access'")
    print("  6. Wait for approval (usually instant)")
    
    print("\n[STEP 1] Run quick test")
    print("  python quick_start.py")
    
    print("\n[STEP 2] Try basic examples")
    print("  python aws_bedrock_comprehensive_examples.py")
    
    print("\n[STEP 3] Explore advanced features")
    print("  python aws_bedrock_advanced_examples.py")
    
    print("\n" + "="*80)
    print("For detailed information, see README.md")
    print("="*80)


def main():
    """
    Main entry point
    
    Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        setup_guide()
    else:
        quick_start = QuickStart()
        quick_start.run_quick_test()


if __name__ == "__main__":
    main()
