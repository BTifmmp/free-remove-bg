from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QFont
from .qt_logger import QtLogger

class InfoLogsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.editor = QTextEdit(self)
        self.editor.setReadOnly(True)
        self.editor.setMinimumHeight(50)

        font = QFont("Monospace")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(10)
        self.editor.setFont(font)

        # Optional: dark theme styling
        self.editor.setStyleSheet(style)

        layout.addWidget(self.editor)

        # connect the global logger
        QtLogger.instance().message.connect(self.append_message)

    def append_message(self, text):
    # Append new text
        self.editor.append(text)

        # Get all lines
        lines = self.editor.toPlainText().splitlines()

        # If more than 1000 lines, remove oldest 200
        if len(lines) > 1000:
            lines = lines[200:]  # remove first 200 lines
            # Block signals to avoid recursion (optional)
            self.editor.blockSignals(True)
            self.editor.setPlainText("\n".join(lines))
            self.editor.blockSignals(False)
            # Move cursor to the end
            cursor = self.editor.textCursor()
            cursor.movePosition(cursor.End)
            self.editor.setTextCursor(cursor)


style = """
    QTextEdit {
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