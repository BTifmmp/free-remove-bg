from PyQt5.QtCore import QObject, pyqtSignal
from src.models_data import AVAILABLE_MODELS
from src.ui.model.selected_model import SelectedModel

class ModelSelectController(QObject):
    def __init__(self, model_select_model: SelectedModel):
        self.model_select_model = model_select_model

    def get_available_models(self):
        return self.model_select_model.get_available_models()

    def get_selected_model(self):
        return self.model_select_model.get_selected_model()

    def set_selected_model(self, model_name):
        self.model_select_model.set_selected_model(model_name)