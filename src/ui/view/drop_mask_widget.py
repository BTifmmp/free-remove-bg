from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class DropMask(QWidget):
    """A mask overlay that fills the whole parent window"""
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setGeometry(0, 0, parent.width(), parent.height())
        
        # Centered label
        label = QLabel("Drop images here", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 24px;")

        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.setStretchFactor(label, 1)
        layout.setContentsMargins(0, 0, 0, 0)

        self.hide()

    def showEvent(self, a0):
        self.resize(self.parent().size())
        return super().showEvent(a0)