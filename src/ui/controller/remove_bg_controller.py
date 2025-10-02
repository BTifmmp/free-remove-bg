import logging
from PyQt5.QtWidgets import QMessageBox
from ..model.images_model import ImagesModel

from src.utils.remove_bg_manager import RemoveBgManager, RemoveBGWorker
from src.utils.download_manager import ModelDownloadWorker, is_model_downloaded
from src.utils.temp_imgs_manager import TempImgsManager
from src.ui.model.selected_model import SelectedModel

class RemoveBgController:
    def __init__(self, source_images_model: ImagesModel, res_images_model: ImagesModel, selected_model: SelectedModel):
        self.source_images_model = source_images_model
        self.res_images_model = res_images_model
        self.selected_model = selected_model

    def remove_backgrounds(self):
        # Clear previous results
        self.res_images_model.clear_images()

        # Check if model is downloaded
        if not is_model_downloaded(self.selected_model.get_model()):
            self._download_and_run(self.selected_model.get_model())
        else:
            self._start_removal(self.selected_model.get_model())

    def _download_and_run(self, model_name):
        # Ask user for confirmation
        res = self._ask_download()
        if res:
            try:
                logging.info(f"Downloading model {model_name}.")
                self.download_worker = ModelDownloadWorker(model_name)
                self.download_worker.finished.connect(lambda: self._start_removal(model_name))
                self.download_worker.start()
            except Exception as e:
                logging.error(f"Error downloading model: {e}")
        
    def _start_removal(self, model_name):
        # Check if there are images to process
        if not self.source_images_model.get_images():
            logging.info("No images to process.")
            return

        # Load model
        try:
            logging.info(f"Loading model {model_name}.")
            inference_manager = RemoveBgManager()
            inference_manager.load_model(model_name)
        except Exception as e:
            logging.error(f"Error loading model {model_name}: {e}")
            return
        
        # Start background removal in a separate thread
        try:
            logging.info("Starting background removal.")
            self.worker = RemoveBGWorker(
                self.source_images_model.get_images(),
                inference_manager.remove_background
            )

            self.worker.start()
            self.worker.finished_image.connect(self._on_image_processed)
            self.worker.done.connect(lambda: logging.info("Background removal completed."))
        except Exception as e:
            logging.error(f"Error removing background: {e}")
            return
    
    def _ask_download(self, parent=None):
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirm Download")
        msg_box.setText(f"Do you want to download the {'RMGB1.4 (~200MB)' if self.selected_model.get_model() == 'rmbg14' else 'RMGB2.0 (~900MB)'}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet(msg_box_style)
        msg_box.setDefaultButton(QMessageBox.Yes)

        ret = msg_box.exec_()  # returns QMessageBox.Yes or QMessageBox.No
        return ret == QMessageBox.Yes
    
    def _on_image_processed(self, filename, img, count):
        path = TempImgsManager().save_temp_img(img, f"{filename}_no_bg.png")
        self.res_images_model.add_images([path])
        logging.info(f"Processed image {count+1}/{len(self.source_images_model.get_images())}")

msg_box_style = """
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
"""