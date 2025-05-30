"""
Centralized constants for environment variables and configuration.
Import this file and use the constants directly instead of calling os.getenv repeatedly.
"""
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env if present
load_dotenv()

# Gemini API Key
GEMINI_KEY = os.getenv("GEMINI_KEY")
# Picovoice/Porcupine Key
PRORCUPINE_KEY = os.getenv("PRORCUPINE_KEY")
# eSpeak NG Phonemizer paths
# PHONEMIZER_ESPEAK_LIBRARY = os.getenv("PHONEMIZER_ESPEAK_LIBRARY")
# PHONEMIZER_ESPEAK_PATH = os.getenv("PHONEMIZER_ESPEAK_PATH")
# Kokoro TTS (add more as needed)
# KOKORO_TTS_PATH = os.getenv("KOKORO_TTS_PATH")
# Azure DevOps/Function keys (add more as needed)
AZURE_FUNCTION_URL = os.getenv("AZURE_FUNCTION_URL")
AZURE_FUNCTION_APP_KEY = os.getenv("AZURE_FUNCTION_APP_KEY")
AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USERNAME = os.getenv("DB_USERNAME") 
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Default to INFO unless overridden by environment variable
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Convert string to logging level constant
LOG_LEVEL_VALUE = getattr(logging, LOG_LEVEL, logging.INFO)