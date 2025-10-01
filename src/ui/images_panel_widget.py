from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImagesPanelWidget(QWidget):
    def __init__(self, images_controller, empty_text="No images selected"):
        super().__init__()
        self.images_controller = images_controller
        self.empty_text = empty_text

        self.setStyleSheet(images_panel_style)
        self.empty_label = QLabel(self.empty_text)
        self.empty_label.setStyleSheet(empty_label_style)
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setWordWrap(True)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(self.empty_label)

        self.update_images()

    def update_images(self):
        pass

images_panel_style = """
    QWidget {
        padding: 30px;
    }
    """

empty_label_style = """
    QLabel {
        color: #aaaaaa;
        font-size: 18px;
    }
"""