import os
from huggingface_hub import snapshot_download

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
    
    def clear_model(self, model_name: str):
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model {model_name} is not available. Choose from {self.AVAILABLE_MODELS}")

        model_path = os.path.join("models", model_name)
        if os.path.exists(model_path):
            for root, dirs, files in os.walk(model_path, top_down=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(model_path)
    
    def _download_model14(self):
        os.makedirs("models/rmbg14", exist_ok=True)

        snapshot_download(
            repo_id="regitBT/rmbg14fork",
            cache_dir="models/rmbg14",
            local_dir="models/rmbg14",
            local_dir_use_symlinks=False,
            resume_download=True,
            repo_type="model"
        )

    def _download_model20(self):
        os.makedirs("models/rmbg20", exist_ok=True)

        snapshot_download(
            repo_id="regitBT/rmbg20fork",
            cache_dir="models/rmbg20",
            local_dir="models/rmbg20",
            local_dir_use_symlinks=False,
            resume_download=True,
            repo_type="model"
        )
    
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
