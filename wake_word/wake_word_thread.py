from PyQt6.QtCore import QThread, pyqtSignal

class WakeWordThread(QThread):
    wake_word_detected = pyqtSignal()

    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self._running = True

    def run(self):
        try:
            self.detector.initialize()
            self.detector.recorder.start()

            while self._running:
                pcm = self.detector.recorder.read()
                keyword_index = self.detector.porcupine.process(pcm)
                if keyword_index >= 0:
                    self.wake_word_detected.emit()
        finally:
            self.detector.cleanup()

    def stop(self):
        self._running = False
        self.quit()
        self.wait()
