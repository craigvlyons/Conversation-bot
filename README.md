# Convo Bot: AI-Powered Voice Assistant

Convo Bot is a voice-controlled AI assistant that integrates wake word detection, speech-to-text (STT), text-to-speech (TTS), and a powerful Gemini AI model to provide intelligent, conversational responses. The system listens for a wake word, records user input, transcribes the speech, processes it using the Gemini AI model, and responds through a TTS engine.

---

## Features

- **Wake Word Detection**: Activates the bot when the user speaks a predefined wake word.
- **Speech-to-Text (STT)**: Converts recorded audio into text using an STT engine.
- **AI-Powered Responses**: Leverages the Gemini AI model to generate intelligent and contextually relevant replies.
- **Text-to-Speech (TTS)**: Synthesizes the AI-generated response into natural-sounding speech using Kokoro TTS.
- **Custom Commands**: Includes a special command, `"Stop listening"`, to gracefully shut down the assistant.

---

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd convo_bot
```
# Windows
```bash
python -m venv venv
venv\Scripts\activate
```

# mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

---

## Wake Word Detection (Picovoice)
Picovoice provides a highly efficient wake word detection engine. To use it, you'll need an access key and potentially their SDK.
- Website: https://picovoice.ai/
- Documentation: https://picovoice.ai/docs/quick-start/
- Access Key: You can sign up on the website and get a free trial key.

## Kokoro Text-to-Speech (TTS)
Kokoro Repository:
- Kokoro is your text-to-speech engine. Follow its specific setup instructions for installation.
- GitHub Repo (example): https://huggingface.co/hexgrad/Kokoro-82M

---

## Resources

- **Wake Word Detection (Picovoice)**:
  - Website: [https://picovoice.ai/](https://picovoice.ai/)
  - Documentation: [https://picovoice.ai/docs/quick-start/](https://picovoice.ai/docs/quick-start/)

- **Text-to-Speech (Kokoro)**:
  - Repository: [https://huggingface.co/hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)

- **Gemini AI Model**:
  - API Documentation: Refer to your Gemini service provider.

- **eSpeak NG (Phonemizer)**:
  - Repository: [https://github.com/espeak-ng/espeak-ng](https://github.com/espeak-ng/espeak-ng)


---

## Setup environment variables.
- PRORCUPINE_KEY=<your-picovoice-access-key>
- GEMINI_KEY=<your-gemini-api-key>

## Follow the installation instructions in the Kokoro README.md

## Install eSpeak ng and add the locations in KokoroTTS.py
- PHONEMIZER_ESPEAK_LIBRARY=C:\Program Files\eSpeak NG\libespeak-ng.dll
- PHONEMIZER_ESPEAK_PATH=C:\Program Files\eSpeak NG\espeak-ng.exe

---


## Code Structure

```plaintext
convo_bot/
│
├── main.py                    # Entry point for the bot
├── .env                       # Environment variables (not tracked by Git)
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
│
├── recording/                 # Audio recording components
│   ├── AutoRecorder.py        # Handles audio recording
│   └── audio_out/             # Directory for recorded audio files
│
├── stt/                       # Speech-to-text components
│   ├── STT.py                 # Handles transcription
│
├── wake_word/                 # Wake word detection components
│   ├── WakeWordDetector.py    # Detects wake words
│
├── Kokoro/                    # Text-to-speech components
│   ├── KokoroTTS.py           # Synthesizes and plays TTS responses
│   ├── models.py              # Kokoro-specific model utilities
│   ├── istftnet.py            # Utility for audio decoding
│
├── models/                    # Local LLM models
│   ├── model_loader.py        # Loads and queries LLaMA or other LLMs
│
└── logs/                      # Log files for debugging
```

