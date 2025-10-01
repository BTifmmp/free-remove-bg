from PyQt5.QtCore import QObject, pyqtSignal
from .images_model import ImagesModel

class ImagesController(QObject):
    imagesChanged = pyqtSignal()  # emitted whenever the list of images changes

    def __init__(self, images_model: ImagesModel):
        super().__init__()
        self.images_model = images_model

        # Forward model signal to controller signal
        self.images_model.imagesChanged.connect(self.imagesChanged)

    def get_images(self):
        return self.images_model.get_images()

    def add_images(self, paths):
        """Add one or multiple images (only .png, .jpg, .jpeg allowed)"""
        if isinstance(paths, str):
            paths = [paths]
        valid_exts = ('.png', '.jpg', '.jpeg')
        filtered = [p for p in paths if p.lower().endswith(valid_exts)]
        if filtered:
            self.images_model.add_images(filtered)

    def remove_image(self, path):
        self.images_model.remove_image(path)

    def clear_images(self):
        self.images_model.clear_images()