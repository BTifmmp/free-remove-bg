import os
from huggingface_hub import snapshot_download, hf_hub_download

import sys
from PyQt5.QtCore import QObject, pyqtSignal, QThread

from src.ui.qt_logger import QtLogger
import logging

class ModelDownloader:
    AVAILABLE_MODELS = [
        "rmbg14",
        "rmbg20"
    ]
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelDownloader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # avoid re-init
            self._initialized = True

    def download_model(self, model_name: str):
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model {model_name} is not available. Choose from {self.AVAILABLE_MODELS}")

        if model_name == "rmbg14":
            self._download_model14()
        elif model_name == "rmbg20":
            self._download_model20()
    
    def clear_models_folder(self, model_name: str):
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model {model_name} is not available. Choose from {self.AVAILABLE_MODELS}")

        model_path = os.path.join("models", model_name)
        if os.path.exists(model_path):
            for root, dirs, files in os.walk(model_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(model_path)
    
    def _download_model14(self):
        os.makedirs("models/rmbg14", exist_ok=True)

        worker = HFDownloadWorker("regitBT/rmbg14fork", "models/rmbg14")
        worker.start()
        QtLogger.instance().log("Download started...")
        worker.finished.connect(lambda path: QtLogger.instance().log(f"Download finished: {path}"))

    def _download_model20(self):
        os.makedirs("models/rmbg20", exist_ok=True)

        worker = HFDownloadWorker("regitBT/rmbg20fork", "models/rmbg20")
        worker.start()
        QtLogger.instance().log("Download started...")
        worker.finished.connect(lambda path: QtLogger.instance().log(f"Download finished: {path}"))
    
    def verify_download(self, model_name: str) -> bool:
        model_path = os.path.join("models", model_name)
        if not os.path.exists(model_path):
            return False
        
        # Check for presence of essential files
        essential_files = {
            "rmbg14": ["config.json", "briarmbg.py", "model.safetensors", "MyConfig.py"],
            "rmbg20": ["config.json", "BiRefNet_config.py", "model.safetensors", "birefnet.py"]
        }

        for file in essential_files.get(model_name, []):
            if not os.path.isfile(os.path.join(model_path, file)):
                return False
        
        return True


class HFDownloadWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, repo_id: str, local_dir: str):
        super().__init__()
        self.repo_id = repo_id
        self.local_dir = local_dir

    def run(self):
        qt_logger = QtLogger.instance()

        # Redirect stdout/stderr temporarily
        class StreamToQt(QObject):
            message = pyqtSignal(str)
            def write(self, text):
                text = text.strip()
                if text:
                    self.message.emit(text)
            def flush(self):
                pass

        stream = StreamToQt()
        stream.message.connect(qt_logger.log)

        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = stream, stream

        try:
            snapshot_download(
                repo_id=self.repo_id,
                local_dir=self.local_dir,
                local_dir_use_symlinks=False,
                resume_download=True,
                repo_type="model"
            )
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

        self.finished.emit(self.local_dir)