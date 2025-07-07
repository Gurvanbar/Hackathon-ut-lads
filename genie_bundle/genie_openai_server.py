#!/usr/bin/env python3
"""
OpenAI-compatible API server for Genie LLM.
This script creates a FastAPI server that provides OpenAI-compatible endpoints
for the Genie model running locally.
"""

import json
import os
import subprocess
import threading
import time
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import tempfile
import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

# Pydantic models for OpenAI API compatibility
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "genie-llama-3.2-3b"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.8
    max_tokens: Optional[int] = 1024
    top_p: Optional[float] = 0.95
    top_k: Optional[int] = 40
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, int]] = None

class Model(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "genie"

class GenieClient:
    """Client to interact with the Genie executable"""
    
    def __init__(self, genie_path: str, config_path: str):
        self.genie_path = genie_path
        self.config_path = config_path
        self.process = None
        
    def start_process(self):
        """Start the Genie process if not already running"""
        if self.process is None or self.process.poll() is not None:
            try:
                self.process = subprocess.Popen(
                    [self.genie_path, "-c", self.config_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                # Give the process time to initialize
                time.sleep(2)
            except Exception as e:
                raise RuntimeError(f"Failed to start Genie process: {e}")
    
    def generate_response(self, messages: List[ChatMessage], **kwargs) -> str:
        """Generate a response using the Genie model"""
        self.start_process()
        
        # Convert messages to a prompt format
        prompt = self._messages_to_prompt(messages)
        
        try:
            # Send the prompt to the process
            self.process.stdin.write(prompt + "\n")
            self.process.stdin.flush()
            
            # Read the response
            response_lines = []
            while True:
                line = self.process.stdout.readline()
                if not line or line.strip() == "":
                    break
                response_lines.append(line.strip())
                
            response = "\n".join(response_lines)
            return response.strip()
            
        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")
    
    def _messages_to_prompt(self, messages: List[ChatMessage]) -> str:
        """Convert OpenAI messages format to a single prompt"""
        prompt_parts = []
        
        for message in messages:
            if message.role == "system":
                prompt_parts.append(f"System: {message.content}")
            elif message.role == "user":
                prompt_parts.append(f"User: {message.content}")
            elif message.role == "assistant":
                prompt_parts.append(f"Assistant: {message.content}")
        
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)
    
    def close(self):
        """Close the Genie process"""
        if self.process:
            self.process.terminate()
            self.process.wait()

# Initialize FastAPI app
app = FastAPI(title="Genie OpenAI Compatible API", version="1.0.0")

# Global Genie client
genie_client = None

def initialize_genie():
    """Initialize the Genie client"""
    global genie_client
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Paths to Genie executable and config
    genie_exe = os.path.join(script_dir, "genie-t2t-run.exe")
    config_file = os.path.join(script_dir, "genie_config.json")
    
    if not os.path.exists(genie_exe):
        raise FileNotFoundError(f"Genie executable not found: {genie_exe}")
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Genie config not found: {config_file}")
    
    genie_client = GenieClient(genie_exe, config_file)

@app.on_event("startup")
async def startup_event():
    """Initialize Genie on startup"""
    initialize_genie()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    if genie_client:
        genie_client.close()

@app.get("/v1/models")
async def list_models():
    """List available models"""
    return {
        "object": "list",
        "data": [
            Model(
                id="genie-llama-3.2-3b",
                created=int(datetime.now().timestamp()),
                owned_by="genie"
            )
        ]
    }

@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """Create a chat completion"""
    if not genie_client:
        raise HTTPException(status_code=500, detail="Genie client not initialized")
    
    try:
        # Generate response using Genie
        response_content = genie_client.generate_response(
            request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            top_k=request.top_k
        )
        
        # Create OpenAI-compatible response
        response = ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(datetime.now().timestamp()),
            model=request.model,
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }
            ],
            usage={
                "prompt_tokens": sum(len(msg.content.split()) for msg in request.messages),
                "completion_tokens": len(response_content.split()),
                "total_tokens": sum(len(msg.content.split()) for msg in request.messages) + len(response_content.split())
            }
        )
        
        if request.stream:
            # TODO: Implement streaming response
            raise HTTPException(status_code=501, detail="Streaming not yet implemented")
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating completion: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": "genie-llama-3.2-3b"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Genie OpenAI Compatible API",
        "version": "1.0.0",
        "endpoints": {
            "models": "/v1/models",
            "chat_completions": "/v1/chat/completions",
            "health": "/health"
        }
    }

def main():
    """Main function to run the server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Genie OpenAI Compatible API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"Starting Genie OpenAI Compatible API Server on {args.host}:{args.port}")
    print(f"API Documentation: http://{args.host}:{args.port}/docs")
    
    uvicorn.run(
        "genie_openai_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
