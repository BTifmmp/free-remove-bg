import os
from huggingface_hub import snapshot_download
from PyQt5.QtCore import pyqtSignal, QThread
from src.models_data import AVAILABLE_MODELS, MODELS_CONFIG
from src.ui.view.console_widget import StdoutRedirector


class ModelDownloadWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def run(self):
        download_model(self.name)
        self.finished.emit(self.name)


def download_model(model_name: str):
    if model_name not in MODELS_CONFIG:
        raise ValueError(f"Model {model_name} is not available. Choose from {list(MODELS_CONFIG.keys())}")

    os.makedirs(os.path.join("models", model_name), exist_ok=True)
    snapshot_download(
        repo_id=MODELS_CONFIG[model_name]['repoId'],
        repo_type=MODELS_CONFIG[model_name]['repoType'],
        local_dir=os.path.join("models", model_name),
        cache_dir=os.path.join("models", ".cache"),
        local_dir_use_symlinks=True
    )


def is_model_downloaded(model_name: str) -> bool:
    "Shallow check if files exist for a model"
    if model_name not in MODELS_CONFIG:
        return False
    
    model_path = os.path.join("models", model_name)
    if not os.path.exists(model_path):
        return False

    for file in MODELS_CONFIG[model_name]['files']:
        if not os.path.isfile(os.path.join(model_path, file)):
            return False
    
    return True
