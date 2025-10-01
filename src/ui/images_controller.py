import shutil
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from .images_model import ImagesModel
import sys
import os

from src.scripts.remove_bg import InferenceManager
from src.scripts.model_downloader import ModelDownloader
from .qt_logger import QtLogger
import os

class ImagesController(QObject):
    imagesChanged = pyqtSignal()  # emitted whenever the list of images changes
    backgroundRemoved = pyqtSignal(str)  # emitted when background removal is done

    def __init__(self, images_model: ImagesModel):
        super().__init__()
        self.images_model = images_model
        self._model_name = None

        # Forward model signal to controller signal
        self.images_model.imagesChanged.connect(self.imagesChanged)

    def get_images(self):
        return self.images_model.get_images()

    def add_images(self, paths, log=True):
        """Add one or multiple images (only .png, .jpg, .jpeg allowed)"""
        if not paths:
            return
        
        if isinstance(paths, str):
            paths = [paths]

        valid_exts = ('.png', '.jpg', '.jpeg')

        # Log warnings for invalid files
        if log:
            for p in paths:
                if not os.path.isfile(p):
                    QtLogger.instance().log(f"Warning: {p} is not a valid file path")
                if not p.lower().endswith(valid_exts):
                    QtLogger.instance().log(f"Warning: {p} is not a supported image format")
                QtLogger.instance().log(f"Adding image: {p}")

        # Filter only valid image files
        filtered = [p for p in paths if p.lower().endswith(valid_exts)]
        if filtered:
            self.images_model.add_images(filtered)

    def clear_images(self, log=True):
        self.clear_temp()
        self.images_model.clear_images()
        if log:
            QtLogger.instance().log("Cleared all images")

    def remove_bg_from_all(self):
        if not ModelDownloader().verify_download(self._model_name):
            res = self.ask_download()
            if not res:
                return
            try:
                QtLogger.instance().log(f"Downloading model: {self._model_name}")
                ModelDownloader().download_model(self._model_name)
            except Exception as e:
                QtLogger.instance().log(f"Error downloading model {self._model_name}: {e}")
                return
            
        try:
            QtLogger.instance().log(f"Loading model: {self._model_name}")
            InferenceManager().load_model(self._model_name)
        except Exception as e:
            QtLogger.instance().log(f"Error loading model {self._model_name}: {e}")
            return

        remove_bg = InferenceManager().remove_background
        temp_dir = os.path.join("temp")
        self.worker = RemoveBGWorker(
            image_paths=self.get_images(),
            output_dir=temp_dir,
            remove_bg_func=remove_bg
        )
        self.worker.progress.connect(lambda msg: QtLogger.instance().log(msg))
        self.worker.finished_image.connect(lambda path: self.backgroundRemoved.emit(path))
        self.worker.done.connect(lambda: QtLogger.instance().log("All images processed"))
        self.worker.start()  # runs in background
    
    def clear_temp(self):
        temp_dir = os.path.join("temp")
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, f)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting temp file {file_path}: {e}", file=sys.stderr) 
    
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
                    QtLogger.instance().log("Image saved successfully to " + dest_path)
                except Exception as e:
                    QtLogger.instance().log(f"Error occurred while saving image to {dest_path}: {e}")
            return

        folder = QFileDialog.getExistingDirectory(widget, "Saving Multiple Images")
        if folder:
            for image_path in self.images_model.get_images():
                # Keep original extension
                dest_path = os.path.join(folder, f"{os.path.basename(image_path)}.png")
                try:
                    shutil.copy(image_path, dest_path)
                    QtLogger.instance().log("Images saved successfully to " + dest_path)
                    raise ValueError("x must be non-negative")
                except Exception as e:
                    QtLogger.instance().log(f"Error occurred while saving images to {dest_path}: {e}")
    
    def select_images(self, widget):
        paths, _ = QFileDialog.getOpenFileNames(widget, "Select Images", "", "Images (*.png *.jpg *.jpeg)")
        if paths:
            self.add_images(paths)

    def setModelName(self, model_name: str):
        self._model_name = model_name

    def ask_download(self, parent=None):
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirm Download")
        msg_box.setText(f"Do you want to download the {'RMGB1.4 (~200MB)' if self._model_name == 'rmbg14' else 'RMGB2.0 (~900MB)'}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet("""
            background-color: #353535;
            color: #eaeaea;
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #222222;
                border-radius: 10px;
                padding: 8px 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
        """)
        msg_box.setDefaultButton(QMessageBox.Yes)

        ret = msg_box.exec_()  # returns QMessageBox.Yes or QMessageBox.No
        return ret == QMessageBox.Yes

class RemoveBGWorker(QThread):
    progress = pyqtSignal(str)  # status messages
    finished_image = pyqtSignal(str)  # path of processed image
    done = pyqtSignal()  # all images finished

    def __init__(self, image_paths, output_dir, remove_bg_func):
        super().__init__()
        self.image_paths = image_paths
        self.output_dir = os.path.abspath(output_dir)
        self.remove_bg_func = remove_bg_func

    def run(self):
        os.makedirs(self.output_dir, exist_ok=True)
        for i, img_path in enumerate(self.image_paths):
            self.progress.emit(f"Processing {os.path.basename(img_path)} ({i+1}/{len(self.image_paths)})")
            # run your actual remove_bg function
            image = self.remove_bg_func(img_path)  # must return a PIL.Image
            base_name = os.path.basename(img_path)
            name, ext = os.path.splitext(base_name)
            output_path = os.path.join(self.output_dir, f"{name}_nobg.png")
            image.save(output_path, "PNG")
            self.finished_image.emit(output_path)
        self.done.emit()