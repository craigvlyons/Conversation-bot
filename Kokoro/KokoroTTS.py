import os
import sys
 # Set environment variables
os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = r"C:\\Program Files\\eSpeak NG\\libespeak-ng.dll"
os.environ["PHONEMIZER_ESPEAK_PATH"] = r"C:\\Program Files\\eSpeak NG\\espeak-ng.exe"

import torch
import pygame
from Kokoro.models import build_model
from Kokoro.kokoro import generate
import soundfile as sf
import time

class KokoroTTS:
    def __init__(self, device=None):
       
        # Setup device
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = "C:/convo_bot/Kokoro/kokoro-v0_19.pth"
        # Load model
        self.model = build_model(self.model_path, self.device)

        # Voice pack directory and output directory
        self.voices_dir = "C:/convo_bot/Kokoro/voices"
        self.output_dir = "C:/convo_bot/Kokoro/audio_out"
        self.audio_file = "output.wav"
        self.audio_path = f"{self.output_dir}/{self.audio_file}"

        # Available voices
        self.voice_names = [
            'af', 'af_bella', 'af_sarah', 'am_adam', 'am_michael',
            'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
            'af_nicole', 'af_sky',
        ]

        # Initialize pygame mixer
        pygame.mixer.init()

    def synthesize(self, text, voice_index=0):
        if voice_index < 0 or voice_index >= len(self.voice_names):
            raise ValueError("Invalid voice index")

        voice_name = self.voice_names[voice_index]
        voicepack_path = f"{self.voices_dir}/{voice_name}.pt"

        # Load voicepack
        voicepack = torch.load(voicepack_path, map_location=self.device)

        # Generate speech
        audio, phonemes = generate(self.model, text, voicepack, lang=voice_name[0])

        # Save audio to file
        output_path = f"{self.output_dir}/{self.audio_file}"
        sf.write(output_path, audio, 24000)

    def audio_exists(self):
        # Wait for audio file to be created
        timeout = time.time() + 10
        pygame.mixer.init()
        while not os.path.exists(self.audio_path):
            if time.time() > timeout:
                raise FileNotFoundError("Audio file not found")
            time.sleep(0.1)

    def play_audio(self):
        self.audio_exists()
        # Play audio
        pygame.mixer.music.load(self.audio_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.stop()
        pygame.mixer.quit()
       

# Example usage
if __name__ == "__main__":

    tts = KokoroTTS()

    text = "Hello, this is a test of the Kokoro TTS system."
    voice_index = 6  # Example: 'bf_isabella'

    tts.synthesize(text, voice_index)
