import sys
import os
from collections import deque
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer
import asyncio
from stt.stt import STT
from tts.KokoroTTS import KokoroTTS
from recording.AutoRecorder import AudioRecorder
from wake_word.wake_word_detector import WakeWordDetector
from wake_word.wake_word_thread import WakeWordThread


class Message:
    _cache = deque(maxlen=10)  # Class-level cache for last 10 messages

    def __init__(self, sender, text):
        self.sender = sender
        self.text = text

        Message._cache.append(self)

    @classmethod
    def get_last_messages(cls):
        return list(cls._cache)


class ChatUI(QMainWindow):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(540, 100)  # Start with small height
        self.old_pos = None
        self.voice = voice = 10  # AF_SKY or map your Enum
        self.tts = KokoroTTS()
        self.stt = STT()
        self.auto = AudioRecorder(silence_duration=2.0)
        self.detector = WakeWordDetector(os.getenv("PRORCUPINE_KEY"), sensitivities=[0.7])
        self.wake_thread = WakeWordThread(self.detector)
        self.wake_thread.wake_word_detected.connect(self.on_voice_triggered)


        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Scrollable message area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.addStretch()
        self.scroll_area.setWidget(self.messages_widget)
        main_layout.addWidget(self.scroll_area)

        # Hide messages on startup
        self.scroll_area.setVisible(False)

        # Multi-line chat input
        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText("Ask anything")
        self.chat_input.setFixedHeight(32)
        self.chat_input.setStyleSheet("""
            QTextEdit {
                color: white;
                background-color: #2b2b2b;
                border: none;
                border-radius: 16px;
                padding: 10px 16px;
                font-size: 14px;
            }
        """)
        self.chat_input.textChanged.connect(self.adjust_input_height)
        main_layout.addWidget(self.chat_input)

        # Icon bar
        icon_bar = QHBoxLayout()
        icon_bar.addStretch()

        images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        icon_files = {
            "send": os.path.join(images_dir, "send_white.png"),
            "messages": os.path.join(images_dir, "message_white.png"),
            "messages_green": os.path.join(images_dir, "message_green.png"),
            "mic": os.path.join(images_dir, "mic_white.png"),
            "mic_green": os.path.join(images_dir, "mic_green.png"),
            "bot": os.path.join(images_dir, "boticon.png"),
            "close": os.path.join(images_dir, "close.png"),
        }

        # --- Add send button to the far left ---
        self.send_btn = QPushButton()
        send_pixmap = QPixmap(icon_files["send"]).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.send_btn.setIcon(QIcon(send_pixmap))
        self.send_btn.setIconSize(send_pixmap.size())
        self.send_btn.setFixedSize(36, 36)
        self.send_btn.setStyleSheet("""
                                QPushButton {
                                    background-color: transparent; 
                                    border: none;
                                }
                                QPushButton:hover {
                                    border-radius: 8px;
                                    border: 1.5px solid #444444;
                                }
                            """)
        self.send_btn.clicked.connect(self.send_message)
        icon_bar.insertWidget(0, self.send_btn)  # Insert at the left

        self.messages_btn = None  # Store reference to the messages button
        self.mic_btn = None       # Store reference to the mic button
        self.mic_selected = False # Track mic state

        for key in ["messages", "mic", "close", "bot"]:
            btn = QPushButton()
            pixmap = QPixmap(icon_files[key]).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(pixmap.size())
            btn.setFixedSize(36, 36)
            btn.setStyleSheet("""
                                QPushButton {
                                    background-color: transparent; 
                                    border: none;
                                }
                                QPushButton:hover {
                                    border-radius: 8px;
                                    border: 1.5px solid #444444;
                                }
                            """)
            icon_bar.addWidget(btn)

            if key == "messages":
                btn.clicked.connect(self.toggle_chat_log)
                self.messages_btn = btn  # Save reference
                btn.setIcon(QIcon(QPixmap(icon_files["messages"]).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)))
            elif key == "mic":
                btn.clicked.connect(self.toggle_mic)
                self.mic_btn = btn  # Save reference
                btn.setIcon(QIcon(QPixmap(icon_files["mic"]).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)))
            elif key == "close":
                btn.clicked.connect(self.shutdown)

        main_layout.addLayout(icon_bar)

        self.set_dark_mode()
        self.display_last_messages()

    def set_dark_mode(self):
        self.setStyleSheet("background-color: #1e1e1e; border-radius: 12px;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    def adjust_input_height(self):
        doc_height = self.chat_input.document().size().height()
        self.chat_input.setFixedHeight(max(32, min(100, int(doc_height + 16))))

    def toggle_chat_log(self):
        # Show/hide the scroll area
        is_visible = self.scroll_area.isVisible()
        self.scroll_area.setVisible(not is_visible)
        images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        if is_visible:
            # Hide messages, shrink window
            self.setFixedHeight(100)
            # Set icon to white
            pixmap = QPixmap(os.path.join(images_dir, "message_white.png")).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.messages_btn.setIcon(QIcon(pixmap))
        else:
            # Show messages, restore window size
            self.setFixedHeight(400)
            # Set icon to green
            pixmap = QPixmap(os.path.join(images_dir, "message_green.png")).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.messages_btn.setIcon(QIcon(pixmap))

    def toggle_mic(self):
        # Toggle mic state and icon, print "pressed"
        self.mic_selected = not self.mic_selected
        images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

        if self.mic_selected:
            # Listening ON
            self.chat_input.setPlaceholderText("Listening...")
            self.chat_input.setReadOnly(False)
            pixmap = QPixmap(os.path.join(images_dir, "mic_green.png")).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.mic_btn.setIcon(QIcon(pixmap))

            self.wake_thread.start()
        else:
            # Listening OFF
            self.chat_input.setPlaceholderText("Ask anything")
            self.chat_input.setReadOnly(False)
            pixmap = QPixmap(os.path.join(images_dir, "mic_white.png")).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.mic_btn.setIcon(QIcon(pixmap))

            self.wake_thread.stop()

    def display_last_messages(self):
        # Clear current messages
        for i in reversed(range(self.messages_layout.count() - 1)):
            widget = self.messages_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # Add last 10 messages
        for msg in Message.get_last_messages():
            label = QLabel(f"<b>{msg.sender}:</b> {msg.text}")
            label.setStyleSheet("color: #f5f5f5; padding: 2px;")
            label.setWordWrap(True)
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, label)

    def add_message(self, sender, text):
        Message(sender, text)
        self.display_last_messages()
        # Scroll to bottom
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def send_message(self):
        text = self.chat_input.toPlainText().strip()
        if text:
            self.add_message("User", text)
            self.chat_input.clear()
            # Run the async call safely in the Qt main thread
            QTimer.singleShot(0, lambda: asyncio.ensure_future(self.get_agent_response(text)))

    async def get_agent_response(self, text):
        result = await self.agent.run(text)
        response_text = result.data
        self.add_message("AI", response_text)

         # Run synthesize and play_audio in background thread to avoid blocking the UI
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.tts.synthesize, response_text, self.voice)
        await loop.run_in_executor(None, self.tts.play_audio)
        

    def shutdown(self):
        self.close()

    def on_voice_triggered(self):
        QTimer.singleShot(0, lambda: asyncio.ensure_future(self.handle_voice_interaction()))

    async def handle_voice_interaction(self):
        loop = asyncio.get_event_loop()

        # Immediately update UI to show it's listening
        self.chat_input.setPlaceholderText("Listening...")
        self.chat_input.setReadOnly(True)

        # Prompt the user
        await loop.run_in_executor(None, self.tts.synthesize, "How can I help you?", self.voice)
        await loop.run_in_executor(None, self.tts.play_audio)

        # Now do the recording
        recording = await loop.run_in_executor(None, self.auto.record)
        if not recording:
            await loop.run_in_executor(None, self.tts.synthesize, "Sorry, I didn't get that.", self.voice)
            await loop.run_in_executor(None, self.tts.play_audio)
            self.chat_input.setPlaceholderText("Ask anything")
            self.chat_input.setReadOnly(False)
            return

        # Transcribe
        speech = await loop.run_in_executor(None, self.stt.transcribe, "C:/convo_bot/recording/audio_out/output.wav")
        self.add_message("User", speech)

        # Respond
        await self.get_agent_response(speech)

        # Reset UI
        self.chat_input.setPlaceholderText("Ask anything")
        self.chat_input.setReadOnly(False)

    async def get_response(self, user_input):
        response = await self.agent.run(user_input)  # Use 'await' directly
        return response.data
