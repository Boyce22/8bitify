"""
Main application window.
"""

import sys
from typing import Optional
from PIL import Image

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QCheckBox, QFileDialog,
    QFrame, QScrollArea, QStackedWidget, QProgressBar,
)

from config.constants import PRESETS, STYLESHEET, COLORS
from core.worker import Worker
from ui.components import DropZone, ParamSlider, create_horizontal_line, pil_to_pixmap


class MainWindow(QMainWindow):
    """
    Main application window for 8-Bitify.
    """
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self._source_path: Optional[str] = None
        self._worker: Optional[Worker] = None
        self._result_img: Optional[Image.Image] = None
        self._applying_preset = False
        
        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        """Set up window properties."""
        self.setWindowTitle("8-BITIFY")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(STYLESHEET)

    def _build_ui(self):
        """Build the main UI layout."""
        root = QWidget()
        self.setCentralWidget(root)
        
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addWidget(self._build_sidebar(), 0)
        layout.addWidget(self._build_canvas(), 1)

    def _build_sidebar(self) -> QWidget:
        """Build the sidebar with controls."""
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet(
            f"QFrame {{ background: {COLORS['panel']}; border-right: 1px solid {COLORS['border']}; }}"
        )
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(6)
        
        # Title
        title_label = QLabel("8-BITIFY")
        title_label.setObjectName("title")
        subtitle_label = QLabel("PIXEL ART CONVERTER")
        subtitle_label.setObjectName("subtitle")
        
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(14)
        layout.addWidget(create_horizontal_line())
        
        # Presets section
        layout.addSpacing(8)
        layout.addWidget(self._create_section_label("▸ PRESET"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(PRESETS.keys()))
        self.preset_combo.currentTextChanged.connect(self._apply_preset)
        layout.addWidget(self.preset_combo)
        layout.addSpacing(10)
        layout.addWidget(create_horizontal_line())
        
        # Image section
        layout.addSpacing(8)
        layout.addWidget(self._create_section_label("▸ IMAGE"))
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_file_selected)
        layout.addWidget(self.drop_zone)
        layout.addSpacing(10)
        layout.addWidget(create_horizontal_line())
        
        # Pixel settings section
        layout.addSpacing(6)
        layout.addWidget(self._create_section_label("▸ PIXEL"))
        self.size_slider = ParamSlider("Pixel Size", 1, 20, 4)
        self.colors_slider = ParamSlider("Colors", 2, 256, 32)
        self.detail_slider = ParamSlider("Detail Level", 0, 200, 80, scale=0.01)
        self.lines_slider = ParamSlider("Line Enhance", 0, 100, 50, scale=0.01)
        
        for slider in (self.size_slider, self.colors_slider, self.detail_slider, self.lines_slider):
            slider.slider.valueChanged.connect(self._on_manual_change)
            layout.addWidget(slider)
        
        layout.addSpacing(8)
        layout.addWidget(create_horizontal_line())
        
        # Tone settings section
        layout.addSpacing(6)
        layout.addWidget(self._create_section_label("▸ TONE"))
        self.sharpness_slider = ParamSlider("Sharpness", 50, 200, 120, scale=0.01)
        self.contrast_slider = ParamSlider("Contrast", 50, 200, 110, scale=0.01)
        
        for slider in (self.sharpness_slider, self.contrast_slider):
            slider.slider.valueChanged.connect(self._on_manual_change)
            layout.addWidget(slider)
        
        layout.addSpacing(8)
        layout.addWidget(create_horizontal_line())
        
        # Options section
        layout.addSpacing(6)
        layout.addWidget(self._create_section_label("▸ OPTIONS"))
        
        options_layout = QHBoxLayout()
        self.dither_checkbox = QCheckBox("Dithering")
        self.dither_checkbox.stateChanged.connect(self._on_manual_change)
        
        self.palette_combo = QComboBox()
        self.palette_combo.addItems(["None", "gameboy", "nes", "vga"])
        self.palette_combo.setFixedWidth(100)
        self.palette_combo.currentTextChanged.connect(self._on_manual_change)
        
        options_layout.addWidget(self.dither_checkbox)
        options_layout.addStretch()
        options_layout.addWidget(QLabel("Palette"))
        options_layout.addWidget(self.palette_combo)
        
        layout.addLayout(options_layout)
        layout.addStretch()
        
        # Progress and status
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {COLORS['muted']}; font-size: 10px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        layout.addSpacing(4)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.convert_button = QPushButton("▶  CONVERT")
        self.convert_button.setObjectName("primary")
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self._convert_image)
        
        self.save_button = QPushButton("SAVE")
        self.save_button.setObjectName("ghost")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self._save_image)
        
        button_layout.addWidget(self.convert_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)
        
        return sidebar

    def _build_canvas(self) -> QWidget:
        """Build the main canvas area for image display."""
        canvas = QWidget()
        canvas.setStyleSheet(f"background: {COLORS['bg']};")
        
        layout = QVBoxLayout(canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Top bar
        top_bar = QWidget()
        top_bar.setFixedHeight(40)
        top_bar.setStyleSheet(
            f"background: {COLORS['surface']}; border-bottom: 1px solid {COLORS['border']};"
        )
        
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(16, 0, 16, 0)
        
        self.info_label = QLabel("NO IMAGE")
        self.info_label.setStyleSheet(
            f"color: {COLORS['muted']}; font-size: 10px; letter-spacing: 2px;"
        )
        
        top_bar_layout.addWidget(self.info_label)
        top_bar_layout.addStretch()
        layout.addWidget(top_bar)
        
        # Image display area
        self.stack_widget = QStackedWidget()
        
        # Empty state
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        placeholder = QLabel("[ NO OUTPUT YET ]")
        placeholder.setStyleSheet(
            f"color: {COLORS['border']}; font-size: 14px; letter-spacing: 4px;"
        )
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_layout.addWidget(placeholder)
        self.stack_widget.addWidget(empty_widget)
        
        # Result display
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area.setStyleSheet(f"border: none; background: {COLORS['bg']};")
        
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area.setWidget(self.result_label)
        self.stack_widget.addWidget(scroll_area)
        
        layout.addWidget(self.stack_widget)
        
        # Bottom metadata bar
        metadata_bar = QWidget()
        metadata_bar.setFixedHeight(32)
        metadata_bar.setStyleSheet(
            f"background: {COLORS['surface']}; border-top: 1px solid {COLORS['border']};"
        )
        
        metadata_layout = QHBoxLayout(metadata_bar)
        metadata_layout.setContentsMargins(16, 0, 16, 0)
        
        self.metadata_label = QLabel("")
        self.metadata_label.setStyleSheet(f"color: {COLORS['muted']}; font-size: 10px;")
        
        metadata_layout.addWidget(self.metadata_label)
        layout.addWidget(metadata_bar)
        
        return canvas

    def _create_section_label(self, text: str) -> QLabel:
        """Create a section header label."""
        label = QLabel(text)
        label.setObjectName("section")
        return label

    def _set_status(self, message: str, is_success: bool = True):
        """Update status label with message."""
        color = COLORS["accent"] if is_success else COLORS["accent2"]
        self.status_label.setStyleSheet(
            f"color: {color}; font-size: 10px; letter-spacing: 1px;"
        )
        self.status_label.setText(message)

    def _apply_preset(self, preset_name: str):
        """Apply preset values to controls."""
        preset = PRESETS.get(preset_name, {})
        if not preset:
            return
            
        self._applying_preset = True
        
        self.size_slider.set_value(preset["size"])
        self.colors_slider.set_value(preset["colors"])
        self.detail_slider.set_value(preset["detail_level"])
        self.lines_slider.set_value(preset["line_enhancement"])
        self.sharpness_slider.set_value(preset["sharpness"])
        self.contrast_slider.set_value(preset["contrast"])
        self.dither_checkbox.setChecked(preset["dithering"])
        
        index = self.palette_combo.findText(preset["palette"])
        if index >= 0:
            self.palette_combo.setCurrentIndex(index)
            
        self._applying_preset = False

    def _on_manual_change(self, *_):
        """Handle manual control changes (switch to Custom preset)."""
        if not self._applying_preset:
            self.preset_combo.blockSignals(True)
            self.preset_combo.setCurrentText("Custom")
            self.preset_combo.blockSignals(False)

    def _on_file_selected(self, file_path: str):
        """Handle file selection via drop zone or dialog."""
        self._source_path = file_path
        self.convert_button.setEnabled(True)
        
        # Extract filename for display
        filename = file_path.replace("\\", "/").split("/")[-1]
        self.info_label.setText(f"SOURCE  ›  {filename}")
        self._set_status("")

    def _collect_parameters(self) -> dict:
        """Collect all current parameter values."""
        return {
            "size": int(self.size_slider.value()),
            "colors": int(self.colors_slider.value()),
            "detail_level": self.detail_slider.value(),
            "line_enhancement": self.lines_slider.value(),
            "sharpness": self.sharpness_slider.value(),
            "contrast": self.contrast_slider.value(),
            "dithering": self.dither_checkbox.isChecked(),
            "palette": self.palette_combo.currentText(),
        }

    def _convert_image(self):
        """Start image conversion process."""
        if not self._source_path:
            return
            
        self.convert_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self._set_status("processing…")
        
        self._worker = Worker(self._source_path, self._collect_parameters())
        self._worker.finished.connect(self._on_conversion_finished)
        self._worker.error.connect(self._on_conversion_error)
        self._worker.start()

    def _on_conversion_finished(self, image: Image.Image, metadata: dict):
        """Handle successful conversion."""
        self.progress_bar.setVisible(False)
        self.convert_button.setEnabled(True)
        self.save_button.setEnabled(True)
        
        self._result_img = image
        
        # Convert PIL image to QPixmap
        pixmap = pil_to_pixmap(image)
        
        # Get the available size from the scroll area's viewport
        # The result_label is inside a QScrollArea, so we need to get the viewport size
        viewport_widget = self.result_label.parentWidget()
        if viewport_widget:
            available_size = viewport_widget.size()
        else:
            # Fallback to a reasonable default size if viewport not found
            available_size = self.result_label.size()
        
        # Ensure we have valid dimensions
        if available_size.width() <= 0 or available_size.height() <= 0:
            available_size = self.size()  # Use window size as fallback
        
        # Calculate maximum dimensions with padding
        max_width = available_size.width() - 20  # 10px padding on each side
        max_height = available_size.height() - 20  # 10px padding on each side
        
        # Get original pixmap dimensions
        original_width = pixmap.width()
        original_height = pixmap.height()
        
        # Only scale down if the image is larger than available space
        if original_width > max_width or original_height > max_height:
            # Scale down to fit while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                max_width, max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        else:
            # Keep original size if it fits
            scaled_pixmap = pixmap
        
        self.result_label.setPixmap(scaled_pixmap)
        self.stack_widget.setCurrentIndex(1)
        
        # Update metadata display
        self.metadata_label.setText(
            f"  {metadata['original_size']}  →  {metadata['final_size']}  "
            f"│  pixels: {metadata['pixel_size']}  "
            f"│  colors: {metadata['colors']}  "
            f"│  palette: {metadata['palette']}"
        )
        
        self._set_status("done ✓", is_success=True)

    def _on_conversion_error(self, error_message: str):
        """Handle conversion error."""
        self.progress_bar.setVisible(False)
        self.convert_button.setEnabled(True)
        self._set_status(f"error: {error_message}", is_success=False)

    def _save_image(self):
        """Save converted image to file."""
        if self._result_img is None:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Pixel Art", "pixel_art.png", "PNG (*.png)"
        )
        
        if file_path:
            self._result_img.save(file_path, "PNG", optimize=True)
            self._set_status(f"saved → {file_path}", is_success=True)