from PyQt5.QtWidgets import QPushButton

class ButtonWidget(QPushButton):
    def __init__(self, label, icon_path=None):
        super().__init__(label)
        self.icon_path = icon_path

        self.setStyleSheet(button_style)


button_style = """
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