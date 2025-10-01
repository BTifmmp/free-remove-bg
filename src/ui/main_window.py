from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QHBoxLayout, QWidget, QVBoxLayout, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from .button_widget import ButtonWidget
from .images_panel_widget import ImagesPanelWidget
from .drop_mask_widget import DropMask
from .images_controller import ImagesController
from .drop_handler import DropHandler
from .images_model import ImagesModel
from .info_log_widget import InfoLogsWidget
from .qt_logger import QtLogger
from .model_type_controller import ModelTypeController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_window()
        
        # Main layout
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        central.setLayout(self.main_layout)

        # Images models and controllers
        self.images_model = ImagesModel()
        self.res_images_model = ImagesModel()
        self.images_controller = ImagesController(self.images_model)
        self.res_images_controller = ImagesController(self.res_images_model)
        self.model_type_controller = ModelTypeController()
        self.model_type_controller.modelChanged.connect(self.images_controller.setModelName)
        self.images_controller.clear_temp() # clear temp on start
        self.images_controller.backgroundRemoved.connect(lambda x: self.res_images_controller.add_images(x, False))

        # Create main UI components
        self.create_menu_bar()
        self.create_buttons_row()
        self.create_resizable_layout()

        # Drag and drop setup
        self.dropHandler = DropHandler(self.images_panel_load)
        self.images_panel_load.setAcceptDrops(True)
        self.mask = DropMask(self.images_panel_load)
        self.mask.raise_()
        self.dropHandler.dropEntered.connect(self.mask.show)
        self.dropHandler.dropExited.connect(self.mask.hide)
        self.dropHandler.filesDropped.connect(lambda paths: self.images_controller.add_images(paths, log=True))
        
        QtLogger.instance().log("Application started.")

    def setup_window(self):
        # self.setAcceptDrops(True)
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

        self.setStyleSheet('background-color: #353535; color: #eaeaea;')

    def create_menu_bar(self):
        files_menu = self.menuBar().addMenu("Files")
        model_menu = self.menuBar().addMenu("Model")
        help_menu = self.menuBar().addMenu("Help")

        # Add actions to the file menu
        load_images = files_menu.addAction("Load Images")
        load_images.triggered.connect(lambda: self.images_controller.select_images(self))
        clear_images = files_menu.addAction("Clear Images")
        clear_images.triggered.connect(lambda: self.images_controller.clear_images(log=True))
        clear_images.triggered.connect(lambda: self.res_images_controller.clear_images(log=False))
        remove_bg = files_menu.addAction("Remove Background")
        remove_bg.triggered.connect(self.images_controller.remove_bg_from_all)
        save_results = files_menu.addAction("Save Results")
        save_results.triggered.connect(lambda: self.res_images_controller.save_images(self))
        files_menu.addSeparator()
        exit_action = files_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        # Add actions to the model menu
        model14 = model_menu.addAction("RMBGv1.4")
        model20 = model_menu.addAction("RMBGv2.0")
        model14.setCheckable(True)
        model20.setCheckable(True)
        def select_model(action):
            if action == model14:
                self.model_type_controller.set_model("rmbg14")
                model14.setChecked(True)
                model20.setChecked(False)
            else:
                self.model_type_controller.set_model("rmbg20")
                model14.setChecked(False)
                model20.setChecked(True)
        select_model(model14)  # default
        model14.triggered.connect(lambda: select_model(model14))
        model20.triggered.connect(lambda: select_model(model20))
        model_menu.addSeparator()
        clear_models = model_menu.addAction(f"Clear Model ({self.model_type_controller.get_model()})")
        clear_models.triggered.connect(self.model_type_controller.clear_models)
        
        # Add actions to the help menu
        open_github = help_menu.addAction("See on GitHub")
        open_github.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/BTifmmp/free-remove-bg")))

        self.menuBar().setStyleSheet(menu_style)

    def create_buttons_row(self):
        row_widget = QWidget()
        row_widget.setStyleSheet("border-bottom: 1px solid #404040; border-top: 1px solid #404040;")
        self.main_layout.addWidget(row_widget)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(5, 5, 5, 5)

        button1 = ButtonWidget("Select Images")
        button1.clicked.connect(lambda: self.images_controller.select_images(self))
        button11 = ButtonWidget("Clear")
        button11.clicked.connect(lambda: self.images_controller.clear_images(log=True))
        button11.clicked.connect(lambda: self.res_images_controller.clear_images(log=False))
        button2 = ButtonWidget("Remove BG")
        button2.clicked.connect(self.images_controller.remove_bg_from_all)
        button3 = ButtonWidget("Save Results")
        button3.clicked.connect(lambda: self.res_images_controller.save_images(self))

        mini_row = QHBoxLayout()
        mini_row.addWidget(button1)
        mini_row.addWidget(button11)

        button_layout.addLayout(mini_row)
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
        self.images_panel_load = ImagesPanelWidget(self.images_controller, empty_text="Drag & drop or select images")
        self.images_panel_load.setMinimumWidth(200)
        self.images_panel_load.setStyleSheet("background-color: #303030;")
        splitter.addWidget(self.images_panel_load)

        # Right panel: result images
        self.images_panel_result = ImagesPanelWidget(self.res_images_controller, empty_text="No results yet")
        self.images_panel_result.setMinimumWidth(200)
        self.images_panel_result.setStyleSheet("background-color: #303030;")
        splitter.addWidget(self.images_panel_result)

        # Optional: initial sizes
        splitter.setSizes([500, 500])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        # Add splitter to the main layout, it will expand to fill available space
        # self.main_layout.addWidget(splitter)
        # self.main_layout.setStretchFactor(splitter, 1)

        return splitter
    
    def create_resizable_layout(self):
        images_splitter = self.create_images_panels()
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(1)  # thickness of draggable handle
        splitter.setStyleSheet("QSplitter::handle { background-color: #404040; }")
        splitter.addWidget(images_splitter)
        splitter.addWidget(InfoLogsWidget())
        splitter.setStretchFactor(0, 1)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setSizes([1000, 100])
        self.main_layout.addWidget(splitter)

    def closeEvent(self, a0):
        self.images_controller.clear_temp() # clear temp on exit
        return super().closeEvent(a0)


menu_style = """
    /* Menu bar background */
    QMenuBar {
        background-color: #353535;
        color: #eaeaea; 
        font-size: 14px;
        padding: 5px 0px;
    }

    /* Highlight menu bar items when hovered */
    QMenuBar::item:selected {
        background-color: #404040;
    }

    /* Menu drop-down background */
    QMenu {
        background-color: #404040; 
        color: #eaeaea;
        border: 1px solid #505050;
    }

    /* Menu item hovered */
    QMenu::item:selected {
        background-color: #505050;
    }

    /* Disabled menu items */
    QMenu::item:disabled {
        color: #888;
    }

    /* Optional separator style */
    QMenu::separator {
        height: 1px;
        background: #505050;
        margin: 5px 0px;
    }
    """