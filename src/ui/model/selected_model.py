from PyQt5.QtCore import QObject, pyqtSignal

class SelectedModel(QObject):
    modelChanged = pyqtSignal(str)

    def __init__(self, initial_model='rmbg14'):
        super().__init__()
        self.model = initial_model

    def set_model(self, model):
        self.model = model
        self.modelChanged.emit(model)

    def get_model(self):
        return self.model