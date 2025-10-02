import logging
import shutil, os
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from ..model.images_model import ImagesModel

class ImagesController(QObject):
    imagesChanged = pyqtSignal()  # emitted whenever the list of images changes

    def __init__(self, images_model: ImagesModel):
        super().__init__()
        self.images_model = images_model
        self._model_name = None

        # Forward model signal to controller signal
        self.images_model.imagesChanged.connect(self.imagesChanged)

    def get_images(self):
        return self.images_model.get_images()

    def add_images(self, paths):
        """Add one or multiple images (only .png, .jpg, .jpeg allowed)"""
        if not paths:
            return
        
        if isinstance(paths, str):
            paths = [paths]

        valid_exts = ('.png', '.jpg', '.jpeg')

        # Log warnings for invalid files
        for p in paths:
            if not os.path.isfile(p):
                logging.warning(f"Warning: {p} is not a valid file path")
            if not p.lower().endswith(valid_exts):
                logging.warning(f"Warning: {p} is not a supported image format")
            logging.info(f"Adding image: {p}")

        # Filter only valid image files
        filtered = [p for p in paths if p.lower().endswith(valid_exts)]
        if filtered:
            self.images_model.add_images(filtered)

    def clear_images(self):
        self.images_model.clear_images()
    
    def save_images(self, widget):
        if not self.images_model.get_images():
            return
        
        if len(self.images_model.get_images()) == 1:
            # Save single image
            image_path = self.images_model.get_images()[0]
            dest_path, _ = QFileDialog.getSaveFileName(widget, "Save Image", f"{os.path.basename(image_path)}", "Images (*.png)")
            if dest_path:
                try:
                    shutil.copy(image_path, dest_path)
                    logging.info("Image saved successfully to " + dest_path)
                except Exception as e:
                    logging.error(f"Error occurred while saving image to {dest_path}: {e}")
            return

        folder = QFileDialog.getExistingDirectory(widget, "Saving Multiple Images")
        if folder:
            for image_path in self.images_model.get_images():
                # Keep original extension
                dest_path = os.path.join(folder, f"{os.path.basename(image_path)}.png")
                try:
                    shutil.copy(image_path, dest_path)
                    logging.info("Images saved successfully to " + dest_path)
                except Exception as e:
                    logging.error(f"Error occurred while saving images to {dest_path}: {e}")

    def select_images(self, widget):
        paths, _ = QFileDialog.getOpenFileNames(widget, "Select Images", "", "Images (*.png *.jpg *.jpeg)")
        if paths:
            self.add_images(paths)
