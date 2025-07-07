from pydantic import BaseModel
import subprocess
from typing import List, Optional, Dict, Any
import time
import os

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
    
    def generate_response(self, messages: List[ChatMessage], **kwargs) -> str:
        """Generate a response using the Genie model"""
        # Convert messages to Llama format prompt
        prompt = self._messages_to_llama_prompt(messages)
        
        try:
            # Get the directory containing the Genie executable
            genie_dir = os.path.dirname(os.path.abspath(self.genie_path))
            
            # Run Genie with command-line arguments, setting the working directory
            result = subprocess.run(
                [self.genie_path, "-c", self.config_path, "-p", prompt],
                capture_output=True,
                text=True,
                timeout=600,  # 10 min timeout
                cwd=genie_dir  # Set working directory to where the executable is located
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Genie process failed with return code {result.returncode}: {result.stderr}")
            
            # Parse the output to extract the response
            output = result.stdout
            
            # Look for content between [BEGIN]: and [END]
            begin_marker = "[BEGIN]:"
            end_marker = "[END]"
            
            begin_idx = output.find(begin_marker)
            if begin_idx != -1:
                begin_idx += len(begin_marker)
                end_idx = output.find(end_marker, begin_idx)
                if end_idx != -1:
                    response = output[begin_idx:end_idx].strip()
                    return response
            
            # Fallback: return everything after the prompt line
            lines = output.split('\n')
            response_lines = []
            found_prompt = False
            
            for line in lines:
                if "[PROMPT]:" in line:
                    found_prompt = True
                    continue
                if found_prompt and line.strip() and not line.startswith("["):
                    response_lines.append(line.strip())
            
            if response_lines:
                return '\n'.join(response_lines)
            
            # Final fallback
            return output.strip()
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Genie process timed out")
        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")
    
    def _messages_to_llama_prompt(self, messages: List[ChatMessage]) -> str:
        """Convert OpenAI messages format to Llama chat template format"""
        prompt = "<|begin_of_text|>"
        
        for message in messages:
            if message.role == "system":
                prompt += f"<|start_header_id|>system<|end_header_id|>\n\n{message.content}<|eot_id|>"
            elif message.role == "user":
                prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{message.content}<|eot_id|>"
            elif message.role == "assistant":
                prompt += f"<|start_header_id|>assistant<|end_header_id|>\n\n{message.content}<|eot_id|>"
        
        # Add the assistant header to start the response
        prompt += "<|start_header_id|>assistant<|end_header_id|>"
        
        return prompt
    
    def close(self):
        """Close method for compatibility - not needed for command-line usage"""
        pass