import logging
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, QObject
import sys


class ConsoleWidget(QPlainTextEdit):
    def __init__(self, parent=None, max_lines=1000):
        super().__init__(parent)
        self.max_lines = max_lines

        font = QFont("Monospace")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(10)
        self.setFont(font)

        self.setStyleSheet(style)

        self.setReadOnly(True)
        self.setMinimumHeight(50)

    def append_message(self, text: str):
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text + "\n")
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

        # Keep max lines
        while self.blockCount() > self.max_lines:
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.BlockUnderCursor)
            cursor.removeSelectedText()

class LogCapture(logging.Handler, QObject):
    """Forward Python logging records into QtLogger."""
    captured = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        QObject.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        self.captured.emit(msg)

class SysOutputCapture(QObject):
    """Capture sys.stdout and sys.stderr and emit as signal. 
    Used mainly to track HF download progress
    """
    captured = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.terminal = sys.__stdout__  # keep a reference to the real console

    def write(self, text):
        self.terminal.write(text)
        if text.strip():  # avoid extra newlines
            self.captured.emit(text)

    def flush(self):
        self.terminal.flush()


style = """
    QPlainTextEdit {
        background-color: #202020;
        color: #eaeaea;
    }
    QScrollBar:vertical {
        border: none;
        background: #2e2e2e;
        width: 8px;
        margin: 0px 0px 0px 0px;
        border-radius: 4px;
    }

    QScrollBar::handle:vertical {
        background: #888;
        min-height: 20px;
        border-radius: 4px;
    }

    QScrollBar::handle:vertical:hover {
        background: #555;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
        subcontrol-origin: margin;
    }

    QScrollBar:horizontal {
        border: none;
        background: #2e2e2e;
        height: 8px;
        margin: 0px 0px 0px 0px;
        border-radius: 4px;
    }

    QScrollBar::handle:horizontal {
        background: #888;
        min-width: 20px;
        border-radius: 4px;
    }

    QScrollBar::handle:horizontal:hover {
        background: #555;
    }

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
        subcontrol-origin: margin;
    }
"""