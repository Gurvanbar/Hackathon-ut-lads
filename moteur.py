import ollama
import os
from dotenv import load_dotenv
# from scipy.io.wavfile import write
import wavio as wv
from groq import Groq
import json
import numpy as np
import keyboard
import pyperclip
from openai import OpenAI
from typing import Literal

load_dotenv()

# Load configuration
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config() 

def generate_mail(
    content: str,
    provider: Literal["groq", "ollama", "anythingllm", "genie"] = None,
    recipients: list = None
):
    # Use default provider from config if none specified
    if provider is None:
        provider = config["mail_generation"]["default_provider"]
    
def get_names_in_prompt(prompt, provider=None):
    # Use default provider from config if not explicitly given
    if provider is None:
        provider = config["mail_generation"]["default_provider"]

    system_prompt = (
        "Extract and return only the list of names of all people mentioned in the following prompt, "
        "specifically those to whom the message is addressed. "
        "Return a JSON array of names, e.g.: [\"Alice\", \"Bob\"]. No explanations."
    )

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"Prompt: {prompt}"
        }
    ]

    try:
        if provider == "groq":
            groq_config = config["providers"]["groq"]
            client = Groq()
            completion = client.chat.completions.create(
                model=groq_config["model"],
                messages=messages,
                temperature=groq_config["temperature"],
                max_completion_tokens=groq_config["max_completion_tokens"],
                top_p=groq_config["top_p"],
                stream=groq_config["stream"],
                response_format=groq_config["response_format"],
                stop=groq_config["stop"],
            )
            result = completion.choices[0].message.content.strip()

        elif provider == "ollama":
            ollama_config = config["providers"]["ollama"]
            response = ollama.chat(
                model=ollama_config["model"],
                messages=messages,
                options=ollama_config["options"]
            )
            result = response["message"]["content"].strip()

        elif provider == "anythingllm":
            anythingllm_config = config["providers"]["anythingllm"]
            client = OpenAI(
                base_url=anythingllm_config["base_url"],
                api_key=anythingllm_config["api_key"]
            )
            completion = client.chat.completions.create(
                model=anythingllm_config["model"],
                messages=messages,
                temperature=anythingllm_config["temperature"],
                max_tokens=anythingllm_config["max_tokens"],
                top_p=anythingllm_config["top_p"]
            )
            result = completion.choices[0].message.content.strip()

        elif provider == "genie":
            genie_config = config["providers"]["genie"]
            client = OpenAI(
                base_url=genie_config["base_url"],
                api_key=genie_config["api_key"]
            )
            completion = client.chat.completions.create(
                model=genie_config["model"],
                messages=messages,
                temperature=genie_config["temperature"],
                max_tokens=genie_config["max_tokens"],
                top_p=genie_config["top_p"]
            )
            result = completion.choices[0].message.content.strip()

        else:
            print(f"Unsupported provider: {provider}")
            return []

        # Attempt to parse the result as JSON
        try:
            names = json.loads(result)
            if isinstance(names, list):
                return names
            else:
                return names['names']
        except json.JSONDecodeError:
            return [result]

    except Exception as e:
        print(f"Error in get_names_in_prompt with provider '{provider}': {e}")
        return []

def generate_mail(content, provider = None, recipients = None):
    # Load sender info from user_data.json
    user_data_file = config["user_data_file"]
    with open(user_data_file, "r") as f:
        user_data = json.load(f)

    sender_name = user_data.get("name", "Your Name")
    sender_profession = user_data.get("function", "Your Profession")

    recipients_text = ""
    if recipients:
        recipients_text = "\n\nRecipient Info:\n"
        for person in recipients:
            recipients_text += f"- {person['name']} – {person['position']}: {person['description']}\n"


    messages = [
        {
            "role": "system",
            "content": config["mail_generation"]["system_prompt"]
        },
        {
            "role": "user",
            "content": (
                f"{content}\n"
                f"user_name: {sender_name}\n"
                f"user_profession: {sender_profession}"
                f"{recipients_text}"
            )
        }
    ]


    if provider == "groq":
        result = generate_groq(messages)
    elif provider == "ollama":
        result = generate_ollama(messages)
    elif provider == "anythingllm":
        result = generate_anythingllm(messages)
    elif provider == "genie":
        result = generate_genie(messages)
    else:
        result = "Unknown provider."

    # Try parsing the JSON result
    try:
        parsed = json.loads(result)
        return parsed.get("mail", result)
    except json.JSONDecodeError:
        return result





def generate_ollama(messages):
    # Generate mail using Ollama with configured model
    ollama_config = config["providers"]["ollama"]
    model_name = ollama_config["model"]
    try:
        response = ollama.chat(
            model=model_name,
            messages=messages,
            options=ollama_config["options"]
        )
        return response['message']['content']
    except ollama.ResponseError as e:
        if "not found" in str(e).lower():
            print(f"Model '{model_name}' not found. Downloading...")
            ollama.pull(model_name)
            # Retry after downloading
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options=ollama_config["options"]
            )
            return response['message']['content']
        else:
            raise

def generate_genie(messages):
    # Generate mail using Genie OpenAI-compatible API
    try:
        genie_config = config["providers"]["genie"]
        # Initialize OpenAI client with custom base URL for Genie
        client = OpenAI(
            base_url=genie_config["base_url"],
            api_key=genie_config["api_key"]
        )
        
        # Make chat completion request
        completion = client.chat.completions.create(
            model=genie_config["model"],
            messages=messages,
            temperature=genie_config["temperature"],
            max_tokens=genie_config["max_tokens"],
            top_p=genie_config["top_p"]
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error with Genie API: {e}")
        raise
    
def generate_anythingllm(messages):
    # Generate mail using AnythingLLM OpenAI-compatible API
    try:
        anythingllm_config = config["providers"]["anythingllm"]
        # Initialize OpenAI client with custom base URL for AnythingLLM
        client = OpenAI(
            base_url=anythingllm_config["base_url"],
            api_key=anythingllm_config["api_key"]
        )
        
        # Make chat completion request
        completion = client.chat.completions.create(
            model=anythingllm_config["model"],
            messages=messages,
            temperature=anythingllm_config["temperature"],
            max_tokens=anythingllm_config["max_tokens"],
            top_p=anythingllm_config["top_p"]
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f"Error with AnythingLLM API: {e}, falling back to Ollama")
        # Fallback to Ollama on any error
        return generate_ollama(messages)


def generate_groq(messages):
    # Generate mail using the language model
    groq_config = config["providers"]["groq"]
    client = Groq()
    completion = client.chat.completions.create(
        model=groq_config["model"],
        messages=messages,
        temperature=groq_config["temperature"],
        max_completion_tokens=groq_config["max_completion_tokens"],
        top_p=groq_config["top_p"],
        stream=groq_config["stream"],
        response_format=groq_config["response_format"],
        stop=groq_config["stop"],
    )

    return completion.choices[0].message.content