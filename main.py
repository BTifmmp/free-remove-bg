import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow  # import the window

from src.scripts.model_downloader import ModelDownloader

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # ModelDownloader()._download_model20() 
    main()