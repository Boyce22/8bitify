"""
Reusable UI components for the application.
"""

import io
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSlider, QFileDialog, QFrame
)
from config.constants import COLORS, MONO_FONT


class DropZone(QLabel):
    """
    Custom drop zone for image file drag-and-drop.
    
    Signals:
        file_dropped: Emitted when a file is dropped or selected
    """
    
    file_dropped = pyqtSignal(str)

    def __init__(self):
        """Initialize drop zone."""
        super().__init__()
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(180)
        self._reset_style()

    def _reset_style(self):
        """Reset to default style."""
        self.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {COLORS['border']};
                background: {COLORS['surface']};
                color: {COLORS['muted']};
                font-family: "{MONO_FONT}";
                font-size: 11px;
                letter-spacing: 2px;
            }}
        """)
        self.setText("[ DROP IMAGE HERE ]\n\nor click to browse")

    def _hover_style(self):
        """Apply hover style."""
        self.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {COLORS['accent']};
                background: {COLORS['surface']};
                color: {COLORS['accent']};
                font-family: "{MONO_FONT}";
                font-size: 11px;
                letter-spacing: 2px;
            }}
        """)

    def mousePressEvent(self, _):
        """Handle mouse click to open file dialog."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if path:
            self._load_image(path)

    def dragEnterEvent(self, e: QDragEnterEvent):
        """Handle drag enter event."""
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._hover_style()

    def dragLeaveEvent(self, _):
        """Handle drag leave event."""
        self._reset_style()

    def dropEvent(self, e: QDropEvent):
        """Handle drop event."""
        urls = e.mimeData().urls()
        if urls:
            self._load_image(urls[0].toLocalFile())

    def _load_image(self, path: str):
        """Load and display image preview."""
        pixmap = QPixmap(path).scaled(
            self.width() - 4, self.height() - 4,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(pixmap)
        self.setStyleSheet(f"QLabel {{ border: 1px solid {COLORS['accent']}; background: {COLORS['surface']}; }}")
        self.file_dropped.emit(path)


class ParamSlider(QWidget):
    """
    Custom slider widget with label and value display.
    """
    
    def __init__(self, label: str, min_val: int, max_val: int, default: int, scale: float = 1.0):
        """
        Initialize parameter slider.
        
        Args:
            label: Display label
            min_val: Minimum slider value
            max_val: Maximum slider value
            default: Default slider value
            scale: Value scaling factor
        """
        super().__init__()
        self.scale = scale
        self._setup_ui(label, min_val, max_val, default)

    def _setup_ui(self, label: str, min_val: int, max_val: int, default: int):
        """Set up UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Label
        lbl = QLabel(label)
        lbl.setFixedWidth(130)
        lbl.setStyleSheet(f"color: {COLORS['text']}; font-size: 11px;")

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(default)

        # Value display
        self.value_label = QLabel(self._format_value(default))
        self.value_label.setObjectName("value")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.slider.valueChanged.connect(lambda v: self.value_label.setText(self._format_value(v)))

        # Add widgets to layout
        layout.addWidget(lbl)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)

    def _format_value(self, value: int) -> str:
        """Format value for display."""
        real_value = value * self.scale
        return f"{real_value:.2f}" if self.scale != 1.0 else str(value)

    def value(self) -> float:
        """Get current scaled value."""
        return self.slider.value() * self.scale

    def set_value(self, value: float):
        """Set slider value (scaled)."""
        self.slider.setValue(round(value / self.scale))


def create_horizontal_line() -> QFrame:
    """
    Create a horizontal separator line.
    
    Returns:
        QFrame configured as horizontal line
    """
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {COLORS['border']};")
    return line


def pil_to_pixmap(image) -> QPixmap:
    """
    Convert PIL Image to QPixmap.
    
    Args:
        image: PIL Image
        
    Returns:
        QPixmap
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return QPixmap.fromImage(QImage.fromData(buffer.read()))