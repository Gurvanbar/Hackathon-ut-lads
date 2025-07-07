#!/usr/bin/env python3
"""
Example client for testing the Genie OpenAI-compatible API.
This script demonstrates how to use the API with both raw requests and OpenAI library.
"""

import json
import requests
from typing import List, Dict

class GenieOpenAIClient:
    """Simple client for the Genie OpenAI-compatible API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        
    def list_models(self) -> Dict:
        """List available models"""
        response = requests.get(f"{self.base_url}/v1/models")
        response.raise_for_status()
        return response.json()
    
    def chat_completion(self, messages: List[Dict], **kwargs) -> Dict:
        """Create a chat completion"""
        data = {
            "model": kwargs.get("model", "genie-llama-3.2-3b"),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.8),
            "max_tokens": kwargs.get("max_tokens", 1024),
            "top_p": kwargs.get("top_p", 0.95),
            "top_k": kwargs.get("top_k", 40),
            "stream": kwargs.get("stream", False)
        }
        
        response = requests.post(f"{self.base_url}/v1/chat/completions", json=data)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict:
        """Check server health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

def example_with_requests():
    """Example using raw requests"""
    print("=== Testing with raw requests ===")
    
    client = GenieOpenAIClient()
    
    # Health check
    try:
        health = client.health_check()
        print(f"Health check: {health}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # List models
    try:
        models = client.list_models()
        print(f"Available models: {json.dumps(models, indent=2)}")
    except Exception as e:
        print(f"Failed to list models: {e}")
        return
    
    # Chat completion
    messages = [
        {"role": "user", "content": "Hello! Can you tell me a short joke?"}
    ]
    
    try:
        completion = client.chat_completion(messages)
        print(f"Chat completion response:")
        print(json.dumps(completion, indent=2))
        print(f"Assistant response: {completion['choices'][0]['message']['content']}")
    except Exception as e:
        print(f"Chat completion failed: {e}")

def example_with_openai_library():
    """Example using OpenAI library (if available)"""
    print("\n=== Testing with OpenAI library ===")
    
    try:
        from openai import OpenAI
        
        # Initialize OpenAI client with custom base URL
        client = OpenAI(
            base_url="http://127.0.0.1:8000/v1",
            api_key="dummy-key"  # Required by OpenAI library but not used by our server
        )
        
        # List models
        models = client.models.list()
        print(f"Available models: {[model.id for model in models.data]}")
        
        # Chat completion
        completion = client.chat.completions.create(
            model="genie-llama-3.2-3b",
            messages=[
                {"role": "user", "content": "Hello! Can you tell me a short joke?"}
            ],
            temperature=0.8,
            max_tokens=1024
        )
        
        print(f"Assistant response: {completion.choices[0].message.content}")
        
    except ImportError:
        print("OpenAI library not installed. Run: pip install openai")
    except Exception as e:
        print(f"OpenAI library test failed: {e}")

def interactive_chat():
    """Interactive chat session"""
    print("\n=== Interactive Chat (type 'quit' to exit) ===")
    
    client = GenieOpenAIClient()
    messages = []
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_input:
            continue
        
        messages.append({"role": "user", "content": user_input})
        
        try:
            completion = client.chat_completion(messages)
            assistant_response = completion['choices'][0]['message']['content']
            print(f"Assistant: {assistant_response}")
            
            messages.append({"role": "assistant", "content": assistant_response})
            
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function"""
    print("Genie OpenAI-Compatible API Client Example")
    print("==========================================")
    
    # Test with raw requests
    # example_with_requests()
    
    # Test with OpenAI library
    # example_with_openai_library()
    
    # Interactive chat
    try:
        interactive_chat()
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    main()
