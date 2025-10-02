import os, tempfile
from PIL import Image

import os, tempfile
from PIL import Image

class TempImgsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.temp_dir = tempfile.TemporaryDirectory()
        return cls._instance

    def save_temp_img(self, image: Image.Image, filename: str) -> str:
        temp_path = os.path.join(self.temp_dir.name, filename)
        image.save(temp_path, 'PNG')
        return temp_path
    
    def clear_temp(self):
        self.temp_dir.cleanup()
        self.temp_dir = tempfile.TemporaryDirectory()