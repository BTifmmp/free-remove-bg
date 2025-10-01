from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class DropMask(QWidget):
    """Visible only during drag, semi-transparent with text."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)

        # Centered label
        self.label = QLabel("Drop images here", self)
        self.label.setStyleSheet("color: white; font-size: 24px;")
        self.label.setAlignment(Qt.AlignCenter)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

        self.hide()  # start hidden

    def resizeEvent(self, event):
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())

class DragDropOverlay(QWidget):
    """Always present, fully transparent, manages drag events and shows/hides mask."""
    def __init__(self, parent, on_drop_callback=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # mask shouldn't block events
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)

        # Child: the drop mask
        self.mask = DropMask(self)
        self.mask.raise_()

        self.on_drop_callback = on_drop_callback  # to forward dropped files

        self.show()
        self.raise_()

    def resizeEvent(self, event):
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        self.mask.resize(self.size())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.mask.show()

    def dragLeaveEvent(self, event):
        self.mask.hide()

    def dropEvent(self, event):
        self.mask.hide()
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        print("Dropped files:", files)
        if self.on_drop_callback:
            self.on_drop_callback(files)
        event.acceptProposedAction()