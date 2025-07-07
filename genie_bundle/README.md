# Genie OpenAI-Compatible API

This directory contains a Python script that provides an OpenAI-compatible API endpoint for the Genie LLM model.

## Features

- **OpenAI-Compatible API**: Drop-in replacement for OpenAI API endpoints
- **FastAPI-based**: Modern, fast web framework with automatic API documentation
- **Local Execution**: Runs the Genie model locally using the provided executable
- **Standard Endpoints**: Supports `/v1/models` and `/v1/chat/completions`
- **Health Monitoring**: Includes health check endpoint

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

Run the server with default settings (localhost:8000):
```bash
python genie_openai_server.py
```

With custom host and port:
```bash
python genie_openai_server.py --host 0.0.0.0 --port 8080
```

With auto-reload for development:
```bash
python genie_openai_server.py --reload
```

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://127.0.0.1:8000/docs
- **Alternative docs**: http://127.0.0.1:8000/redoc
- **Health check**: http://127.0.0.1:8000/health

### Using the API

#### With curl

List models:
```bash
curl http://127.0.0.1:8000/v1/models
```

Chat completion:
```bash
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "genie-llama-3.2-3b",
    "messages": [
      {"role": "user", "content": "Hello! How are you?"}
    ],
    "temperature": 0.8,
    "max_tokens": 1024
  }'
```

#### With Python requests

```python
import requests

response = requests.post("http://127.0.0.1:8000/v1/chat/completions", json={
    "model": "genie-llama-3.2-3b",
    "messages": [
        {"role": "user", "content": "Hello! How are you?"}
    ],
    "temperature": 0.8,
    "max_tokens": 1024
})

result = response.json()
print(result["choices"][0]["message"]["content"])
```

#### With OpenAI Python library

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="dummy-key"  # Required but not used
)

completion = client.chat.completions.create(
    model="genie-llama-3.2-3b",
    messages=[
        {"role": "user", "content": "Hello! How are you?"}
    ],
    temperature=0.8,
    max_tokens=1024
)

print(completion.choices[0].message.content)
```

### Running the Example Client

Test the API with the provided example client:
```bash
python client_example.py
```

This will run various tests and provide an interactive chat interface.

## API Endpoints

### GET /v1/models
Lists available models.

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "genie-llama-3.2-3b",
      "object": "model",
      "created": 1704067200,
      "owned_by": "genie"
    }
  ]
}
```

### POST /v1/chat/completions
Creates a chat completion.

**Request Body:**
```json
{
  "model": "genie-llama-3.2-3b",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.8,
  "max_tokens": 1024,
  "top_p": 0.95,
  "top_k": 40,
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl-12345678",
  "object": "chat.completion",
  "created": 1704067200,
  "model": "genie-llama-3.2-3b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model": "genie-llama-3.2-3b"
}
```

## Configuration

The server automatically uses the following files from the same directory:
- `genie-t2t-run.exe` - The Genie executable
- `genie_config.json` - Genie configuration file

Make sure these files exist and are properly configured before starting the server.

## Parameters

The API supports the following parameters for chat completions:
- `model`: Model name (currently only "genie-llama-3.2-3b")
- `messages`: Array of message objects with role and content
- `temperature`: Sampling temperature (0.0 to 2.0)
- `max_tokens`: Maximum tokens to generate
- `top_p`: Nucleus sampling parameter
- `top_k`: Top-k sampling parameter
- `stream`: Whether to stream responses (not yet implemented)
- `stop`: Stop sequences (optional)

## Troubleshooting

1. **Server won't start**: Check that `genie-t2t-run.exe` and `genie_config.json` exist in the same directory
2. **Model errors**: Ensure the Genie model files (.bin files) are present and properly referenced in the config
3. **API errors**: Check the server logs for detailed error messages
4. **Performance issues**: Adjust the temperature and token limits based on your hardware capabilities

## Development

To modify the server behavior:
1. Edit `genie_openai_server.py`
2. Run with `--reload` flag for automatic reloading during development
3. Check the FastAPI documentation at `/docs` for testing

## Future Enhancements

- [ ] Streaming response support
- [ ] Multiple model support
- [ ] Authentication/API key validation
- [ ] Rate limiting
- [ ] Logging and metrics
- [ ] Docker containerization
