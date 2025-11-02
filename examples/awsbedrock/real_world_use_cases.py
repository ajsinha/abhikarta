"""
AWS Bedrock Real-World Use Cases

Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com

This module demonstrates practical real-world applications:
1. Content Generation Pipeline
2. Semantic Search System
3. Multi-Model Comparison Tool
4. Intelligent Chatbot
5. Document Analysis System
"""

import boto3
import json
from typing import List, Dict, Any
import numpy as np
from datetime import datetime


class ContentGenerationPipeline:
    """
    Use Case 1: Automated content generation using multiple models
    
    Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
    """
    
    def __init__(self, region_name='us-east-1'):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
    
    def generate_blog_post(self, topic: str) -> Dict[str, str]:
        """
        Generate a complete blog post with title, outline, content, and image
        """
        print(f"\n{'='*80}")
        print(f"CONTENT GENERATION PIPELINE: {topic}")
        print(f"{'='*80}")
        
        # Step 1: Generate title using Claude (creative)
        print("\n[Step 1/4] Generating title with Claude 3...")
        title = self._generate_title(topic)
        print(f"Title: {title}")
        
        # Step 2: Create outline using Llama (structured)
        print("\n[Step 2/4] Creating outline with Llama 3...")
        outline = self._generate_outline(topic, title)
        print(f"Outline:\n{outline}")
        
        # Step 3: Write content using Claude (high quality)
        print("\n[Step 3/4] Writing content with Claude 3 Sonnet...")
        content = self._generate_content(topic, title, outline)
        print(f"Content: {content[:200]}...")
        
        # Step 4: Generate featured image using Stability AI
        print("\n[Step 4/4] Generating featured image with Stable Diffusion...")
        image_path = self._generate_featured_image(title)
        print(f"Image saved to: {image_path}")
        
        return {
            'title': title,
            'outline': outline,
            'content': content,
            'image_path': image_path,
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_title(self, topic: str) -> str:
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [{
                "role": "user",
                "content": f"Create a catchy, SEO-friendly blog post title about: {topic}. Only respond with the title."
            }]
        }
        
        response = self.bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps(payload)
        )
        result = json.loads(response['body'].read())
        return result['content'][0]['text'].strip()
    
    def _generate_outline(self, topic: str, title: str) -> str:
        payload = {
            "prompt": f"Create a detailed outline for a blog post titled '{title}' about {topic}. Use bullet points.",
            "max_gen_len": 512,
            "temperature": 0.7
        }
        
        response = self.bedrock.invoke_model(
            modelId="meta.llama3-8b-instruct-v1:0",
            body=json.dumps(payload)
        )
        result = json.loads(response['body'].read())
        return result['generation']
    
    def _generate_content(self, topic: str, title: str, outline: str) -> str:
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "messages": [{
                "role": "user",
                "content": f"Write a comprehensive blog post with the title '{title}' following this outline:\n{outline}\n\nTopic: {topic}"
            }]
        }
        
        response = self.bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(payload)
        )
        result = json.loads(response['body'].read())
        return result['content'][0]['text']
    
    def _generate_featured_image(self, title: str) -> str:
        import base64
        
        payload = {
            "text_prompts": [{"text": f"Professional blog header image for: {title}", "weight": 1.0}],
            "cfg_scale": 8,
            "steps": 30
        }
        
        try:
            response = self.bedrock.invoke_model(
                modelId="stability.stable-diffusion-xl-v1",
                body=json.dumps(payload)
            )
            result = json.loads(response['body'].read())
            
            image_data = base64.b64decode(result['artifacts'][0]['base64'])
            image_path = f"/home/claude/blog_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            return image_path
        except:
            return "Image generation skipped (model access required)"


class SemanticSearchSystem:
    """
    Use Case 2: Build a semantic search system using embeddings
    
    Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
    """
    
    def __init__(self, region_name='us-east-1'):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
        self.document_embeddings = []
        self.documents = []
    
    def add_documents(self, documents: List[str]):
        """
        Add documents to the search index
        """
        print(f"\n{'='*80}")
        print(f"SEMANTIC SEARCH: Indexing {len(documents)} documents")
        print(f"{'='*80}")
        
        for i, doc in enumerate(documents, 1):
            print(f"\nIndexing document {i}/{len(documents)}: {doc[:50]}...")
            embedding = self._get_embedding(doc)
            self.documents.append(doc)
            self.document_embeddings.append(embedding)
        
        print(f"\n✓ Indexed {len(documents)} documents")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        """
        print(f"\n{'='*80}")
        print(f"SEMANTIC SEARCH: Query = '{query}'")
        print(f"{'='*80}")
        
        query_embedding = self._get_embedding(query)
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(self.document_embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append({
                'document': self.documents[i],
                'similarity': similarity,
                'index': i
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        results = similarities[:top_k]
        
        print(f"\nTop {top_k} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Similarity: {result['similarity']:.4f}")
            print(f"   Document: {result['document'][:100]}...")
        
        return results
    
    def _get_embedding(self, text: str) -> List[float]:
        payload = {"inputText": text}
        
        response = self.bedrock.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=json.dumps(payload)
        )
        result = json.loads(response['body'].read())
        return result['embedding']
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


class MultiModelComparison:
    """
    Use Case 3: Compare responses from different models
    
    Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
    """
    
    def __init__(self, region_name='us-east-1'):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
    
    def compare_models(self, prompt: str, models: List[str]) -> Dict[str, str]:
        """
        Get responses from multiple models for comparison
        """
        print(f"\n{'='*80}")
        print(f"MODEL COMPARISON")
        print(f"{'='*80}")
        print(f"Prompt: {prompt}")
        print(f"Models: {', '.join(models)}")
        
        results = {}
        
        for model in models:
            print(f"\n--- {model} ---")
            response = self._get_response(model, prompt)
            results[model] = response
            print(f"Response: {response[:200]}...")
        
        return results
    
    def _get_response(self, model: str, prompt: str) -> str:
        if 'llama' in model.lower():
            payload = {
                "prompt": prompt,
                "max_gen_len": 512,
                "temperature": 0.7
            }
            model_id = "meta.llama3-8b-instruct-v1:0"
            
            response = self.bedrock.invoke_model(modelId=model_id, body=json.dumps(payload))
            result = json.loads(response['body'].read())
            return result['generation']
        
        elif 'claude' in model.lower():
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "messages": [{"role": "user", "content": prompt}]
            }
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            
            response = self.bedrock.invoke_model(modelId=model_id, body=json.dumps(payload))
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
        
        elif 'titan' in model.lower():
            payload = {
                "inputText": prompt,
                "textGenerationConfig": {"maxTokenCount": 512}
            }
            model_id = "amazon.titan-text-express-v1"
            
            response = self.bedrock.invoke_model(modelId=model_id, body=json.dumps(payload))
            result = json.loads(response['body'].read())
            return result['results'][0]['outputText']
        
        return "Model not supported in this demo"


class IntelligentChatbot:
    """
    Use Case 4: Build a context-aware chatbot with Llama
    
    Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
    """
    
    def __init__(self, region_name='us-east-1'):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
        self.conversation_history = []
        self.system_prompt = "You are a helpful AI assistant."
    
    def chat(self, user_message: str) -> str:
        """
        Process a chat message and maintain conversation history
        """
        print(f"\nUser: {user_message}")
        
        # Build context from history
        context = self.system_prompt + "\n\n"
        for msg in self.conversation_history:
            context += f"{msg['role']}: {msg['content']}\n"
        context += f"User: {user_message}\nAssistant:"
        
        payload = {
            "prompt": context,
            "max_gen_len": 512,
            "temperature": 0.8
        }
        
        response = self.bedrock.invoke_model(
            modelId="meta.llama3-70b-instruct-v1:0",
            body=json.dumps(payload)
        )
        result = json.loads(response['body'].read())
        assistant_response = result['generation']
        
        # Update history
        self.conversation_history.append({
            "role": "User",
            "content": user_message
        })
        self.conversation_history.append({
            "role": "Assistant",
            "content": assistant_response
        })
        
        print(f"Assistant: {assistant_response}")
        return assistant_response
    
    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []


def demonstrate_use_cases():
    """
    Run demonstrations of all use cases
    
    Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
    """
    print("="*80)
    print("AWS BEDROCK REAL-WORLD USE CASES")
    print("Copyright 2025-2030 all rights reserved")
    print("Ashutosh Sinha, Email: ajsinha@gmail.com")
    print("="*80)
    
    try:
        # Use Case 1: Content Generation
        print("\n\n" + "="*80)
        print("USE CASE 1: CONTENT GENERATION PIPELINE")
        print("="*80)
        pipeline = ContentGenerationPipeline()
        blog_post = pipeline.generate_blog_post("The Future of Artificial Intelligence")
        print(f"\n✓ Generated complete blog post: {blog_post['title']}")
        
        # Use Case 2: Semantic Search
        print("\n\n" + "="*80)
        print("USE CASE 2: SEMANTIC SEARCH SYSTEM")
        print("="*80)
        search_system = SemanticSearchSystem()
        documents = [
            "Python is a high-level programming language known for its simplicity.",
            "Machine learning is a subset of artificial intelligence.",
            "JavaScript is commonly used for web development.",
            "Deep learning uses neural networks with multiple layers.",
            "Cloud computing provides on-demand computing resources."
        ]
        search_system.add_documents(documents)
        search_system.search("What is AI and ML?", top_k=3)
        
        # Use Case 3: Model Comparison
        print("\n\n" + "="*80)
        print("USE CASE 3: MULTI-MODEL COMPARISON")
        print("="*80)
        comparator = MultiModelComparison()
        comparator.compare_models(
            "Explain quantum computing in simple terms.",
            ["Llama", "Claude", "Titan"]
        )
        
        # Use Case 4: Intelligent Chatbot
        print("\n\n" + "="*80)
        print("USE CASE 4: INTELLIGENT CHATBOT")
        print("="*80)
        chatbot = IntelligentChatbot()
        chatbot.chat("What is machine learning?")
        chatbot.chat("Can you give me an example?")
        chatbot.chat("How is it used in practice?")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nNote: Some features require model access in AWS Bedrock console")
    
    print("\n" + "="*80)
    print("USE CASES DEMONSTRATION COMPLETED")
    print("Copyright 2025-2030 all rights reserved")
    print("Ashutosh Sinha, Email: ajsinha@gmail.com")
    print("="*80)


if __name__ == "__main__":
    demonstrate_use_cases()
