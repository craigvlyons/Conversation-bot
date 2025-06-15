# Import STT and wake word components (these should have minimal dependencies)
from speech.stt import stt

# Import TTS and wake word components conditionally to avoid dependency issues
try:
    from speech.tts import KokoroTTS
except ImportError as e:
    print(f"⚠️ TTS not available: {e}")
    KokoroTTS = None

try:
    from speech.wake_word.wake_word_detector import WakeWordDetector
    from speech.wake_word.wake_word_thread import WakeWordThread
except ImportError as e:
    print(f"⚠️ Wake word detection not available: {e}")
    WakeWordDetector = None
    WakeWordThread = None