from PyQt5.QtCore import QObject, pyqtSignal

class ImagesModel(QObject):
    imagesChanged = pyqtSignal()  # signal emitted when images list changes

    def __init__(self):
        super().__init__()
        self._images = []

    def get_images(self):
        return list(self._images)

    def add_images(self, paths):
        """Add images, ignore duplicates"""
        for path in paths:
            if path not in self._images:
                self._images.append(path)
        self.imagesChanged.emit()

    def remove_image(self, path):
        if path in self._images:
            self._images.remove(path)
            self.imagesChanged.emit()

    def clear_images(self):
        if self._images:
            self._images.clear()
            self.imagesChanged.emit()