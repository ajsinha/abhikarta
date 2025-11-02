"""
================================================================================
Comprehensive Hugging Face Models Guide
================================================================================

Copyright 2025-2030 All Rights Reserved
Author: Ashutosh Sinha
Email: ajsinha@gmail.com

================================================================================

Examples of 12+ different models (free and gated) using Python
Includes Llama models as requested

Requirements:
pip install transformers torch accelerate bitsandbytes sentencepiece protobuf
pip install huggingface_hub

For gated models (like Llama), you'll need:
1. Create a Hugging Face account
2. Accept model license agreements
3. Create an access token (Settings > Access Tokens)
4. Login: huggingface-cli login
"""

import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM,
    AutoModelForSequenceClassification, AutoModelForQuestionAnswering,
    pipeline, BitsAndBytesConfig
)
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. LLAMA 2 - Meta's Large Language Model (GATED - Requires License)
# ============================================================================
def example_llama2():
    """
    Llama 2 7B - Text Generation
    License: Requires acceptance at https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
    """
    print("\n" + "="*80)
    print("1. LLAMA 2 - 7B Chat Model")
    print("="*80)
    
    model_name = "meta-llama/Llama-2-7b-chat-hf"
    
    # Use 8-bit quantization to reduce memory
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0
    )
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto",
            token=True
        )
        
        prompt = "What are the three laws of robotics?"
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            top_p=0.9
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Llama requires accepting license and authentication token")


# ============================================================================
# 2. LLAMA 3 - Meta's Latest Model (GATED)
# ============================================================================
def example_llama3():
    """
    Llama 3 8B Instruct - Advanced Text Generation
    License: Requires acceptance at https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
    """
    print("\n" + "="*80)
    print("2. LLAMA 3 - 8B Instruct Model")
    print("="*80)
    
    model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
    
    try:
        # Using pipeline for easier inference
        generator = pipeline(
            "text-generation",
            model=model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            token=True
        )
        
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ]
        
        outputs = generator(
            messages,
            max_new_tokens=150,
            temperature=0.7
        )
        
        print(f"Response: {outputs[0]['generated_text'][-1]['content']}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Llama 3 requires accepting license and authentication token")


# ============================================================================
# 3. GPT-2 - OpenAI's Text Generation Model (FREE)
# ============================================================================
def example_gpt2():
    """
    GPT-2 - Classic text generation model by OpenAI
    Free to use, no authentication required
    """
    print("\n" + "="*80)
    print("3. GPT-2 - Text Generation")
    print("="*80)
    
    model_name = "gpt2"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    prompt = "The future of artificial intelligence is"
    inputs = tokenizer(prompt, return_tensors="pt")
    
    outputs = model.generate(
        **inputs,
        max_length=100,
        num_return_sequences=1,
        temperature=0.8,
        do_sample=True
    )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Generated: {generated_text}")


# ============================================================================
# 4. BERT - Bidirectional Encoder (FREE)
# ============================================================================
def example_bert():
    """
    BERT - Text Classification and Embeddings
    Free to use, great for understanding tasks
    """
    print("\n" + "="*80)
    print("4. BERT - Fill Mask & Classification")
    print("="*80)
    
    # Fill-mask task
    fill_mask = pipeline("fill-mask", model="bert-base-uncased")
    
    text = "The capital of France is [MASK]."
    results = fill_mask(text)
    
    print(f"Text: {text}")
    print("Predictions:")
    for result in results[:3]:
        print(f"  - {result['token_str']}: {result['score']:.4f}")


# ============================================================================
# 5. T5 - Text-to-Text Transfer Transformer (FREE)
# ============================================================================
def example_t5():
    """
    T5 - Versatile text-to-text model for multiple tasks
    Free to use, excellent for summarization, translation, QA
    """
    print("\n" + "="*80)
    print("5. T5 - Text-to-Text (Translation & Summarization)")
    print("="*80)
    
    model_name = "t5-small"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    # Translation
    input_text = "translate English to German: How are you doing today?"
    inputs = tokenizer(input_text, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=50)
    translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    print(f"Translation: {translation}")
    
    # Summarization
    article = """
    Artificial intelligence is transforming industries worldwide. From healthcare 
    to finance, AI systems are helping humans make better decisions. Machine learning 
    algorithms can process vast amounts of data quickly and identify patterns that 
    humans might miss.
    """
    
    input_text = f"summarize: {article}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=50)
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    print(f"\nSummary: {summary}")


# ============================================================================
# 6. DistilBERT - Lightweight BERT (FREE)
# ============================================================================
def example_distilbert():
    """
    DistilBERT - Faster, lighter version of BERT
    Free to use, 40% smaller, 60% faster
    """
    print("\n" + "="*80)
    print("6. DistilBERT - Sentiment Analysis")
    print("="*80)
    
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    
    texts = [
        "I love this product! It's amazing!",
        "This is the worst experience ever.",
        "It's okay, nothing special."
    ]
    
    results = classifier(texts)
    
    for text, result in zip(texts, results):
        print(f"Text: {text}")
        print(f"Sentiment: {result['label']} (confidence: {result['score']:.4f})\n")


# ============================================================================
# 7. RoBERTa - Robustly Optimized BERT (FREE)
# ============================================================================
def example_roberta():
    """
    RoBERTa - Improved version of BERT
    Free to use, better performance on many tasks
    """
    print("\n" + "="*80)
    print("7. RoBERTa - Question Answering")
    print("="*80)
    
    qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")
    
    context = """
    Python is a high-level programming language. It was created by Guido van Rossum 
    and first released in 1991. Python emphasizes code readability and simplicity.
    """
    
    questions = [
        "Who created Python?",
        "When was Python first released?",
        "What does Python emphasize?"
    ]
    
    for question in questions:
        result = qa_pipeline(question=question, context=context)
        print(f"Q: {question}")
        print(f"A: {result['answer']} (score: {result['score']:.4f})\n")


# ============================================================================
# 8. BART - Bidirectional and Auto-Regressive Transformer (FREE)
# ============================================================================
def example_bart():
    """
    BART - Excellent for summarization and text generation
    Free to use
    """
    print("\n" + "="*80)
    print("8. BART - Text Summarization")
    print("="*80)
    
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    article = """
    Climate change is one of the most pressing issues of our time. Rising temperatures 
    are causing ice caps to melt, sea levels to rise, and weather patterns to become 
    more extreme. Scientists around the world are working on solutions to reduce carbon 
    emissions and develop renewable energy sources. Governments are implementing policies 
    to encourage sustainable practices and reduce the impact of human activities on the 
    environment. However, more action is needed to prevent catastrophic consequences.
    """
    
    summary = summarizer(article, max_length=60, min_length=30, do_sample=False)
    print(f"Original length: {len(article.split())} words")
    print(f"Summary: {summary[0]['summary_text']}")
    print(f"Summary length: {len(summary[0]['summary_text'].split())} words")


# ============================================================================
# 9. FALCON - Large Language Model (FREE)
# ============================================================================
def example_falcon():
    """
    Falcon 7B - Open-source LLM
    Free to use, competitive performance
    """
    print("\n" + "="*80)
    print("9. FALCON - 7B Instruct Model")
    print("="*80)
    
    model_name = "tiiuae/falcon-7b-instruct"
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        prompt = "Write a haiku about programming:"
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            do_sample=True
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Response:\n{response}")
        
    except Exception as e:
        print(f"Error: {e}")


# ============================================================================
# 10. MISTRAL - 7B Model (FREE)
# ============================================================================
def example_mistral():
    """
    Mistral 7B - High-performance open-source model
    Free to use, Apache 2.0 license
    """
    print("\n" + "="*80)
    print("10. MISTRAL - 7B Instruct Model")
    print("="*80)
    
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    
    try:
        generator = pipeline(
            "text-generation",
            model=model_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        
        prompt = "Explain the concept of recursion in programming with an example."
        
        outputs = generator(
            prompt,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True
        )
        
        print(f"Response:\n{outputs[0]['generated_text']}")
        
    except Exception as e:
        print(f"Error: {e}")


# ============================================================================
# 11. MIXTRAL - Mixture of Experts (FREE but requires more resources)
# ============================================================================
def example_mixtral():
    """
    Mixtral 8x7B - Mixture of Experts model
    Free to use, requires more VRAM
    """
    print("\n" + "="*80)
    print("11. MIXTRAL - 8x7B Instruct Model")
    print("="*80)
    
    model_name = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    
    try:
        # This model is large and requires significant resources
        generator = pipeline(
            "text-generation",
            model=model_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        
        prompt = "What are the key differences between Python and JavaScript?"
        
        outputs = generator(
            prompt,
            max_new_tokens=150,
            temperature=0.7
        )
        
        print(f"Response:\n{outputs[0]['generated_text']}")
        
    except Exception as e:
        print(f"Error (expected for resource-constrained systems): {e}")


# ============================================================================
# 12. BLOOMZ - Multilingual LLM (FREE)
# ============================================================================
def example_bloomz():
    """
    BLOOMZ - Multilingual language model
    Free to use, supports 46+ languages
    """
    print("\n" + "="*80)
    print("12. BLOOMZ - Multilingual Model")
    print("="*80)
    
    model_name = "bigscience/bloomz-560m"
    
    try:
        generator = pipeline("text-generation", model=model_name)
        
        prompts = [
            "Translate to French: Hello, how are you?",
            "Translate to Spanish: Good morning!",
        ]
        
        for prompt in prompts:
            outputs = generator(prompt, max_length=50)
            print(f"Prompt: {prompt}")
            print(f"Response: {outputs[0]['generated_text']}\n")
            
    except Exception as e:
        print(f"Error: {e}")


# ============================================================================
# 13. CodeLlama - Llama fine-tuned for coding (GATED)
# ============================================================================
def example_code_llama():
    """
    CodeLlama - Specialized for code generation
    Requires license acceptance like Llama 2
    """
    print("\n" + "="*80)
    print("13. CODE LLAMA - Code Generation")
    print("="*80)
    
    model_name = "codellama/CodeLlama-7b-Instruct-hf"
    
    try:
        generator = pipeline(
            "text-generation",
            model=model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            token=True
        )
        
        prompt = "Write a Python function to calculate fibonacci numbers recursively:"
        
        outputs = generator(
            prompt,
            max_new_tokens=200,
            temperature=0.2
        )
        
        print(f"Prompt: {prompt}")
        print(f"Generated Code:\n{outputs[0]['generated_text']}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: CodeLlama requires accepting license and authentication token")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_gpu_availability():
    """Check if GPU is available"""
    if torch.cuda.is_available():
        print(f"✓ GPU Available: {torch.cuda.get_device_name(0)}")
        print(f"  CUDA Version: {torch.version.cuda}")
        print(f"  Available Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        print("✗ No GPU available - using CPU (models will be slower)")


def setup_huggingface_token():
    """
    Guide for setting up Hugging Face token
    """
    print("\n" + "="*80)
    print("SETUP: Hugging Face Authentication")
    print("="*80)
    print("""
For gated models (Llama, CodeLlama, etc.), you need to:

1. Create account at https://huggingface.co/
2. Go to Settings → Access Tokens
3. Create a new token (Read access is sufficient)
4. Run in terminal:
   
   huggingface-cli login
   
   Or set environment variable:
   
   export HUGGINGFACE_TOKEN="your_token_here"
   
5. Accept license agreements for specific models:
   - Llama 2: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
   - Llama 3: https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
   - CodeLlama: https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Run all examples
    """
    print("\n" + "="*80)
    print("HUGGING FACE MODELS - COMPREHENSIVE EXAMPLES")
    print("="*80)
    
    check_gpu_availability()
    setup_huggingface_token()
    
    # Free models (no authentication required)
    print("\n\n" + "="*80)
    print("FREE MODELS (No Authentication Required)")
    print("="*80)
    
    example_gpt2()
    example_bert()
    example_t5()
    example_distilbert()
    example_roberta()
    example_bart()
    example_falcon()
    example_mistral()
    example_bloomz()
    
    # Note about resource-intensive model
    print("\n⚠️  Skipping Mixtral (requires significant GPU memory)")
    
    # Gated models (require authentication)
    print("\n\n" + "="*80)
    print("GATED MODELS (Require Authentication & License Acceptance)")
    print("="*80)
    
    example_llama2()
    example_llama3()
    example_code_llama()
    
    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80)


if __name__ == "__main__":
    # You can run all examples or individual ones
    main()
    
    # Or run specific examples:
    # example_llama2()
    # example_gpt2()
    # example_bert()
