import pvporcupine
from pvrecorder import PvRecorder

class WakeWordDetector:
    def __init__(self, access_key, sensitivities=None, device_index=-1):
        """
        Initialize the WakeWordDetector class.

        :param access_key: Picovoice access key
        :param keyword_paths: List of paths to .ppn files for keywords
        :param sensitivities: List of sensitivities for keywords
        :param device_index: Index of the microphone device (-1 for default)
        """
        self.access_key = access_key
        self.keyword_paths = ["C:\convo_bot\wake_word\Hey-Gary\Hey-Gary_en_windows_v3_0_0.ppn"]  # Change this to your wake keyword path. 
        self.sensitivities = sensitivities or [0.5] * len(self.keyword_paths)
        self.device_index = device_index
        self.porcupine = None
        self.recorder = None

    def initialize(self):
        """
        Initialize Porcupine and PvRecorder.
        """
        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=self.keyword_paths,
            sensitivities=self.sensitivities
        )
        self.recorder = PvRecorder(device_index=self.device_index, frame_length=self.porcupine.frame_length)

    def listen(self, callback):
        """
        Start listening for the wake word and trigger the callback when detected.

        :param callback: Function to call when wake word is detected
        """
        if not self.porcupine or not self.recorder:
            raise RuntimeError("WakeWordDetector is not initialized. Call 'initialize()' first.")

        try:
            print("Listening for the wake word...")
            self.recorder.start()

            while True:
                pcm = self.recorder.read()
                keyword_index = self.porcupine.process(pcm)

                if keyword_index >= 0:
                    print(f"Wake word detected! Keyword index: {keyword_index}")
                    callback()  # Trigger the callback function
        except KeyboardInterrupt:
            print("\nExiting program...")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """
        Clean up resources used by Porcupine and PvRecorder.
        """
        if self.recorder:
            self.recorder.stop()
            self.recorder.delete()
        if self.porcupine:
            self.porcupine.delete()
