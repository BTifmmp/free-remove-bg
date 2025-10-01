from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QGridLayout, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QDrag
from PyQt5.QtCore import Qt, QTimer, QUrl, QMimeData
from .images_controller import ImagesController

class ImagesPanelWidget(QWidget):
    def __init__(self, images_controller: ImagesController, empty_text="No images selected"):
        super().__init__()
        self.images_controller = images_controller
        self.empty_text = empty_text

        self.images_controller.imagesChanged.connect(self.update_images)

        self.setStyleSheet(images_panel_style)

        # Empty label
        self.empty_label = QLabel(self.empty_text)
        self.empty_label.setStyleSheet(empty_label_style)
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setWordWrap(True)

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout()
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(15)
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setStyleSheet(scroll_area)

        self.layout.addWidget(self.empty_label)
        self.layout.addWidget(self.scroll_area)

        self.update_images()

        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self.update_images)

    def resizeEvent(self, a0):
        self._resize_timer.start(20)
        return super().resizeEvent(a0)

    def update_images(self):
        # Clear existing items
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        images = self.images_controller.get_images()

        if not images:
            self.empty_label.show()
            self.scroll_area.hide()
            return
        else:
            self.empty_label.hide()
            self.scroll_area.show()

        # Add images in 3-column grid

        panel_width = self.scroll_area.viewport().width()
        panel_height = self.scroll_area.viewport().height()

        num_of_img = len(images)
        max_width = max(0, panel_width//3-20)
        columns = 3

        if num_of_img <= 3:
            max_width = max(min(max(0, panel_width//num_of_img-20), panel_height-50), 100)
            columns = max(1, num_of_img)

        if panel_width < 450 and num_of_img >= 2:
            max_width = max(min(max(0, panel_width//2-20), panel_height-50), 100)
            columns = 2

        if panel_width < 300 and num_of_img >= 2:
            max_width = max(min(max(0, panel_width//1-20), panel_height-50), 100)
            columns = 1

        for index, path in enumerate(images):
            row = index // columns
            col = index % columns

            container = QWidget()
            container.setMaximumWidth(max_width)
            container_layout = QVBoxLayout()
            container_layout.setContentsMargins(5, 5, 5, 5)
            container_layout.setSpacing(5)
            container.setLayout(container_layout)

            # Image
            image_container = QWidget()
            image_container.setMaximumSize(max_width, max_width)
            image_container.setLayout(QVBoxLayout())
            image_container.layout().setContentsMargins(1, 1, 1, 1)
            image_container.layout().setAlignment(Qt.AlignCenter)
            image_label = DraggableImage(path, max_width)
            image_container.layout().addWidget(image_label)
            container_layout.addWidget(image_container)
            container_layout.addStretch()

            # File name
            filename = path.split('/')[-1] if len(path.split('/')[-1]) < 50 else path.split('/')[-1][:23] + '...' + path.split('/')[-1][-23:]
            filename = '\u200B'.join(filename)
            name_label = QLabel(filename)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setWordWrap(True)
            name_label.setStyleSheet("font-size: 12px; color: #cccccc;")
            container_layout.addWidget(name_label)

            container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            self.scroll_layout.addWidget(container, row, col)

        # Update scroll area size
        self.scroll_content.setMinimumHeight(self.scroll_layout.sizeHint().height())
        self.scroll_area.setWidget(self.scroll_content)


class DraggableImage(QLabel):
    def __init__(self, image_path, max_width, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        pixmap = QPixmap(image_path).scaled(max_width, max_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        if pixmap.isNull():
            pixmap = QPixmap(max_width, max_width)
            pixmap.fill(Qt.darkGray)
        
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(pixmap.size())
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()

            # Important: set URLs for file drag (desktop/file system)
            mime_data.setUrls([QUrl.fromLocalFile(self.image_path)])
            drag.setMimeData(mime_data)

            # Optional: show pixmap while dragging
            drag.setPixmap(self.pixmap())
            drag.setHotSpot(event.pos())

            drag.exec_(Qt.CopyAction)


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

scroll_area = """
QScrollBar:vertical {
    border: none;
    background: #2e2e2e;
    width: 8px;
    margin: 0px 0px 0px 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #888;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #555;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    subcontrol-origin: margin;
}

QScrollBar:horizontal {
    border: none;
    background: #2e2e2e;
    height: 8px;
    margin: 0px 0px 0px 0px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #888;
    min-width: 20px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background: #555;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
    subcontrol-origin: margin;
}
"""