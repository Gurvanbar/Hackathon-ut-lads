# Voxmail AI

![Voxmail AI Logo](https://github.com/user-attachments/assets/ea88e707-0099-4823-b05f-8b4ac75fe75a)

> **Speak. Send. Done.**  
**Voxmail AI** is a productivity-first, voice-powered assistant that transforms spoken words into professional or friendly, personalized emails in seconds. It runs locally to ensure data security and compliance.

---

## 🚀 Overview

Voxmail AI streamlines email communication by allowing you to respond to emails effortlessly. Simply copy an email, trigger the app with a keyboard shortcut, speak your reply, and Voxmail AI generates a polished, ready-to-send email. Powered by on-device voice recognition (whisper) and on device Large Language Models (Llama), it prioritizes speed, privacy, and ease of use.

---

## 🎯 Key Features

- **🎤 Voice-to-Email**: Convert natural speech into professionally or friendly formatted emails.
- **🔒 Local Processing**: All data stays on your device, ensuring privacy and compliance with regulated industries.
- **🌐 Multilingual Support**: Compose emails in multiple languages with context-aware tone matching.
- **📥 Broad Compatibility**: Seamlessly integrates with any email service.
- **💁‍♂️ Contact Framework**: Automatically identifies senders and adapts responses based on your relationship (e.g., boss, colleague, friend).

---

## ⌨️ Usage: Keyboard Shortcuts vs. GUI

Voxmail AI offers two ways to interact:

- **Keyboard Shortcuts (Recommended for productivity)**: Enable "Auto-read from clipboard" in the config to use the default shortcut (`Ctrl + Space`, customizable). Copy an email to your clipboard, trigger the shortcut, speak your response, and Voxmail AI will:
  1. Transcribe your audio.
  2. Identify the sender and prompt to add them to your contact directory if new.
  3. Generate a professional email and paste it at your cursor.
- **Graphical User Interface (GUI)**: Disable "Auto-read from clipboard" to use the GUI for manual input. Ideal for users who prefer a visual interface.

---

## 🛠️ Tech Stack

- **Frontend**: Tkinter (planned migration to PyQt for enhanced UI).
- **Voice Recognition**: Faster-Whisper for efficient, on-device transcription.
- **Text Generation**: On-device LLM (Llama 3.2) using NPU, CPU, or GPU, with optional Groq API integration for online processing.

---

## 🚀 Roadmap

- **Vision Recognition**: Auto-detect email content and sender using visual input.
- **Performance Optimization**: Enhance the Genie backend server for faster processing.
- **Improved UI**: Transition to PyQt with a modern, cohesive design system.
- **Expanded Models**: Support additional LLMs for greater flexibility.

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- Git
- Compatible hardware (NPU, CPU, or GPU for on-device processing)
- API keys for Groq (optional) and AnythingLLM
- Ollama installed for local LLM support

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Gurvanbar/Hackathon-ut-lads.git
   cd Hackathon-ut-lads
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure settings:
   - Edit `config.json` and `config_settings.py` with your preferences (e.g., keyboard shortcuts, API keys).
4. Set up the Genie LLM server:
   - Download the three `.bin` model files from [Genie-Compatible Llama 3.2](https://huggingface.co/Volko76/Llama-3.2-3B-Genie-Compatible-QNN-Binaries/tree/main/genie_bundle).
   - Launch the Genie server to enable OpenAI-compatible API endpoints.
   - ![Genie Server](https://github.com/user-attachments/assets/6f5a70b3-d1c9-491a-a851-868a21c8d6ef)
5. Install and configure additional dependencies:
   - **AnythingLLM**: Download from [AnythingLLM Desktop](https://anythingllm.com/desktop) and set up a developer key.
   - **Groq**: Obtain an API key and add it to `config.json`.
   - **Ollama**: Install [Ollama](https://ollama.com/) for local model support.
6. Run the application:
   ```bash
   python main.py
   ```

> **Note**: The first run may be slower as models are downloaded. Subsequent runs will be faster.

---

🖥️ System Tray Integration

To keep your workspace uncluttered, Voxmail AI can be minimized to the system tray, ensuring it doesn't take up valuable screen space. We recommend enabling this feature for a seamless experience. Additionally, you can activate an overlay directly from the system tray, providing a convenient button to trigger the application instantly without navigating through menus.

---

## 🛠️ Configuration

- **config.json**: Set API keys, model preferences, and other settings.
- **config_settings.py**: Customize keyboard shortcuts (e.g., change `Ctrl + Space` to your preferred keybinding).
- **Contact Directory**: Add or update contacts to improve sender recognition and response personalization.

---

## 📝 Notes

- Ensure sufficient disk space for model downloads.
- For optimal performance, use a device with a dedicated NPU or GPU. We recommend the Qualcomm Snapdragon X Elite with his powerfull Hexagon NPU.
- Check the [GitHub repository](https://github.com/Gurvanbar/Hackathon-ut-lads) for updates and community contributions.

---

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m "Add YourFeature"`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

---

## 📬 Support

For issues, feature requests, or questions, please open an issue on the [GitHub repository](https://github.com/Gurvanbar/Hackathon-ut-lads/issues).

