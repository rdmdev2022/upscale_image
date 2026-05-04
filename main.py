"""
Image Upscaler Pro - Entry Point
Upscale your photos to 2K, 4K, or 8K resolution.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.main_window import MainWindow
from ui.styles import DARK_STYLESHEET


def main():
    """Launch the Image Upscaler Pro application."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Image Upscaler Pro")
    app.setOrganizationName("UpscalerPro")

    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Apply dark theme stylesheet
    app.setStyleSheet(DARK_STYLESHEET)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
