"""
================================================================================
Hugging Face Models - Quick Start Script
================================================================================

Copyright 2025-2030 All Rights Reserved
Author: Ashutosh Sinha
Email: ajsinha@gmail.com

================================================================================

This script provides a simple menu-driven interface to test different models.
Perfect for beginners and quick testing!

Usage:
    python quickstart.py
"""

import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import warnings
warnings.filterwarnings('ignore')


def check_system():
    """Check system capabilities"""
    print("\n" + "="*80)
    print("SYSTEM CHECK")
    print("="*80)
    
    # Check Python version
    import sys
    print(f"✓ Python version: {sys.version.split()[0]}")
    
    # Check PyTorch
    print(f"✓ PyTorch version: {torch.__version__}")
    
    # Check GPU
    if torch.cuda.is_available():
        print(f"✓ GPU Available: {torch.cuda.get_device_name(0)}")
        print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        print("⚠ No GPU detected - using CPU (slower)")
    
    # Check authentication
    try:
        from huggingface_hub import HfFolder
        token = HfFolder.get_token()
        if token:
            print("✓ Hugging Face authenticated")
        else:
            print("⚠ Not authenticated - gated models won't work")
    except:
        print("⚠ Not authenticated - gated models won't work")
    
    print("="*80)


def test_gpt2():
    """Test GPT-2 (Free, no auth needed)"""
    print("\n" + "="*80)
    print("Testing GPT-2 - Text Generation")
    print("="*80)
    
    try:
        generator = pipeline("text-generation", model="gpt2")
        
        prompt = "The future of artificial intelligence is"
        print(f"\nPrompt: {prompt}")
        print("Generating...\n")
        
        output = generator(
            prompt,
            max_length=80,
            num_return_sequences=1,
            temperature=0.7
        )
        
        print(f"Generated text:\n{output[0]['generated_text']}")
        print("\n✓ GPT-2 working correctly!")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def test_sentiment():
    """Test Sentiment Analysis with DistilBERT"""
    print("\n" + "="*80)
    print("Testing DistilBERT - Sentiment Analysis")
    print("="*80)
    
    try:
        classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        
        texts = [
            "I absolutely love this! It's amazing!",
            "This is terrible and disappointing.",
            "It's okay, nothing special."
        ]
        
        print("\nAnalyzing sentiments...\n")
        results = classifier(texts)
        
        for text, result in zip(texts, results):
            emoji = "😊" if result['label'] == 'POSITIVE' else "😞"
            print(f"{emoji} '{text}'")
            print(f"   → {result['label']} (confidence: {result['score']:.2%})\n")
        
        print("✓ Sentiment analysis working correctly!")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def test_summarization():
    """Test Summarization with BART"""
    print("\n" + "="*80)
    print("Testing BART - Text Summarization")
    print("="*80)
    
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        article = """
        Artificial intelligence has made significant advances in recent years. 
        Machine learning algorithms can now perform tasks that were once thought 
        to require human intelligence. Deep learning, a subset of machine learning, 
        uses neural networks with multiple layers to process data. These technologies 
        are being applied in various fields including healthcare, finance, and 
        transportation. Self-driving cars use AI to navigate roads safely. Medical 
        diagnostic systems can detect diseases from medical images. AI assistants 
        help us with daily tasks. However, there are also concerns about privacy, 
        job displacement, and the ethical implications of AI systems.
        """
        
        print("\nOriginal article length:", len(article.split()), "words")
        print("Summarizing...\n")
        
        summary = summarizer(article, max_length=60, min_length=30, do_sample=False)
        
        print(f"Summary ({len(summary[0]['summary_text'].split())} words):")
        print(summary[0]['summary_text'])
        
        print("\n✓ Summarization working correctly!")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def test_question_answering():
    """Test Question Answering with RoBERTa"""
    print("\n" + "="*80)
    print("Testing RoBERTa - Question Answering")
    print("="*80)
    
    try:
        qa = pipeline("question-answering", model="deepset/roberta-base-squad2")
        
        context = """
        Python is a high-level, interpreted programming language created by 
        Guido van Rossum. It was first released in 1991. Python's design philosophy 
        emphasizes code readability with its use of significant indentation. 
        Python is dynamically typed and supports multiple programming paradigms 
        including object-oriented, functional, and procedural programming.
        """
        
        questions = [
            "Who created Python?",
            "When was Python released?",
            "What does Python emphasize?"
        ]
        
        print("\nContext:", context[:100] + "...\n")
        
        for question in questions:
            result = qa(question=question, context=context)
            print(f"Q: {question}")
            print(f"A: {result['answer']} (confidence: {result['score']:.2%})\n")
        
        print("✓ Question answering working correctly!")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def test_translation():
    """Test Translation with T5"""
    print("\n" + "="*80)
    print("Testing T5 - Translation")
    print("="*80)
    
    try:
        translator = pipeline("translation_en_to_de", model="t5-small")
        
        texts = [
            "Hello, how are you?",
            "I love programming in Python.",
            "Machine learning is fascinating."
        ]
        
        print("\nTranslating English to German...\n")
        
        for text in texts:
            # T5 expects "translate English to German: " prefix
            result = translator(f"translate English to German: {text}", max_length=100)
            print(f"EN: {text}")
            print(f"DE: {result[0]['translation_text']}\n")
        
        print("✓ Translation working correctly!")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def test_llama2():
    """Test Llama 2 (Gated - requires authentication)"""
    print("\n" + "="*80)
    print("Testing Llama 2 - Advanced Text Generation")
    print("="*80)
    
    model_name = "meta-llama/Llama-2-7b-chat-hf"
    
    try:
        print("\n⚠ Note: Llama 2 requires:")
        print("  1. Hugging Face authentication (huggingface-cli login)")
        print("  2. License acceptance at: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf")
        print("  3. Significant GPU memory (~7GB with 8-bit quantization)")
        
        response = input("\nHave you completed these steps? (y/n): ")
        
        if response.lower() != 'y':
            print("\nSkipping Llama 2 test. Complete the steps above and try again.")
            return
        
        from transformers import BitsAndBytesConfig
        
        print("\nLoading Llama 2 (this may take a minute)...")
        
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto",
            token=True
        )
        
        prompt = "[INST] What are the three laws of robotics? [/INST]"
        print(f"\nPrompt: {prompt}")
        print("Generating response...\n")
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Response:\n{response}")
        
        print("\n✓ Llama 2 working correctly!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nCommon issues:")
        print("  - Not authenticated: Run 'huggingface-cli login'")
        print("  - License not accepted: Visit the model page and accept")
        print("  - Insufficient GPU memory: Try a machine with more VRAM")


def run_interactive_mode():
    """Interactive mode - ask user what to test"""
    print("\n" + "="*80)
    print("HUGGING FACE QUICK START - INTERACTIVE MODE")
    print("Copyright 2025-2030 - Ashutosh Sinha (ajsinha@gmail.com)")
    print("="*80)
    
    while True:
        print("\n" + "="*80)
        print("SELECT A TEST:")
        print("="*80)
        print("1. System Check")
        print("2. GPT-2 (Text Generation) - FREE")
        print("3. DistilBERT (Sentiment Analysis) - FREE")
        print("4. BART (Summarization) - FREE")
        print("5. RoBERTa (Question Answering) - FREE")
        print("6. T5 (Translation) - FREE")
        print("7. Llama 2 (Advanced Chat) - GATED")
        print("8. Run All Free Tests")
        print("0. Exit")
        print("="*80)
        
        choice = input("\nEnter your choice (0-8): ").strip()
        
        if choice == '0':
            print("\nThank you for using Hugging Face Quick Start!")
            break
        elif choice == '1':
            check_system()
        elif choice == '2':
            test_gpt2()
        elif choice == '3':
            test_sentiment()
        elif choice == '4':
            test_summarization()
        elif choice == '5':
            test_question_answering()
        elif choice == '6':
            test_translation()
        elif choice == '7':
            test_llama2()
        elif choice == '8':
            check_system()
            test_gpt2()
            test_sentiment()
            test_summarization()
            test_question_answering()
            test_translation()
            print("\n" + "="*80)
            print("ALL FREE TESTS COMPLETED!")
            print("="*80)
        else:
            print("\n✗ Invalid choice. Please enter a number between 0 and 8.")
        
        input("\nPress Enter to continue...")


def run_automated_tests():
    """Run all tests automatically"""
    print("\n" + "="*80)
    print("RUNNING AUTOMATED TESTS")
    print("Copyright 2025-2030 - Ashutosh Sinha (ajsinha@gmail.com)")
    print("="*80)
    
    check_system()
    
    print("\n\nRunning free model tests (this will take a few minutes)...\n")
    
    test_gpt2()
    test_sentiment()
    test_summarization()
    test_question_answering()
    test_translation()
    
    print("\n" + "="*80)
    print("AUTOMATED TESTS COMPLETED!")
    print("="*80)
    print("\nNote: Llama 2 test skipped (requires authentication)")
    print("To test Llama 2, run in interactive mode and select option 7")


def main():
    """Main entry point"""
    import sys
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║           HUGGING FACE MODELS - QUICK START SCRIPT                  ║
    ║                                                                      ║
    ║  Copyright 2025-2030 All Rights Reserved                            ║
    ║  Author: Ashutosh Sinha                                             ║
    ║  Email: ajsinha@gmail.com                                           ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        run_automated_tests()
    else:
        run_interactive_mode()


if __name__ == "__main__":
    main()
