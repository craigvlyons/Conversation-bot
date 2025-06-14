"""
Centralized constants for environment variables and configuration.
Import this file and use the constants directly instead of calling os.getenv repeatedly.
"""
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

# Load environment variables from .env if present
load_dotenv()

# Get platform configuration for path resolution
try:
    from utils.platform_config import get_platform_config
    _platform_config = get_platform_config()
    BASE_DIR = str(_platform_config.base_dir)
    DATA_DIR = str(_platform_config.data_dir)
    TEMP_MEMORY_DIR = str(_platform_config.get_temp_memory_dir())
except ImportError:
    # Fallback if platform_config is not available (avoid circular imports)
    BASE_DIR = str(Path(__file__).parent.parent)
    DATA_DIR = os.path.join(BASE_DIR, "data")
    TEMP_MEMORY_DIR = os.path.join(BASE_DIR, "temp_memory")

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
LOG_LEVEL_VALUE = getattr(logging, LOG_LEVEL)

# MCP server configuration
MCP_SERVERS = {
    "azure-devops": {
        "url": "http://127.0.0.1:8000/sse"
    }
}