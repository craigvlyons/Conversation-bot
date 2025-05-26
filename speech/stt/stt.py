
import warnings
# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="whisper")
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

import whisper

class STT:
    def __init__(self):
        self.model = whisper.load_model("tiny", device="cpu")

    def transcribe(self, audio_file):
        result = self.model.transcribe(audio_file)
        return result["text"]