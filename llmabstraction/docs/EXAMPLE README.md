# Claude API Provider Examples


**Copyright © 2025-2030 All rights reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

This repository contains standalone example code for using Claude through different providers.

## 📁 Available Examples

| Provider | File | Description |
|----------|------|-------------|
| **Anthropic Direct API** | `anthropic_example.py` | Direct access through Anthropic's API (Claude) |
| **AWS Bedrock** | `bedrock_example.py` | Claude through Amazon Bedrock |
| **Google Cloud Vertex AI** | `vertex_ai_example.py` | Claude through Google Cloud |
| **OpenAI** | `openai_example.py` | GPT models through OpenAI's API |
| **Together AI** | `together_example.py` | Open-source models (Llama, Mixtral, Qwen, etc.) |

---

## 🚀 Quick Start

### 1. Anthropic Direct API

**Installation:**
```bash
pip install anthropic
```

**Setup:**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Run:**
```bash
python anthropic_example.py
```

**Features:**
- Basic message creation
- Streaming responses
- Multi-turn conversations
- Latest Claude models (Sonnet 4.5, Opus 4.1)

**Get API Key:** https://console.anthropic.com

---

### 2. AWS Bedrock

**Installation:**
```bash
pip install boto3
```

**Setup:**
```bash
# Configure AWS credentials
aws configure

# Or use environment variables
export AWS_ACCESS_KEY_ID='your-access-key'
export AWS_SECRET_ACCESS_KEY='your-secret-key'
export AWS_REGION='us-east-1'
```

**Enable Claude Models:**
1. Go to AWS Bedrock Console
2. Navigate to "Model access"
3. Request access to Claude models
4. Wait for approval (usually instant)

**Run:**
```bash
python bedrock_example.py
```

**Features:**
- Standard invocation
- Streaming responses
- Multi-turn conversations
- AWS credential management

**Available Regions:** us-east-1, us-west-2, ap-southeast-1, ap-northeast-1, eu-central-1

---

### 3. Google Cloud Vertex AI

**Installation:**
```bash
pip install google-cloud-aiplatform anthropic[vertex]
```

**Setup:**
```bash
# Authenticate
gcloud auth application-default login

# Set project and region
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_REGION='us-east5'
```

**Enable Vertex AI:**
1. Create a Google Cloud project
2. Enable Vertex AI API
3. Request access to Claude in Model Garden

**Run:**
```bash
python vertex_ai_example.py
```

**Features:**
- Basic invocation
- Streaming responses
- Multi-turn conversations
- System prompts
- Temperature control

**Available Regions:** us-east5, europe-west1, asia-southeast1

---

### 4. OpenAI

**Installation:**
```bash
pip install openai
```

**Setup:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**Run:**
```bash
python openai_example.py
```

**Features:**
- Chat completions with GPT models
- Streaming responses
- Multi-turn conversations
- System prompts
- Function calling (tool use)
- Vision capabilities (image understanding)
- JSON mode for structured outputs
- Temperature control

**Get API Key:** https://platform.openai.com/api-keys

**Available Models:** gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo

---

### 5. Together AI

**Installation:**
```bash
pip install together
```

**Setup:**
```bash
export TOGETHER_API_KEY='your-api-key-here'
```

**Run:**
```bash
python together_example.py
```

**Features:**
- Access to open-source models (Llama, Mixtral, Qwen)
- Streaming responses
- Multi-turn conversations
- Code generation models
- Image generation
- Function calling
- Model comparison examples

**Get API Key:** https://api.together.xyz/settings/api-keys

**Popular Models:** Llama 3.1 (8B/70B/405B), Mixtral 8x22B, Qwen 2.5, Gemma 2, CodeLlama

---

## 📊 Provider Comparison

| Feature | Anthropic | AWS Bedrock | GCP Vertex | OpenAI | Together AI |
|---------|-----------|-------------|------------|--------|-------------|
| **Models** | Claude 4/3 | Claude 3 | Claude 3 | GPT-4/3.5 | Open-source |
| **Latest Updates** | ✅ Fastest | ⏱️ Delayed | ⏱️ Delayed | ✅ Fast | ✅ Fast |
| **Global Availability** | ✅ Worldwide | 🌍 AWS regions | 🌍 GCP regions | ✅ Worldwide | ✅ Worldwide |
| **Pricing** | Direct | AWS billing | GCP billing | Direct | Direct |
| **Enterprise** | Basic | Advanced | Advanced | Advanced | Basic |
| **Setup** | Easy | Medium | Medium | Easy | Easy |
| **Vision** | ✅ | ✅ | ✅ | ✅ | Limited |
| **Function Calling** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Streaming** | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🔧 Common Parameters

All providers support these common parameters:

```python
{
    "model": "claude-3-5-sonnet...",  # Model identifier
    "max_tokens": 1024,               # Maximum response length
    "temperature": 1.0,               # Randomness (0-1)
    "system": "...",                  # System prompt (optional)
    "messages": [                     # Conversation history
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
}
```

---

## 💡 Best Practices

1. **API Keys**: Always use environment variables, never hardcode keys
2. **Error Handling**: Implement retry logic with exponential backoff
3. **Token Management**: Monitor usage to control costs
4. **Streaming**: Use streaming for better user experience with long responses
5. **Context Management**: Keep conversation history for multi-turn interactions

---

## 📝 Model Names by Provider

### Anthropic Direct API
- `claude-sonnet-4-5-20250929` (Sonnet 4.5 - Latest)
- `claude-opus-4-1-20250514` (Opus 4.1)
- `claude-3-5-sonnet-20241022` (Sonnet 3.5)
- `claude-3-opus-20240229` (Opus 3)

### AWS Bedrock
- `anthropic.claude-3-5-sonnet-20241022-v2:0`
- `anthropic.claude-3-5-sonnet-20240620-v1:0`
- `anthropic.claude-3-opus-20240229-v1:0`
- `anthropic.claude-3-sonnet-20240229-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0`

### Google Vertex AI
- `claude-3-5-sonnet-v2@20241022`
- `claude-3-5-sonnet@20240620`
- `claude-3-opus@20240229`
- `claude-3-sonnet@20240229`
- `claude-3-haiku@20240307`

### OpenAI
- `gpt-4o` (GPT-4 Optimized - Latest)
- `gpt-4o-mini` (Smaller, faster GPT-4)
- `gpt-4-turbo` (GPT-4 Turbo)
- `gpt-4` (GPT-4)
- `gpt-3.5-turbo` (GPT-3.5)

### Together AI
**Chat Models:**
- `meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo`
- `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo`
- `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`
- `mistralai/Mixtral-8x22B-Instruct-v0.1`
- `Qwen/Qwen2.5-72B-Instruct-Turbo`
- `google/gemma-2-27b-it`

**Code Models:**
- `Qwen/Qwen2.5-Coder-32B-Instruct`
- `codellama/CodeLlama-70b-Instruct-hf`

---

## 🔗 Additional Resources

- **Anthropic Documentation**: https://docs.anthropic.com
- **AWS Bedrock Docs**: https://docs.aws.amazon.com/bedrock
- **Google Vertex AI Docs**: https://cloud.google.com/vertex-ai/docs
- **OpenAI Documentation**: https://platform.openai.com/docs
- **Together AI Documentation**: https://docs.together.ai
- **Claude API Reference**: https://docs.anthropic.com/en/api
- **OpenAI API Reference**: https://platform.openai.com/docs/api-reference

---

## ⚠️ Troubleshooting

### Anthropic Direct API
```
Error: Authentication error
→ Check your ANTHROPIC_API_KEY is set correctly
```

### AWS Bedrock
```
Error: AccessDeniedException
→ Request model access in AWS Bedrock console
→ Check IAM permissions for bedrock:InvokeModel
```

### Google Vertex AI
```
Error: PermissionDenied
→ Enable Vertex AI API in GCP console
→ Authenticate with: gcloud auth application-default login
```

### OpenAI
```
Error: AuthenticationError
→ Check your OPENAI_API_KEY is set correctly
→ Verify API key is active at https://platform.openai.com/api-keys
→ Ensure you have credits in your account
```

### Together AI
```
Error: Authentication failed
→ Check your TOGETHER_API_KEY is set correctly
→ Get API key from: https://api.together.xyz/settings/api-keys
→ Verify you have credits in your account
```

---

## 📄 License

These examples are provided as-is for educational purposes.

## 🤝 Contributing

Feel free to submit issues or pull requests for improvements!
