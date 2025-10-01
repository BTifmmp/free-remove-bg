from PyQt5.QtCore import QObject, pyqtSignal
from .qt_logger import QtLogger

from src.scripts.model_downloader import ModelDownloader

class ModelTypeController(QObject):
    modelChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_model = None

    def set_model(self, model_name: str):
        QtLogger.instance().message.emit(f"Model set to {model_name}")
        self.current_model = model_name
        self.modelChanged.emit(model_name)
        
    def get_model(self) -> str:
        return self.current_model
    
    def clear_models(self):
        if self.current_model:
            ModelDownloader().clear_models_folder(self.current_model)
            QtLogger.instance().message.emit(f"Cleared model files for {self.current_model}")
        else:
            QtLogger.instance().message.emit("No model selected to clear.")
