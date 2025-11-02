# Comprehensive Hugging Face Models Guide

```
================================================================================
Copyright 2025-2030 All Rights Reserved
Author: Ashutosh Sinha
Email: ajsinha@gmail.com
================================================================================
```

## Overview

This comprehensive guide provides working examples of **13+ different Hugging Face models** including:
- **Free models**: GPT-2, BERT, T5, DistilBERT, RoBERTa, BART, Falcon, Mistral, BLOOMZ
- **Gated models**: Llama 2, Llama 3, CodeLlama (require license acceptance)

## Files Included

1. **huggingface_models_guide.py** - Basic examples with 13 different models
2. **huggingface_advanced_guide.py** - Advanced techniques and specialized use cases
3. **README.md** - This file with instructions and documentation

---

## Installation

### Prerequisites
```bash
# Python 3.8 or higher required
python --version
```

### Install Required Packages
```bash
# Core packages
pip install transformers torch accelerate

# For quantization (reduces memory usage)
pip install bitsandbytes

# For Llama models
pip install sentencepiece protobuf

# For semantic search examples
pip install sentence-transformers

# Hugging Face Hub
pip install huggingface_hub
```

### GPU Support (Recommended)
```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

## Authentication for Gated Models

Llama models require authentication and license acceptance:

### Step 1: Create Hugging Face Account
Visit: https://huggingface.co/join

### Step 2: Accept Model Licenses
- Llama 2: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
- Llama 3: https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
- CodeLlama: https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf

### Step 3: Create Access Token
1. Go to: https://huggingface.co/settings/tokens
2. Create new token (Read access is sufficient)
3. Copy the token

### Step 4: Login
```bash
# Method 1: Using CLI
huggingface-cli login

# Method 2: Using environment variable
export HUGGINGFACE_TOKEN="your_token_here"

# Method 3: In Python code
from huggingface_hub import login
login(token="your_token_here")
```

---

## Quick Start

### Run All Examples
```bash
# Basic examples (13 models)
python huggingface_models_guide.py

# Advanced examples
python huggingface_advanced_guide.py
```

### Run Individual Examples
```python
from huggingface_models_guide import *

# Run specific model examples
example_llama2()
example_gpt2()
example_bert()
example_t5()
```

---

## Models Covered

### 1. **Llama 2** (GATED)
- **Model**: meta-llama/Llama-2-7b-chat-hf
- **Use Case**: Advanced text generation, chat
- **Memory**: ~14GB (fp16), ~7GB (8-bit)
- **License**: Meta AI License (requires acceptance)

### 2. **Llama 3** (GATED)
- **Model**: meta-llama/Meta-Llama-3-8B-Instruct
- **Use Case**: Latest generation chat model
- **Memory**: ~16GB (fp16)
- **License**: Meta AI License (requires acceptance)

### 3. **GPT-2** (FREE)
- **Model**: gpt2
- **Use Case**: Text generation, completion
- **Memory**: ~500MB
- **License**: MIT

### 4. **BERT** (FREE)
- **Model**: bert-base-uncased
- **Use Case**: Fill-mask, embeddings, classification
- **Memory**: ~440MB
- **License**: Apache 2.0

### 5. **T5** (FREE)
- **Model**: t5-small, t5-base, t5-large
- **Use Case**: Translation, summarization, Q&A
- **Memory**: 242MB (small), 892MB (base)
- **License**: Apache 2.0

### 6. **DistilBERT** (FREE)
- **Model**: distilbert-base-uncased
- **Use Case**: Sentiment analysis, classification
- **Memory**: ~260MB (40% smaller than BERT)
- **License**: Apache 2.0

### 7. **RoBERTa** (FREE)
- **Model**: roberta-base
- **Use Case**: Question answering, NER
- **Memory**: ~500MB
- **License**: MIT

### 8. **BART** (FREE)
- **Model**: facebook/bart-large-cnn
- **Use Case**: Summarization, text generation
- **Memory**: ~1.6GB
- **License**: Apache 2.0

### 9. **Falcon** (FREE)
- **Model**: tiiuae/falcon-7b-instruct
- **Use Case**: Text generation, chat
- **Memory**: ~14GB
- **License**: Apache 2.0

### 10. **Mistral** (FREE)
- **Model**: mistralai/Mistral-7B-Instruct-v0.2
- **Use Case**: High-performance text generation
- **Memory**: ~14GB
- **License**: Apache 2.0

### 11. **Mixtral** (FREE)
- **Model**: mistralai/Mixtral-8x7B-Instruct-v0.1
- **Use Case**: Mixture of Experts model
- **Memory**: ~45GB (requires substantial resources)
- **License**: Apache 2.0

### 12. **BLOOMZ** (FREE)
- **Model**: bigscience/bloomz-560m
- **Use Case**: Multilingual (46+ languages)
- **Memory**: ~1.1GB
- **License**: BigScience RAIL License

### 13. **CodeLlama** (GATED)
- **Model**: codellama/CodeLlama-7b-Instruct-hf
- **Use Case**: Code generation, completion
- **Memory**: ~14GB
- **License**: Meta AI License (requires acceptance)

---

## Advanced Features Covered

### 1. **Custom System Prompts**
```python
# Llama 2 with custom instructions
system_prompt = "You are a Python expert"
prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{user_message} [/INST]"
```

### 2. **Multi-turn Conversations**
```python
conversation = [
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "How are you?"}
]
```

### 3. **Streaming Generation**
```python
from transformers import TextIteratorStreamer
streamer = TextIteratorStreamer(tokenizer)
# Real-time token-by-token output
```

### 4. **Semantic Search**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(documents)
# Find similar documents using cosine similarity
```

### 5. **Zero-Shot Classification**
```python
# Classify without training data
classifier = pipeline("zero-shot-classification")
result = classifier(text, candidate_labels=["tech", "sports", "politics"])
```

### 6. **Named Entity Recognition**
```python
ner = pipeline("ner", model="dslim/bert-base-NER")
entities = ner("Apple Inc. was founded by Steve Jobs")
```

### 7. **Quantization (8-bit)**
```python
from transformers import BitsAndBytesConfig
config = BitsAndBytesConfig(load_in_8bit=True)
# Reduces memory by ~75%
```

### 8. **Batch Processing**
```python
# Process multiple inputs efficiently
results = classifier(texts, batch_size=8)
```

---

## System Requirements

### Minimum (CPU Only)
- **RAM**: 16GB
- **Storage**: 50GB
- **Models**: GPT-2, BERT, DistilBERT, T5-small

### Recommended (GPU)
- **RAM**: 32GB
- **GPU VRAM**: 16GB (RTX 4080, A4000)
- **Storage**: 100GB
- **Models**: All models including Llama 7B (with quantization)

### High-End (Multiple GPUs)
- **RAM**: 64GB+
- **GPU VRAM**: 24GB+ per GPU (RTX 4090, A5000, A6000)
- **Storage**: 200GB+
- **Models**: All models including 70B variants

---

## Usage Examples

### Example 1: Text Generation with Llama 2
```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name, token=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype=torch.float16,
    token=True
)

prompt = "[INST] Explain quantum computing [/INST]"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

### Example 2: Sentiment Analysis with BERT
```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis")
result = classifier("I love this product!")
print(result)
# Output: [{'label': 'POSITIVE', 'score': 0.9998}]
```

### Example 3: Summarization with BART
```python
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
article = "Long article text here..."
summary = summarizer(article, max_length=130, min_length=30)
print(summary[0]['summary_text'])
```

### Example 4: Question Answering with RoBERTa
```python
from transformers import pipeline

qa = pipeline("question-answering", model="deepset/roberta-base-squad2")
context = "Python was created by Guido van Rossum in 1991."
question = "Who created Python?"
result = qa(question=question, context=context)
print(result['answer'])  # Output: Guido van Rossum
```

---

## Performance Tips

### 1. Use Quantization
```python
# Reduces memory by 75%
from transformers import BitsAndBytesConfig
config = BitsAndBytesConfig(load_in_8bit=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=config
)
```

### 2. Batch Processing
```python
# Process multiple inputs at once
results = model(texts, batch_size=16)
```

### 3. Use Smaller Models
- Use `distilbert` instead of `bert` (40% faster)
- Use `gpt2` instead of larger models for prototyping
- Use `t5-small` instead of `t5-base` for limited resources

### 4. Cache Results
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_inference(text):
    return model(text)
```

---

## Common Issues and Solutions

### Issue 1: Out of Memory
**Solution**: Use quantization or smaller batch sizes
```python
config = BitsAndBytesConfig(load_in_8bit=True)
```

### Issue 2: Slow Inference
**Solution**: Use GPU, batch processing, or smaller models
```python
device = 0 if torch.cuda.is_available() else -1
pipeline("sentiment-analysis", device=device)
```

### Issue 3: Gated Model Access Denied
**Solution**: Accept license and authenticate
```bash
huggingface-cli login
# Then accept license at model page
```

### Issue 4: Import Errors
**Solution**: Install missing dependencies
```bash
pip install transformers torch accelerate bitsandbytes
```

---

## Model Comparison Table

| Model | Size | Memory | Speed | License | Best For |
|-------|------|--------|-------|---------|----------|
| GPT-2 | 124M | 500MB | Fast | MIT | Quick prototyping |
| BERT | 110M | 440MB | Fast | Apache 2.0 | Classification |
| DistilBERT | 66M | 260MB | Fastest | Apache 2.0 | Fast inference |
| T5 | 60M-11B | 242MB-42GB | Medium | Apache 2.0 | Versatile tasks |
| RoBERTa | 125M | 500MB | Fast | MIT | Q&A, NER |
| BART | 406M | 1.6GB | Medium | Apache 2.0 | Summarization |
| Llama 2 | 7B | 14GB | Slow | Meta | Advanced chat |
| Llama 3 | 8B | 16GB | Slow | Meta | Latest gen chat |
| Mistral | 7B | 14GB | Medium | Apache 2.0 | High performance |
| CodeLlama | 7B | 14GB | Slow | Meta | Code generation |

---

## Cost Analysis

### Running Locally (Free)
- **One-time cost**: GPU hardware ($500-$5000)
- **Ongoing cost**: Electricity (~$0.10-0.50 per hour)
- **Total**: Free after hardware purchase

### Hugging Face Inference API
- **Free tier**: Limited requests/month
- **PRO**: $9/month
- **Enterprise**: Custom pricing

### Cloud GPU (AWS, GCP, Azure)
- **Small GPU (T4)**: $0.50-1.00/hour
- **Large GPU (A100)**: $3.00-5.00/hour
- **TPU**: $4.50/hour

---

## Resources

### Official Documentation
- Hugging Face: https://huggingface.co/docs
- Transformers: https://huggingface.co/docs/transformers
- PEFT: https://huggingface.co/docs/peft

### Tutorials
- Hugging Face Course: https://huggingface.co/learn
- Model Hub: https://huggingface.co/models
- Datasets: https://huggingface.co/datasets

### Community
- Forum: https://discuss.huggingface.co
- Discord: https://discord.com/invite/hugging-face
- GitHub: https://github.com/huggingface

---

## License

```
Copyright 2025-2030 All Rights Reserved
Author: Ashutosh Sinha
Email: ajsinha@gmail.com
```

This code is provided for educational purposes. Individual model licenses apply:
- Meta models (Llama, CodeLlama): Meta AI License
- OpenAI models (GPT-2): MIT License  
- Google models (BERT, T5): Apache 2.0
- Facebook models (BART): Apache 2.0
- Mistral models: Apache 2.0

---

## Support

For questions or issues:
- Email: ajsinha@gmail.com
- Check model documentation on Hugging Face Hub
- Review error messages carefully - they usually indicate missing dependencies or authentication issues

---

## Changelog

### Version 1.0 (2025)
- Initial release with 13+ model examples
- Basic and advanced usage patterns
- Optimization techniques
- Comprehensive documentation

---

**Happy Coding! 🚀**

*Remember to always check model licenses and terms of use before deploying in production.*
