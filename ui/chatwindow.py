import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton
)
from PyQt6.QtGui import QPixmap, QPalette, QColor, QIcon
from PyQt6.QtCore import Qt


class ChatUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(540, 120)
        self.set_dark_mode()
        self.old_pos = None

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Message log (toggle visibility)
        self.chat_log = QLabel("Previous messages here...")
        self.chat_log.setStyleSheet("color: white; padding: 5px;")
        self.chat_log.setWordWrap(True)
        self.chat_log.setVisible(False)
        main_layout.addWidget(self.chat_log)

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
        self.chat_log.setVisible(not self.chat_log.isVisible())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatUI()
    window.show()
    sys.exit(app.exec())
