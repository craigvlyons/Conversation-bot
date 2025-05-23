import sys
import os
from collections import deque
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt


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
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(540, 320)
        self.old_pos = None

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
            "messages": os.path.join(images_dir, "message_white.png"),
            "mic": os.path.join(images_dir, "mic_white.png"),
            "bot": os.path.join(images_dir, "boticon.png"),
        }

        for key in ["messages", "mic", "bot"]:
            btn = QPushButton()
            pixmap = QPixmap(icon_files[key]).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(pixmap.size())
            btn.setFixedSize(36, 36)
            btn.setStyleSheet("background-color: transparent; border: none;")
            icon_bar.addWidget(btn)

            if key == "messages":
                btn.clicked.connect(self.toggle_chat_log)

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
        is_visable = self.scroll_area.isVisible()
        self.scroll_area.setVisible(not is_visable)
        if is_visable:
            # Hide messages, shrink window
            self.setFixedHeight(100)
        else:
            # Show messages, restore window size
            self.setFixedHeight(400)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatUI()
    # Example messages for demo
    window.add_message("User", "Hello, AI!")
    window.add_message("AI", "Hello! How can I help you today?")
    window.show()
    sys.exit(app.exec())
