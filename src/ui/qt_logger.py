from PyQt5.QtCore import QObject, pyqtSignal, Qt

class QtLogger(QObject):
    message = pyqtSignal(str)  # signals text to UI

    _instance = None

    def __init__(self):
        super().__init__()
        if QtLogger._instance is not None:
            raise RuntimeError("Use QtLogger.instance()")
        QtLogger._instance = self

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = QtLogger()
        return cls._instance

    def log(self, text: str):
        """Call from any thread (OK if called from main thread)."""
        # if you want, you can add timestamp/level here
        self.message.emit(text)
        