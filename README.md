# Voxmail AI

> From voice to email instantly :🎙️ Speak. ✉️ Send. ✅ Done.  
**Voxmail AI** is a locally-running voice-powered assistant that helps professionals write clear, personalized, and secure emails, just by talking.

---

## 🚀 Overview

<p>Voxmail AI lets you respond to emails in seconds, just copy the message, hit your keyboard shortcut, speak your reply, and instantly see a professionally written response. Powered by on-device voice recognition and natural language generation, Voxmail AI runs locally to protect your data and ensure full privacy compliance.

---

## 🧠 Key Features

- 🎤 **Voice-to-Email**: Speak naturally — Voxmail AI turns your voice into professionally formatted emails.
- 🔒 **Local Processing**: All data stays on your device — no cloud transmission. Perfect for regulated industries.
- 🌐 **Multilingual Support**: Compose emails in multiple languages with automatic tone matching.
- 📥 **Email Integration**: Compatible with email services.

---

## 🛠️ Tech Stack

- **Frontend**: Tkinter
- **Voice Recognition**: Whisper.cpp
- **Text Generation**: On-device LLM (Llama 3.2)

---

## 📦 Installation

```bash
git clone https://github.com/Gurvanbar/Hackathon-ut-lads.git
cd Hackathon-ut-lads
pip install -r requirements.txt
```
Fill up the `config.json` and the `config_settings.py`
```bash
python main.py
```

# Genie
Note that you have to add the 3 .bin files (the model) for the genie LLM provider from : `https://huggingface.co/Volko76/Llama-3.2-3B-Genie-Compatible-QNN-Binaries/tree/main/genie_bundle`

# AnythingLLM
https://anythingllm.com/desktop download it and setup a developer key

# Groq
Get an api key and add it to the config

# Ollama
Install Ollama

Please note that we will download models if they are not already there so your first requests can be slow
