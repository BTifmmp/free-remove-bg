from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QHBoxLayout, QWidget, QVBoxLayout, QSplitter
)
from PyQt5.QtCore import Qt
from .button_widget import ButtonWidget
from .images_panel_widget import ImagesPanelWidget
from .drag_drop_widget import DragDropOverlay


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        central = QWidget()
        self.setCentralWidget(central)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        central.setLayout(self.main_layout)

        self.setWindowTitle("Free Remove BG")
        
        # Get screen geometry
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        # Set window size to half the screen
        width = screen_width // 2
        height = screen_height // 2
        self.resize(width, height)

        # Center the window
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.move(x, y)

        self.setStyleSheet(q_window_style)

        self.overlay = DragDropOverlay(self)

        self.create_buttons_row()
        self.create_images_panels()
        self.main_layout.addStretch()


    def create_buttons_row(self):
        row_widget = QWidget()
        row_widget.setStyleSheet("border-bottom: 1px solid #404040; border-top: 1px solid #404040;")
        self.main_layout.addWidget(row_widget)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(5, 5, 5, 5)

        button1 = ButtonWidget("Select Images")
        button2 = ButtonWidget("Remove BG")
        button3 = ButtonWidget("Save Results")


        button_layout.addWidget(button1)
        button_layout.addStretch()
        button_layout.addWidget(button2)
        button_layout.addStretch()
        button_layout.addWidget(button3)

        row_widget.setLayout(button_layout)

    def create_images_panels(self):
        # Create a horizontal splitter for left/right panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)  # thickness of draggable handle
        splitter.setStyleSheet("QSplitter::handle { background-color: #404040; }")

        # Left panel: loaded images
        self.images_panel_load = ImagesPanelWidget(None, empty_text="Drag & drop or select images")
        self.images_panel_load.setMinimumWidth(200)
        self.images_panel_load.setStyleSheet("background-color: #303030;")
        splitter.addWidget(self.images_panel_load)

        # Right panel: result images
        self.images_panel_result = ImagesPanelWidget(None, empty_text="No results yet")
        self.images_panel_result.setMinimumWidth(200)
        self.images_panel_result.setStyleSheet("background-color: #303030;")
        splitter.addWidget(self.images_panel_result)

        # Optional: initial sizes
        splitter.setSizes([500, 500])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        # Add splitter to the main layout, it will expand to fill available space
        self.main_layout.addWidget(splitter)
        self.main_layout.setStretchFactor(splitter, 1)

        
q_window_style = """
    QMainWindow {
        background-color: #353535;
    }
"""