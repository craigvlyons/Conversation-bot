import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

class AudioRecorder:
    def __init__(self, samplerate=16000, silence_threshold=100, silence_duration=1.0, max_duration=30):
        """
        Initialize the AudioRecorder class.
        
        :param samplerate: Sampling rate for audio recording
        :param silence_threshold: Amplitude below which audio is considered silent
        :param silence_duration: Duration of silence to stop recording (in seconds)
        :param max_duration: Maximum recording duration to prevent endless recording (in seconds)
        """
        self.samplerate = samplerate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_duration = max_duration
        self.audio_file = "C:/convo_bot/recording/audio_out/output.wav"

    def is_silent(self, data):
        """
        Check if the audio data is silent.
        
        :param data: Audio data chunk
        :return: True if silent, otherwise False
        """
        return np.abs(data).mean() < self.silence_threshold

    def record(self) -> bool:
        """
        Record audio until a long pause is detected or the maximum duration is reached.
        
        :return: Recorded audio data
        """
        print("Recording audio... Speak now!")
        stream = sd.InputStream(samplerate=self.samplerate, channels=1, dtype='int16')
        stream.start()

        recording = []
        silent_chunks = 0
        chunk_size = int(self.samplerate / 10)  # 100ms chunks

        try:
            while len(recording) < self.samplerate * self.max_duration:
                # Read a chunk of audio data
                chunk = stream.read(chunk_size)[0].flatten()
                recording.append(chunk)

                # Check for silence
                if self.is_silent(chunk):
                    silent_chunks += 1
                    if silent_chunks >= int(self.silence_duration * 10):  # 10 chunks per second
                        # print("Detected silence. Stopping recording.")
                        break
                else:
                    silent_chunks = 0
        finally:
            stream.stop()

        # Concatenate all chunks into a single array
        audio_data = np.concatenate(recording)
        # check if the audio is silent if its duration is less than silence_duration + 1 then return None
        if len(audio_data) < self.samplerate * (self.silence_duration + 1):
            # print("Audio too short. Please try again.")
            return False
        # print(f"Recording complete. Duration: {len(audio_data) / self.samplerate:.2f} seconds")
        write(self.audio_file, self.samplerate, audio_data)
        return True
        

    def save(self, audio_data):
        """
        Save audio data to a WAV file.
        
        :param audio_data: Recorded audio data
        """
        write(self.audio_file, self.samplerate, audio_data)
        # print(f"Audio saved to {self.audio_file}")
