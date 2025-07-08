# Voxmail AI

![image](https://github.com/user-attachments/assets/ea88e707-0099-4823-b05f-8b4ac75fe75a)

> From voice to email instantly :🎙️ Speak. ✉️ Send. ✅ Done.  
**Voxmail AI** is a locally-running voice-powered assistant that helps professionals write clear, personalized, and secure emails, just by talking.

---

## 🚀 Overview

Voxmail AI lets you respond to emails in seconds, just copy the message, hit your keyboard shortcut, speak your reply, and instantly see a professionally written response. Powered by on-device voice recognition and natural language generation, Voxmail AI runs locally to protect your data and ensure full privacy compliance.

---

## ⌨️ Keyboard Shortcuts VS UI

To make it easy to use for anyone, we have created a GUI that you can enable by unckecking "Auto-read from clipboard". However, we very much recommand to use it though keyboard shortcuts (by enabling auto-read). 
The keyboard shortcut to enable it is by default "ctrl space" but you can change this in the config file.
It will read the content of you clipboard (you should have copy the email you want to anwser to), record what you say (you say what you want to anwser to the email), transcribe you audio, detect who send the email, if he is not part of the directory offers you to add it to the directory to know the relationship you have with him, then ask an AI to write the email and it will paste it directetly on your cursor 

---

## 🧠 Key Features

- 🎤 **Voice-to-Email**: Speak naturally — Voxmail AI turns your voice into professionally formatted emails.
- 🔒 **Local Processing**: All data stays on your device — no cloud transmission. Perfect for regulated industries.
- 🌐 **Multilingual Support**: Compose emails in multiple languages with automatic tone matching.
- 📥 **Email Integration**: Compatible any with email services.
- 💁‍♂️ **Contact Framework**: The AI recognize who it is talking to (your boss, a friend etc).

---

## 🛠️ Tech Stack

- **Frontend**: Tkinter (to change in the future)
- **Voice Recognition**: faster-whisper
- **Text Generation**: On-device LLM (Llama 3.2) on the NPU, CPU, or GPU, or online with Groq

---

## 🚀 Future

- **Visual**: Vision recognition to automatically detect the mail and the sender
- **Improved performance**: Improve the Genie backend server
- **UI**: Going to PyQt instead of Tkinter and setup a graphic chart
- **Models**: More models to come

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
Launch the server so make genie a openai compatible server
![image](https://github.com/user-attachments/assets/6f5a70b3-d1c9-491a-a851-868a21c8d6ef)


# AnythingLLM
https://anythingllm.com/desktop download it and setup a developer key

# Groq
Get an api key and add it to the config

# Ollama
Install Ollama

Please note that we will download models if they are not already there so your first requests can be slow
