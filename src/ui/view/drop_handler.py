from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QObject, pyqtSignal

class DropHandler(QObject):
    filesDropped = pyqtSignal(list)  # emits list of file paths
    dropEntered = pyqtSignal()
    dropExited = pyqtSignal()

    def __init__(self, widget):
        super().__init__()
        self.widget = widget

        self.widget.dragEnterEvent = self.dragEnterEvent
        self.widget.dragLeaveEvent = self.dragLeaveEvent
        self.widget.dropEvent = self.dropEvent

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.dropEntered.emit()

    def dragLeaveEvent(self, event):
        self.dropExited.emit()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.dropExited.emit()
        self.filesDropped.emit(files)
        event.acceptProposedAction()
   