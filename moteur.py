import ollama
import os
from dotenv import load_dotenv
import sounddevice as sd
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
    email_received: str,
    i_want_to_respond: str,
    provider: Literal["groq", "ollama", "anythingllm", "genie"] = None
):
    # Use default provider from config if none specified
    if provider is None:
        provider = config["mail_generation"]["default_provider"]
    
    # Load sender info from user_data.json
    user_data_file = config["user_data_file"]
    with open(user_data_file, "r") as f:
        user_data = json.load(f)

    sender_name = user_data.get("name", "Your Name")
    sender_profession = user_data.get("function", "Your Profession")

    messages = [
        {
            "role": "system",
            "content": config["mail_generation"]["system_prompt"].replace("{sender_name}", sender_name).replace("{sender_profession}", sender_profession).replace("{email_received}", email_received).replace("{i_want_to_respond}", i_want_to_respond)
        },
        {
            "role": "user",
            "content": "Just answer the mail in JSON with the format: { \"mail\": \"This is a mail\" }"
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

def detect_audio_and_process(provider=None):
    keys_to_press = config["keybindings"]["recording_keys"]
    
    # Audio parameters from config
    audio_config = config["audio"]
    freq = audio_config["frequency"]
    channels = audio_config["channels"]
    chunk_duration = audio_config["chunk_duration"]
    chunk_size = int(freq * chunk_duration)

    print("Press and hold the spacebar to start recording...")

    all_chunks = []

    # Start stream
    stream = sd.InputStream(samplerate=freq, channels=channels)
    stream.start()

    # Continue recording while space is held
    condition = True
    while condition:
        for keys in keys_to_press:
            if not keyboard.is_pressed(keys):
                condition = False
        audio_chunk, _ = stream.read(chunk_size)
        all_chunks.append(audio_chunk)

    stream.stop()
    print("* Done recording")

    # Concatenation des extraits audio avec numpy
    recording = np.concatenate(all_chunks, axis=0)

    filename = os.path.dirname(__file__) + "/" + audio_config["output_file"]
    wv.write(filename, recording, freq, sampwidth=audio_config["sample_width"])
    
    # Transcription with configured settings
    transcription_config = config["transcription"]
    client = Groq()
    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),
            model=transcription_config["model"],
            language=transcription_config["language"],
            response_format=transcription_config["response_format"],
        )
    print(transcription.text)
    return transcription.text




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