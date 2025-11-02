"""
================================================================================
Advanced Hugging Face Models Guide
================================================================================

Copyright 2025-2030 All Rights Reserved
Author: Ashutosh Sinha
Email: ajsinha@gmail.com

================================================================================

Detailed information about costs, limitations, and advanced usage

MODEL CATEGORIES & COSTS
========================

FREE MODELS (No restrictions):
- GPT-2
- BERT, DistilBERT, RoBERTa
- T5 (all sizes)
- BART
- BLOOMZ
- Falcon (7B and larger)
- Mistral 7B

GATED MODELS (Free but require license acceptance):
- Llama 2 (7B, 13B, 70B)
- Llama 3 (8B, 70B)
- CodeLlama (7B, 13B, 34B)

INFERENCE API COSTS (Using Hugging Face's hosted API):
- Free tier: Limited requests per month
- PRO ($9/month): More requests, faster inference
- Enterprise: Custom pricing

Note: Running models locally is free but requires computational resources (GPU recommended)
"""

import torch
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForCausalLM,
    pipeline, StoppingCriteria, StoppingCriteriaList
)
from huggingface_hub import InferenceClient
import json


# ============================================================================
# ADVANCED LLAMA EXAMPLES
# ============================================================================

class LlamaAdvancedExamples:
    """Advanced usage patterns for Llama models"""
    
    @staticmethod
    def llama2_with_custom_system_prompt():
        """
        Using Llama 2 with custom system prompts for specialized tasks
        """
        print("\n" + "="*80)
        print("LLAMA 2 - Custom System Prompt")
        print("="*80)
        
        model_name = "meta-llama/Llama-2-7b-chat-hf"
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, token=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                token=True,
                load_in_8bit=True  # Reduces memory usage
            )
            
            # Llama 2 chat format with custom system prompt
            system_prompt = "You are a helpful coding assistant specialized in Python and data science."
            user_message = "How do I read a CSV file and calculate the mean of a column?"
            
            prompt = f"""<s>[INST] <<SYS>>
{system_prompt}
<</SYS>>

{user_message} [/INST]"""
            
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            
            outputs = model.generate(
                **inputs,
                max_new_tokens=300,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.15,
                do_sample=True
            )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"System Prompt: {system_prompt}")
            print(f"User Query: {user_message}")
            print(f"Response:\n{response}")
            
        except Exception as e:
            print(f"Error: {e}")
            print("Note: Requires Hugging Face authentication and license acceptance")
    
    @staticmethod
    def llama3_multi_turn_conversation():
        """
        Multi-turn conversation with Llama 3 using chat template
        """
        print("\n" + "="*80)
        print("LLAMA 3 - Multi-turn Conversation")
        print("="*80)
        
        model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, token=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                token=True
            )
            
            # Initialize conversation history
            conversation = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": "What is the difference between a list and a tuple in Python?"},
            ]
            
            # First turn
            inputs = tokenizer.apply_chat_template(
                conversation,
                return_tensors="pt",
                add_generation_prompt=True
            ).to(model.device)
            
            outputs = model.generate(
                inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True
            )
            
            response1 = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            print(f"User: {conversation[-1]['content']}")
            print(f"Assistant: {response1}\n")
            
            # Add assistant response and continue conversation
            conversation.append({"role": "assistant", "content": response1})
            conversation.append({"role": "user", "content": "Can you show me a practical example?"})
            
            inputs = tokenizer.apply_chat_template(
                conversation,
                return_tensors="pt",
                add_generation_prompt=True
            ).to(model.device)
            
            outputs = model.generate(
                inputs,
                max_new_tokens=250,
                temperature=0.7,
                do_sample=True
            )
            
            response2 = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            print(f"User: {conversation[-1]['content']}")
            print(f"Assistant: {response2}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    @staticmethod
    def llama_with_streaming():
        """
        Streaming generation with Llama for real-time output
        """
        print("\n" + "="*80)
        print("LLAMA 2 - Streaming Generation")
        print("="*80)
        
        model_name = "meta-llama/Llama-2-7b-chat-hf"
        
        try:
            from transformers import TextIteratorStreamer
            from threading import Thread
            
            tokenizer = AutoTokenizer.from_pretrained(model_name, token=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                token=True,
                load_in_8bit=True
            )
            
            prompt = "[INST] Write a short story about a robot learning to paint. [/INST]"
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            
            streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True)
            
            generation_kwargs = dict(
                inputs,
                streamer=streamer,
                max_new_tokens=200,
                temperature=0.8,
                do_sample=True
            )
            
            thread = Thread(target=model.generate, kwargs=generation_kwargs)
            thread.start()
            
            print("Streaming output:")
            print("-" * 80)
            for text in streamer:
                print(text, end="", flush=True)
            print("\n" + "-" * 80)
            
        except Exception as e:
            print(f"Error: {e}")
    
    @staticmethod
    def code_llama_with_infilling():
        """
        CodeLlama with code infilling and completion
        """
        print("\n" + "="*80)
        print("CODE LLAMA - Code Infilling & Completion")
        print("="*80)
        
        model_name = "codellama/CodeLlama-7b-Instruct-hf"
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, token=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                token=True
            )
            
            # Example 1: Function completion
            code1 = """[INST] Write a Python function to check if a number is prime. [/INST]"""
            
            inputs = tokenizer(code1, return_tensors="pt").to(model.device)
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.1,  # Very low temperature for deterministic code
                do_sample=True
            )
            
            completed_code1 = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Example 1 - Function Generation:")
            print(completed_code1)
            print("\n")
            
            # Example 2: Bug fixing
            code2 = """[INST] Fix this Python code:
def factorial(n):
    if n = 1:
        return 1
    return n * factorial(n-1)
[/INST]"""
            
            inputs = tokenizer(code2, return_tensors="pt").to(model.device)
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.1
            )
            
            fixed_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Example 2 - Bug Fixing:")
            print(fixed_code)
            
        except Exception as e:
            print(f"Error: {e}")


# ============================================================================
# SPECIALIZED USE CASES
# ============================================================================

class SpecializedUseCases:
    """Real-world applications of different models"""
    
    @staticmethod
    def semantic_search_with_embeddings():
        """
        Generate embeddings for semantic search using BERT-based models
        """
        print("\n" + "="*80)
        print("BERT - Semantic Search with Embeddings")
        print("="*80)
        
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            from numpy.linalg import norm
            
            # Load a model optimized for semantic similarity
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            # Knowledge base documents
            documents = [
                "Python is a high-level programming language known for its simplicity.",
                "Machine learning is a subset of artificial intelligence.",
                "Dogs are domesticated animals that have been companions to humans for thousands of years.",
                "Neural networks are computational models inspired by biological neural networks.",
                "JavaScript is primarily used for web development.",
                "Deep learning uses multiple layers to progressively extract features from data."
            ]
            
            # Generate embeddings for all documents
            doc_embeddings = model.encode(documents)
            
            # User queries
            queries = [
                "What is AI and machine learning?",
                "Tell me about programming languages",
                "Information about pets"
            ]
            
            for query in queries:
                query_embedding = model.encode([query])[0]
                
                # Calculate cosine similarity
                similarities = []
                for doc_emb in doc_embeddings:
                    similarity = np.dot(query_embedding, doc_emb) / (norm(query_embedding) * norm(doc_emb))
                    similarities.append(similarity)
                
                print(f"\nQuery: {query}")
                print("Top 3 most similar documents:")
                top_indices = np.argsort(similarities)[::-1][:3]
                for idx in top_indices:
                    print(f"  Score {similarities[idx]:.4f}: {documents[idx]}")
                    
        except Exception as e:
            print(f"Error: {e}")
            print("Install: pip install sentence-transformers")
    
    @staticmethod
    def zero_shot_classification():
        """
        Zero-shot classification without training data
        """
        print("\n" + "="*80)
        print("BART - Zero-Shot Classification")
        print("="*80)
        
        classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        texts = [
            "The new iPhone 15 features an improved camera and longer battery life.",
            "The Lakers won the championship game in overtime.",
            "Climate change is affecting weather patterns worldwide.",
            "The latest Marvel movie broke box office records."
        ]
        
        candidate_labels = ["technology", "sports", "environment", "entertainment"]
        
        for text in texts:
            result = classifier(text, candidate_labels)
            print(f"\nText: {text}")
            print("Classifications:")
            for label, score in zip(result['labels'][:2], result['scores'][:2]):
                print(f"  {label}: {score:.4f}")
    
    @staticmethod
    def named_entity_recognition():
        """
        Extract named entities from text
        """
        print("\n" + "="*80)
        print("RoBERTa - Named Entity Recognition (NER)")
        print("="*80)
        
        ner = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
        
        texts = [
            "Apple Inc. was founded by Steve Jobs in Cupertino, California.",
            "Elon Musk announced Tesla's new factory in Berlin, Germany.",
            "The Amazon rainforest spans across Brazil and several other countries."
        ]
        
        for text in texts:
            entities = ner(text)
            print(f"\nText: {text}")
            print("Entities found:")
            for entity in entities:
                print(f"  {entity['word']}: {entity['entity_group']} (score: {entity['score']:.4f})")
    
    @staticmethod
    def text_to_sql_generation():
        """
        Generate SQL queries from natural language using T5
        """
        print("\n" + "="*80)
        print("T5 - Natural Language to SQL")
        print("="*80)
        
        try:
            model_name = "gaussalgo/T5-LM-Large-text2sql-spider"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Schema definition
            schema = """
            Table: employees (id, name, department, salary, hire_date)
            Table: departments (id, name, manager_id)
            """
            
            queries = [
                "Get all employees in the sales department",
                "Find the average salary by department",
                "List employees hired after 2020"
            ]
            
            print(f"Database Schema:\n{schema}\n")
            
            for query in queries:
                input_text = f"translate English to SQL: {query}"
                inputs = tokenizer(input_text, return_tensors="pt")
                outputs = model.generate(**inputs, max_length=100)
                sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                print(f"Natural Language: {query}")
                print(f"SQL Query: {sql}\n")
                
        except Exception as e:
            print(f"Error: {e}")
            print("Note: This is an example - actual model may need different handling")
    
    @staticmethod
    def document_question_answering():
        """
        Answer questions about documents using RoBERTa
        """
        print("\n" + "="*80)
        print("RoBERTa - Document Question Answering")
        print("="*80)
        
        qa_pipeline = pipeline(
            "question-answering",
            model="deepset/roberta-base-squad2"
        )
        
        context = """
        Python is a high-level, interpreted programming language created by Guido van Rossum.
        It was first released in 1991. Python's design philosophy emphasizes code readability
        with its notable use of significant indentation. Python is dynamically typed and
        garbage-collected. It supports multiple programming paradigms, including structured,
        object-oriented and functional programming. It is often described as a "batteries included"
        language due to its comprehensive standard library.
        """
        
        questions = [
            "Who created Python?",
            "When was Python first released?",
            "What programming paradigms does Python support?",
            "What is Python's design philosophy?",
            "Is Python statically or dynamically typed?"
        ]
        
        print(f"Context: {context[:100]}...\n")
        
        for question in questions:
            result = qa_pipeline(question=question, context=context)
            print(f"Q: {question}")
            print(f"A: {result['answer']} (confidence: {result['score']:.4f})\n")


# ============================================================================
# MODEL COMPARISON AND BENCHMARKING
# ============================================================================

class ModelComparison:
    """Compare different models for the same task"""
    
    @staticmethod
    def compare_sentiment_analysis():
        """
        Compare sentiment analysis across different models
        """
        print("\n" + "="*80)
        print("COMPARISON - Sentiment Analysis Across Models")
        print("="*80)
        
        models = [
            "distilbert-base-uncased-finetuned-sst-2-english",
            "cardiffnlp/twitter-roberta-base-sentiment",
            "nlptown/bert-base-multilingual-uncased-sentiment"
        ]
        
        test_text = "This product exceeded my expectations! Absolutely love it!"
        
        print(f"Test text: {test_text}\n")
        
        for model_name in models:
            try:
                classifier = pipeline("sentiment-analysis", model=model_name)
                result = classifier(test_text)[0]
                print(f"Model: {model_name.split('/')[-1]}")
                print(f"  Sentiment: {result['label']}, Score: {result['score']:.4f}\n")
            except Exception as e:
                print(f"Model: {model_name} - Error: {e}\n")
    
    @staticmethod
    def compare_text_generation():
        """
        Compare text generation quality across models
        """
        print("\n" + "="*80)
        print("COMPARISON - Text Generation Quality")
        print("="*80)
        
        prompt = "The future of artificial intelligence will"
        
        models_config = [
            ("gpt2", "GPT-2"),
            ("gpt2-medium", "GPT-2 Medium"),
            ("distilgpt2", "DistilGPT-2")
        ]
        
        print(f"Prompt: {prompt}\n")
        
        for model_name, display_name in models_config:
            try:
                generator = pipeline("text-generation", model=model_name)
                output = generator(
                    prompt,
                    max_length=50,
                    num_return_sequences=1,
                    temperature=0.7
                )[0]['generated_text']
                
                print(f"{display_name}:")
                print(f"  {output}\n")
            except Exception as e:
                print(f"{display_name} - Error: {e}\n")


# ============================================================================
# PERFORMANCE OPTIMIZATION TECHNIQUES
# ============================================================================

class OptimizationTechniques:
    """Techniques to optimize model inference"""
    
    @staticmethod
    def quantization_example():
        """
        Model quantization for reduced memory usage
        """
        print("\n" + "="*80)
        print("OPTIMIZATION - 8-bit Quantization")
        print("="*80)
        
        from transformers import BitsAndBytesConfig
        
        model_name = "meta-llama/Llama-2-7b-chat-hf"
        
        try:
            # 8-bit quantization configuration
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0,
                llm_int8_has_fp16_weight=False
            )
            
            tokenizer = AutoTokenizer.from_pretrained(model_name, token=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map="auto",
                token=True
            )
            
            print(f"Model loaded with 8-bit quantization")
            print(f"Memory footprint reduced by approximately 75%")
            
            # Test inference
            prompt = "[INST] What is quantization in neural networks? [/INST]"
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            
            outputs = model.generate(**inputs, max_new_tokens=100)
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            print(f"\nTest inference successful:")
            print(f"Response: {response[:200]}...")
            
        except Exception as e:
            print(f"Error: {e}")
    
    @staticmethod
    def batch_processing():
        """
        Batch processing for improved throughput
        """
        print("\n" + "="*80)
        print("OPTIMIZATION - Batch Processing")
        print("="*80)
        
        classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Multiple texts to process
        texts = [
            "I love this product!",
            "This is terrible.",
            "It's okay, nothing special.",
            "Best purchase ever!",
            "Would not recommend.",
            "Exceeded my expectations!",
            "Waste of money.",
            "Pretty good overall."
        ]
        
        import time
        
        # Single processing
        start = time.time()
        for text in texts:
            _ = classifier(text)
        single_time = time.time() - start
        
        # Batch processing
        start = time.time()
        results = classifier(texts, batch_size=4)
        batch_time = time.time() - start
        
        print(f"Single processing time: {single_time:.4f}s")
        print(f"Batch processing time: {batch_time:.4f}s")
        print(f"Speedup: {single_time/batch_time:.2f}x")
        
        print("\nResults:")
        for text, result in zip(texts[:3], results[:3]):
            print(f"  '{text}' -> {result['label']} ({result['score']:.4f})")
    
    @staticmethod
    def caching_strategy():
        """
        Implement caching for repeated queries
        """
        print("\n" + "="*80)
        print("OPTIMIZATION - Response Caching")
        print("="*80)
        
        from functools import lru_cache
        import time
        
        generator = pipeline("text-generation", model="gpt2")
        
        @lru_cache(maxsize=100)
        def cached_generate(prompt):
            result = generator(prompt, max_length=50, num_return_sequences=1)
            return result[0]['generated_text']
        
        test_prompt = "The importance of machine learning is"
        
        # First call (not cached)
        start = time.time()
        result1 = cached_generate(test_prompt)
        time1 = time.time() - start
        
        # Second call (cached)
        start = time.time()
        result2 = cached_generate(test_prompt)
        time2 = time.time() - start
        
        print(f"First call (not cached): {time1:.4f}s")
        print(f"Second call (cached): {time2:.4f}s")
        print(f"Speedup: {time1/time2:.2f}x")
        print(f"\nGenerated: {result1[:100]}...")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all advanced examples"""
    
    print("\n" + "="*80)
    print("ADVANCED HUGGING FACE EXAMPLES")
    print("Copyright 2025-2030 - Ashutosh Sinha (ajsinha@gmail.com)")
    print("="*80)
    
    # Advanced Llama Examples
    print("\n\n### ADVANCED LLAMA EXAMPLES ###")
    llama_examples = LlamaAdvancedExamples()
    llama_examples.llama2_with_custom_system_prompt()
    llama_examples.llama3_multi_turn_conversation()
    llama_examples.llama_with_streaming()
    llama_examples.code_llama_with_infilling()
    
    # Specialized Use Cases
    print("\n\n### SPECIALIZED USE CASES ###")
    use_cases = SpecializedUseCases()
    use_cases.semantic_search_with_embeddings()
    use_cases.zero_shot_classification()
    use_cases.named_entity_recognition()
    use_cases.document_question_answering()
    
    # Model Comparisons
    print("\n\n### MODEL COMPARISONS ###")
    comparisons = ModelComparison()
    comparisons.compare_sentiment_analysis()
    comparisons.compare_text_generation()
    
    # Optimization Techniques
    print("\n\n### OPTIMIZATION TECHNIQUES ###")
    optimizations = OptimizationTechniques()
    optimizations.quantization_example()
    optimizations.batch_processing()
    optimizations.caching_strategy()
    
    print("\n" + "="*80)
    print("All advanced examples completed!")
    print("="*80)


if __name__ == "__main__":
    main()
