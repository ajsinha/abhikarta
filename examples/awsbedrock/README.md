# AWS Bedrock Comprehensive Examples

**Copyright 2025-2030 all rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Overview

This repository contains comprehensive Python examples for using AWS Bedrock with 13+ different AI models, including:

### Featured Models

1. **Meta Llama Models** (Required)
   - Llama 3 8B Instruct
   - Llama 3 70B Instruct
   - Llama 2 13B Chat

2. **Anthropic Claude Models**
   - Claude 3 Sonnet
   - Claude 3 Haiku

3. **Amazon Titan Models**
   - Titan Text Express
   - Titan Text Lite
   - Titan Embed Text

4. **AI21 Labs Models**
   - Jurassic-2 Ultra
   - Jurassic-2 Mid

5. **Cohere Models**
   - Command Text
   - Command Light

6. **Mistral AI Models**
   - Mistral 7B Instruct
   - Mistral Large

7. **Stability AI Models**
   - Stable Diffusion XL

---

## Features

### Basic Examples (`aws_bedrock_comprehensive_examples.py`)
- Text generation with 13+ models
- Model comparison examples
- Error handling and best practices
- Cost-effective model options

### Advanced Examples (`aws_bedrock_advanced_examples.py`)
- Streaming responses
- Text embeddings and semantic similarity
- Image generation
- Multi-turn conversations
- Token counting and cost estimation
- Batch processing

---

## Prerequisites

### 1. AWS Account Setup
- Active AWS account
- AWS CLI installed and configured
- IAM user with Bedrock permissions

### 2. Model Access
Enable model access in AWS Console:
1. Navigate to AWS Bedrock Console
2. Go to "Model access" in the left sidebar
3. Request access for desired models
4. Wait for approval (usually instant for most models)

### 3. IAM Permissions
Required IAM policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## Installation

### 1. Clone or Download Files

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install boto3 botocore python-dotenv numpy
```

### 3. Configure AWS Credentials

**Option A: AWS CLI**
```bash
aws configure
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

**Option C: Credentials File**
Create `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = us-east-1
```

---

## Usage

### Basic Examples

Run all model examples:
```bash
python aws_bedrock_comprehensive_examples.py
```

Use specific models in your code:
```python
from aws_bedrock_comprehensive_examples import BedrockModelExamples

# Initialize
bedrock = BedrockModelExamples(region_name='us-east-1')

# Use Llama 3
response = bedrock.example_llama_3_8b_instruct("What is AI?")

# Use Claude 3
response = bedrock.example_claude_3_sonnet("Explain quantum computing")

# Use Titan
response = bedrock.example_titan_text_express("Write a poem")
```

### Advanced Examples

Run all advanced examples:
```bash
python aws_bedrock_advanced_examples.py
```

Use advanced features:
```python
from aws_bedrock_advanced_examples import BedrockAdvancedExamples

# Initialize
bedrock = BedrockAdvancedExamples(region_name='us-east-1')

# Streaming response
bedrock.stream_llama_3_response("Tell me a story")

# Generate embeddings
embeddings = bedrock.generate_titan_embeddings("Sample text")

# Calculate similarity
similarity = bedrock.calculate_similarity("text1", "text2")

# Generate image
bedrock.generate_image_stable_diffusion("A beautiful landscape")

# Multi-turn conversation
bedrock.multi_turn_conversation_claude()
```

---

## Model Details and Pricing

### Meta Llama Models
- **Llama 3 8B**: Fast, cost-effective for most tasks
- **Llama 3 70B**: Higher quality, more expensive
- **Pricing**: ~$0.0003-0.002/1K tokens (varies by model)

### Anthropic Claude Models
- **Claude 3 Sonnet**: Balanced performance and cost
- **Claude 3 Haiku**: Fast and economical
- **Pricing**: ~$0.00025-0.015/1K tokens

### Amazon Titan Models
- **Titan Express**: General purpose, good value
- **Titan Lite**: Cost-optimized
- **Titan Embed**: Text embeddings
- **Pricing**: ~$0.0002-0.0006/1K tokens

### AI21 Labs Models
- **Jurassic-2 Ultra**: High performance
- **Jurassic-2 Mid**: Balanced option
- **Pricing**: ~$0.0125-0.0188/1K tokens

### Cohere Models
- **Command**: Full-featured
- **Command Light**: Faster, cheaper
- **Pricing**: ~$0.0005-0.002/1K tokens

### Mistral AI Models
- **Mistral 7B**: Efficient, open-source
- **Mistral Large**: Premium performance
- **Pricing**: ~$0.0002-0.002/1K tokens

### Stability AI
- **Stable Diffusion XL**: Image generation
- **Pricing**: ~$0.04 per image

*Note: Prices are approximate and subject to change. Check AWS pricing page for current rates.*

---

## Code Examples

### Example 1: Basic Text Generation with Llama
```python
from aws_bedrock_comprehensive_examples import BedrockModelExamples

bedrock = BedrockModelExamples()
response = bedrock.example_llama_3_8b_instruct(
    "Explain machine learning in simple terms"
)
print(response)
```

### Example 2: Streaming Response
```python
from aws_bedrock_advanced_examples import BedrockAdvancedExamples

bedrock = BedrockAdvancedExamples()
bedrock.stream_llama_3_response(
    "Write a story about space exploration"
)
```

### Example 3: Semantic Similarity
```python
from aws_bedrock_advanced_examples import BedrockAdvancedExamples

bedrock = BedrockAdvancedExamples()
similarity = bedrock.calculate_similarity(
    "I love programming",
    "I enjoy coding"
)
print(f"Similarity: {similarity}")
```

### Example 4: Multi-Model Comparison
```python
from aws_bedrock_comprehensive_examples import BedrockModelExamples

bedrock = BedrockModelExamples()
prompt = "What is quantum computing?"

# Compare different models
llama_response = bedrock.example_llama_3_8b_instruct(prompt)
claude_response = bedrock.example_claude_3_haiku(prompt)
titan_response = bedrock.example_titan_text_express(prompt)
```

### Example 5: Batch Processing
```python
from aws_bedrock_advanced_examples import BedrockAdvancedExamples

bedrock = BedrockAdvancedExamples()
prompts = [
    "What is Python?",
    "What is JavaScript?",
    "What is Java?"
]
results = bedrock.batch_process_with_llama(prompts)
```

---

## Troubleshooting

### Common Issues

**1. Access Denied Error**
```
Solution: 
- Check IAM permissions
- Ensure model access is enabled in Bedrock console
- Verify AWS credentials are configured correctly
```

**2. Model Not Found**
```
Solution:
- Request model access in AWS Bedrock console
- Wait for approval (usually instant)
- Check model ID spelling
```

**3. Rate Limiting**
```
Solution:
- Implement exponential backoff
- Reduce request frequency
- Consider upgrading account limits
```

**4. Invalid Region**
```
Solution:
- Use supported regions: us-east-1, us-west-2, etc.
- Check AWS documentation for available regions
```

---

## Best Practices

### 1. Model Selection
- Use **Llama 3 8B** or **Titan Lite** for cost-effective solutions
- Use **Claude 3 Sonnet** or **Llama 3 70B** for complex tasks
- Use **Titan Embed** for embeddings and semantic search
- Use **Claude 3 Haiku** for fast responses

### 2. Cost Optimization
- Cache responses when possible
- Use smaller models for simpler tasks
- Implement token limits
- Monitor usage with AWS Cost Explorer

### 3. Performance
- Use streaming for long responses
- Implement batch processing for multiple requests
- Choose region closest to users
- Consider async processing for non-real-time use

### 4. Security
- Never commit AWS credentials to code
- Use IAM roles when possible
- Implement least privilege access
- Rotate credentials regularly

---

## API Reference

### BedrockModelExamples Class

```python
class BedrockModelExamples:
    def __init__(self, region_name: str = 'us-east-1')
    
    # Llama Models
    def example_llama_3_8b_instruct(self, prompt: str) -> str
    def example_llama_3_70b_instruct(self, prompt: str) -> str
    def example_llama_2_13b_chat(self, prompt: str) -> str
    
    # Claude Models
    def example_claude_3_sonnet(self, prompt: str) -> str
    def example_claude_3_haiku(self, prompt: str) -> str
    
    # Titan Models
    def example_titan_text_express(self, prompt: str) -> str
    def example_titan_text_lite(self, prompt: str) -> str
    
    # AI21 Models
    def example_ai21_jurassic_2_ultra(self, prompt: str) -> str
    def example_ai21_jurassic_2_mid(self, prompt: str) -> str
    
    # Cohere Models
    def example_cohere_command_text(self, prompt: str) -> str
    def example_cohere_command_light(self, prompt: str) -> str
    
    # Mistral Models
    def example_mistral_7b_instruct(self, prompt: str) -> str
    def example_mistral_large(self, prompt: str) -> str
```

### BedrockAdvancedExamples Class

```python
class BedrockAdvancedExamples:
    def __init__(self, region_name: str = 'us-east-1')
    
    def stream_llama_3_response(self, prompt: str) -> None
    def stream_claude_response(self, prompt: str) -> None
    def generate_titan_embeddings(self, text: str) -> list
    def calculate_similarity(self, text1: str, text2: str) -> float
    def generate_image_stable_diffusion(self, prompt: str, output_path: str) -> str
    def multi_turn_conversation_llama(self) -> None
    def multi_turn_conversation_claude(self) -> None
    def estimate_tokens_and_cost(self, text: str, model_id: str) -> Dict
    def batch_process_with_llama(self, prompts: list) -> list
```

---

## Contributing

This is a reference implementation. Feel free to:
- Extend with more models
- Add error handling improvements
- Optimize performance
- Add new use cases

---

## Resources

### AWS Documentation
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/)
- [Model IDs Reference](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)

### Model Documentation
- [Meta Llama](https://ai.meta.com/llama/)
- [Anthropic Claude](https://www.anthropic.com/claude)
- [Amazon Titan](https://aws.amazon.com/bedrock/titan/)
- [AI21 Labs](https://www.ai21.com/)
- [Cohere](https://cohere.com/)
- [Mistral AI](https://mistral.ai/)
- [Stability AI](https://stability.ai/)

### Python Libraries
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

## License and Copyright

**Copyright 2025-2030 all rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

This code is provided as-is for educational and development purposes.

---

## Support

For questions or issues:
- Email: ajsinha@gmail.com
- Check AWS Bedrock documentation
- Review AWS support resources

---

## Version History

- **v1.0** (2025) - Initial release with 13+ models
  - Basic text generation examples
  - Advanced features (streaming, embeddings, image generation)
  - Comprehensive documentation

---

**Copyright 2025-2030 all rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**
