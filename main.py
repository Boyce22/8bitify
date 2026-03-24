"""
8-Bitify - Pixel Art Converter
Main entry point for the application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui import MainWindow


def main():
    """
    Application entry point.
    """
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()