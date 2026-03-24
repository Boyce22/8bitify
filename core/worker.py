"""
Worker thread for background image processing.
"""

from typing import Optional
from PyQt6.QtCore import QThread, pyqtSignal
from .image_processor import process_image


class Worker(QThread):
    """
    Worker thread for processing images in the background.
    
    Signals:
        finished: Emitted when processing completes successfully
        error: Emitted when an error occurs during processing
    """
    
    finished = pyqtSignal(object, dict)  # (image, metadata)
    error = pyqtSignal(str)  # error_message

    def __init__(self, source_path: str, params: dict):
        """
        Initialize worker.
        
        Args:
            source_path: Path to source image
            params: Processing parameters dictionary
        """
        super().__init__()
        self.source_path = source_path
        self.params = params

    def run(self):
        """
        Main processing method (runs in background thread).
        """
        try:
            result, meta = process_image(self.source_path, self.params)
            self.finished.emit(result, meta)
        except Exception as e:
            self.error.emit(str(e))