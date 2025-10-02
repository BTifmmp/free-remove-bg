import logging
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QFont
import sys


class ConsoleWidget(QPlainTextEdit):
    def __init__(self, parent=None, max_lines=1000):
        super().__init__(parent)
        self.max_lines = max_lines
        self.last_line_overwrite = False

        font = QFont("Monospace")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(10)
        self.setFont(font)

        self.setStyleSheet(style)

        self.setReadOnly(True)
        self.setMinimumHeight(50)

    def append_message(self, text: str):
        cursor = self.textCursor()
        overwrite = False
        if "\r " in text:
            text = text.replace("\r ", "")
            overwrite = True
        if overwrite and self.last_line_overwrite:
            cursor.movePosition(cursor.End)
            cursor.select(cursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()
        else:
            self.last_line_overwrite = False

        cursor.movePosition(cursor.End)
        cursor.insertText(text + "\n")
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

        # Keep max lines
        while self.blockCount() > self.max_lines:
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.BlockUnderCursor)
            cursor.removeSelectedText()

        self.last_line_overwrite = overwrite

class QtLogHandler(logging.Handler):
    """Forward Python logging records into QtLogger."""
    def __init__(self, widget: ConsoleWidget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.append_message(msg)

class StdoutRedirector:
    """Singleton to capture stdout/stderr and forward to a console widget."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.console_widget = None
        self.terminal = sys.__stderr__ 
        self._initialized = True

    def set_console(self, console_widget):
        """Attach/replace the console widget where logs will be written."""
        self.console_widget = console_widget

    def write(self, text):
        self.terminal.write(text)  # still print to real console
        if self.console_widget and text.strip():  # forward to Qt console
            self.console_widget.append_message(text)

    def flush(self):
        self.terminal.flush()

    def enabled(self, enable: bool):
        if enable:
            sys.stderr = self
        else:
            sys.stderr = self.terminal


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