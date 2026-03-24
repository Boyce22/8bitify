"""8-Bitify Desktop — PyQt6, processamento direto (sem API)."""

import io
import sys
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QComboBox, QCheckBox, QFileDialog,
    QFrame, QScrollArea, QStackedWidget, QProgressBar,
)
from PIL import Image, ImageEnhance, ImageFilter


# ─── Presets ──────────────────────────────────────────────────────────────────

PRESETS: dict[str, dict] = {
    "Custom": {},
    "Personagem principal": {
        "size": 4, "colors": 32, "detail_level": 0.9,
        "line_enhancement": 0.6, "sharpness": 1.3, "contrast": 1.1,
        "dithering": False, "palette": "None",
    },
    "Inimigo": {
        "size": 5, "colors": 24, "detail_level": 0.7,
        "line_enhancement": 0.5, "sharpness": 1.2, "contrast": 1.1,
        "dithering": False, "palette": "None",
    },
    "Item / objeto": {
        "size": 3, "colors": 16, "detail_level": 0.8,
        "line_enhancement": 0.7, "sharpness": 1.4, "contrast": 1.1,
        "dithering": False, "palette": "None",
    },
    "Cenário": {
        "size": 6, "colors": 48, "detail_level": 0.5,
        "line_enhancement": 0.3, "sharpness": 1.0, "contrast": 1.0,
        "dithering": True, "palette": "None",
    },
    "Game Boy": {
        "size": 4, "colors": 4, "detail_level": 0.7,
        "line_enhancement": 0.4, "sharpness": 1.2, "contrast": 1.2,
        "dithering": False, "palette": "gameboy",
    },
    "NES": {
        "size": 5, "colors": 16, "detail_level": 0.6,
        "line_enhancement": 0.4, "sharpness": 1.1, "contrast": 1.15,
        "dithering": True, "palette": "nes",
    },
    "VGA retrô": {
        "size": 3, "colors": 256, "detail_level": 1.0,
        "line_enhancement": 0.3, "sharpness": 1.1, "contrast": 1.05,
        "dithering": True, "palette": "vga",
    },
    "Ultra detalhe": {
        "size": 3, "colors": 64, "detail_level": 1.5,
        "line_enhancement": 0.6, "sharpness": 1.4, "contrast": 1.1,
        "dithering": False, "palette": "None",
    },
    "Pixel grosso": {
        "size": 12, "colors": 16, "detail_level": 0.3,
        "line_enhancement": 0.2, "sharpness": 1.0, "contrast": 1.0,
        "dithering": False, "palette": "None",
    },
}


# ─── Processamento ────────────────────────────────────────────────────────────

def enhance_lines(image: Image.Image, strength: float) -> Image.Image:
    if strength <= 0:
        return image

    edges = image.filter(ImageFilter.FIND_EDGES).convert("L")
    edges = edges.point(lambda x: min(255, int(x * (1 + strength))))

    factor   = 1 - strength * 0.3
    channels = [ch.point(lambda x: int(x * factor)) for ch in image.split()]
    darkened = Image.merge(image.mode, channels)

    mask = edges.point(lambda x: 255 if x > 50 else 0)
    return Image.composite(darkened, image, mask)


def pixelate_advanced(
    image: Image.Image,
    pixel_size: int,
    colors: int,
    dithering: bool = False,
    detail_level: float = 0.5,
    line_enhancement: float = 0.3,
) -> Image.Image:
    width, height = image.size

    if detail_level >= 1.2:
        effective_size = max(1, pixel_size - 2) if pixel_size > 2 else 1
        small_w = max(1, width // effective_size)
        small_h = max(1, height // effective_size)
        resize_method = Image.Resampling.LANCZOS
    elif detail_level >= 0.8:
        small_w = max(1, width // pixel_size)
        small_h = max(1, height // pixel_size)
        resize_method = Image.Resampling.LANCZOS
    elif detail_level >= 0.4:
        small_w = max(1, width // pixel_size)
        small_h = max(1, height // pixel_size)
        resize_method = Image.Resampling.BICUBIC
    else:
        small_w = max(1, width // pixel_size)
        small_h = max(1, height // pixel_size)
        resize_method = Image.Resampling.NEAREST

    if line_enhancement > 0 and detail_level > 0.6:
        image = enhance_lines(image, line_enhancement * 0.5)

    small = image.resize((small_w, small_h), resize_method)

    if detail_level > 0.5:
        sharpness = 1.0 + (detail_level - 0.5) * 0.5
        small = ImageEnhance.Sharpness(small).enhance(min(sharpness, 1.8))

    if colors < 256:
        dither_mode = Image.Dither.FLOYDSTEINBERG if dithering else Image.Dither.NONE
        small = small.quantize(colors=colors, dither=dither_mode).convert("RGB")

    result = small.resize((small_w * pixel_size, small_h * pixel_size), Image.Resampling.NEAREST)

    if line_enhancement > 0:
        result = enhance_lines(result, line_enhancement * 0.7)

    if detail_level > 0.7:
        result = ImageEnhance.Sharpness(result).enhance(1.1)

    return result


def apply_palette(image: Image.Image, palette: str) -> Image.Image:
    if palette == "gameboy":
        colors = [(15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)]
        palette_img = Image.new("P", (1, 1))
        palette_img.putpalette([c for color in colors for c in color] * 64)
        return image.convert("L").quantize(colors=4, palette=palette_img).convert("RGB")

    if palette in ("nes", "vga"):
        num_colors = 16 if palette == "nes" else 256
        return image.quantize(
            colors=num_colors,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.FLOYDSTEINBERG,
        ).convert("RGB")

    return image


def process_image(source_path: str, params: dict) -> tuple[Image.Image, dict]:
    img = Image.open(source_path)

    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    contrast  = params.get("contrast", 1.0)
    sharpness = params.get("sharpness", 1.0)
    detail    = params.get("detail_level", 0.8)

    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if sharpness != 1.0 and detail > 0.5:
        img = ImageEnhance.Sharpness(img).enhance(sharpness)

    result = pixelate_advanced(
        img,
        pixel_size=params.get("size", 4),
        colors=params.get("colors", 32),
        dithering=params.get("dithering", False),
        detail_level=detail,
        line_enhancement=params.get("line_enhancement", 0.5),
    )

    palette = params.get("palette", "None")
    if palette and palette != "None":
        result = apply_palette(result, palette.lower())

    if sharpness != 1.0:
        result = ImageEnhance.Sharpness(result).enhance(sharpness)
    if contrast != 1.0:
        result = ImageEnhance.Contrast(result).enhance(contrast)

    meta = {
        "original_size": f"{img.width}x{img.height}",
        "final_size":    f"{result.width}x{result.height}",
        "pixel_size":    params.get("size", 4),
        "colors":        params.get("colors", 32),
        "palette":       palette,
    }
    return result, meta


# ─── Worker ───────────────────────────────────────────────────────────────────

class Worker(QThread):
    finished = pyqtSignal(object, dict)
    error    = pyqtSignal(str)

    def __init__(self, source_path: str, params: dict):
        super().__init__()
        self.source_path = source_path
        self.params      = params

    def run(self):
        try:
            result, meta = process_image(self.source_path, self.params)
            self.finished.emit(result, meta)
        except Exception as e:
            self.error.emit(str(e))


# ─── Tema ─────────────────────────────────────────────────────────────────────

C = {
    "bg":      "#0a0a0f",
    "surface": "#12121a",
    "panel":   "#1a1a26",
    "border":  "#2a2a3f",
    "accent":  "#00ff88",
    "accent2": "#ff3366",
    "accent3": "#ffcc00",
    "text":    "#e0e0f0",
    "muted":   "#666688",
    "pixel":   "#00cc66",
}

MONO = "Courier New"

QSS = f"""
QMainWindow, QWidget {{
    background: {C['bg']};
    color: {C['text']};
    font-family: "{MONO}";
    font-size: 12px;
}}
QLabel#title {{
    color: {C['accent']};
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 4px;
}}
QLabel#subtitle {{
    color: {C['muted']};
    font-size: 10px;
    letter-spacing: 3px;
}}
QLabel#section {{
    color: {C['accent3']};
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
}}
QLabel#value {{
    color: {C['accent']};
    font-size: 11px;
    min-width: 36px;
}}
QPushButton#primary {{
    background: {C['accent']};
    color: {C['bg']};
    border: none;
    padding: 10px 24px;
    font-family: "{MONO}";
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 2px;
}}
QPushButton#primary:hover   {{ background: #00ffaa; }}
QPushButton#primary:pressed {{ background: {C['pixel']}; }}
QPushButton#primary:disabled {{ background: {C['border']}; color: {C['muted']}; }}
QPushButton#ghost {{
    background: transparent;
    color: {C['muted']};
    border: 1px solid {C['border']};
    padding: 6px 16px;
    font-family: "{MONO}";
    font-size: 11px;
}}
QPushButton#ghost:hover {{ color: {C['text']}; border-color: {C['muted']}; }}
QSlider::groove:horizontal {{ height: 3px; background: {C['border']}; }}
QSlider::handle:horizontal {{
    background: {C['accent']};
    width: 12px; height: 12px;
    margin: -5px 0;
}}
QSlider::sub-page:horizontal {{ background: {C['accent']}; height: 3px; }}
QComboBox {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    color: {C['text']};
    padding: 4px 10px;
    font-family: "{MONO}";
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    color: {C['text']};
    selection-background-color: {C['accent']};
    selection-color: {C['bg']};
}}
QCheckBox {{ color: {C['text']}; spacing: 8px; }}
QCheckBox::indicator {{
    width: 14px; height: 14px;
    border: 1px solid {C['border']};
    background: {C['surface']};
}}
QCheckBox::indicator:checked {{
    background: {C['accent']};
    border-color: {C['accent']};
}}
QProgressBar {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    height: 4px;
    color: transparent;
}}
QProgressBar::chunk {{ background: {C['accent']}; }}
QScrollBar:vertical {{
    background: {C['surface']};
    width: 6px; border: none;
}}
QScrollBar::handle:vertical {{
    background: {C['border']};
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {C['muted']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""


# ─── Drop Zone ────────────────────────────────────────────────────────────────

class DropZone(QLabel):
    file_dropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(180)
        self._reset()

    def _reset(self):
        self.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {C['border']};
                background: {C['surface']};
                color: {C['muted']};
                font-family: "{MONO}";
                font-size: 11px;
                letter-spacing: 2px;
            }}
        """)
        self.setText("[ DROP IMAGE HERE ]\n\nor click to browse")

    def _hover(self):
        self.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {C['accent']};
                background: {C['surface']};
                color: {C['accent']};
                font-family: "{MONO}";
                font-size: 11px;
                letter-spacing: 2px;
            }}
        """)

    def mousePressEvent(self, _):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if path:
            self._load(path)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._hover()

    def dragLeaveEvent(self, _):
        self._reset()

    def dropEvent(self, e: QDropEvent):
        urls = e.mimeData().urls()
        if urls:
            self._load(urls[0].toLocalFile())

    def _load(self, path: str):
        px = QPixmap(path).scaled(
            self.width() - 4, self.height() - 4,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(px)
        self.setStyleSheet(f"QLabel {{ border: 1px solid {C['accent']}; background: {C['surface']}; }}")
        self.file_dropped.emit(path)


# ─── Param Slider ─────────────────────────────────────────────────────────────

class ParamSlider(QWidget):
    def __init__(self, label: str, min_: int, max_: int, default: int, scale: float = 1.0):
        super().__init__()
        self.scale = scale
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        lbl = QLabel(label)
        lbl.setFixedWidth(130)
        lbl.setStyleSheet(f"color: {C['text']}; font-size: 11px;")

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_, max_)
        self.slider.setValue(default)

        self.val_lbl = QLabel(self._fmt(default))
        self.val_lbl.setObjectName("value")
        self.val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.slider.valueChanged.connect(lambda v: self.val_lbl.setText(self._fmt(v)))

        layout.addWidget(lbl)
        layout.addWidget(self.slider)
        layout.addWidget(self.val_lbl)

    def _fmt(self, v: int) -> str:
        real = v * self.scale
        return f"{real:.2f}" if self.scale != 1.0 else str(v)

    def value(self) -> float:
        return self.slider.value() * self.scale

    def set_value(self, v: float):
        self.slider.setValue(round(v / self.scale))


# ─── Main Window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("8-BITIFY")
        self.setMinimumSize(1000, 700)
        self._source_path: Optional[str]        = None
        self._worker: Optional[Worker]           = None
        self._result_img: Optional[Image.Image]  = None
        self._applying_preset                    = False

        self.setStyleSheet(QSS)
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        lay = QHBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self._build_sidebar(), 0)
        lay.addWidget(self._build_canvas(),  1)

    def _build_sidebar(self) -> QWidget:
        sb = QFrame()
        sb.setFixedWidth(300)
        sb.setStyleSheet(f"QFrame {{ background: {C['panel']}; border-right: 1px solid {C['border']}; }}")
        lay = QVBoxLayout(sb)
        lay.setContentsMargins(20, 24, 20, 20)
        lay.setSpacing(6)

        t = QLabel("8-BITIFY")
        t.setObjectName("title")
        s = QLabel("PIXEL ART CONVERTER")
        s.setObjectName("subtitle")
        lay.addWidget(t)
        lay.addWidget(s)
        lay.addSpacing(14)
        lay.addWidget(self._hr())

        # Presets
        lay.addSpacing(8)
        lay.addWidget(self._section("▸ PRESET"))
        self.combo_preset = QComboBox()
        self.combo_preset.addItems(list(PRESETS.keys()))
        self.combo_preset.currentTextChanged.connect(self._apply_preset)
        lay.addWidget(self.combo_preset)
        lay.addSpacing(10)
        lay.addWidget(self._hr())

        # Image
        lay.addSpacing(8)
        lay.addWidget(self._section("▸ IMAGE"))
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_file)
        lay.addWidget(self.drop_zone)
        lay.addSpacing(10)
        lay.addWidget(self._hr())

        # Pixel
        lay.addSpacing(6)
        lay.addWidget(self._section("▸ PIXEL"))
        self.s_size   = ParamSlider("Pixel Size",   1,  20,  4)
        self.s_colors = ParamSlider("Colors",       2, 256, 32)
        self.s_detail = ParamSlider("Detail Level", 0, 200, 80, scale=0.01)
        self.s_lines  = ParamSlider("Line Enhance", 0, 100, 50, scale=0.01)
        for w in (self.s_size, self.s_colors, self.s_detail, self.s_lines):
            w.slider.valueChanged.connect(self._on_manual_change)
            lay.addWidget(w)

        lay.addSpacing(8)
        lay.addWidget(self._hr())

        # Tone
        lay.addSpacing(6)
        lay.addWidget(self._section("▸ TONE"))
        self.s_sharp    = ParamSlider("Sharpness", 50, 200, 120, scale=0.01)
        self.s_contrast = ParamSlider("Contrast",  50, 200, 110, scale=0.01)
        for w in (self.s_sharp, self.s_contrast):
            w.slider.valueChanged.connect(self._on_manual_change)
            lay.addWidget(w)

        lay.addSpacing(8)
        lay.addWidget(self._hr())

        # Options
        lay.addSpacing(6)
        lay.addWidget(self._section("▸ OPTIONS"))
        row = QHBoxLayout()
        self.cb_dither = QCheckBox("Dithering")
        self.cb_dither.stateChanged.connect(self._on_manual_change)
        self.combo_palette = QComboBox()
        self.combo_palette.addItems(["None", "gameboy", "nes", "vga"])
        self.combo_palette.setFixedWidth(100)
        self.combo_palette.currentTextChanged.connect(self._on_manual_change)
        row.addWidget(self.cb_dither)
        row.addStretch()
        row.addWidget(QLabel("Palette"))
        row.addWidget(self.combo_palette)
        lay.addLayout(row)

        lay.addStretch()

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        lay.addWidget(self.progress)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(f"color: {C['muted']}; font-size: 10px;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.status_lbl)
        lay.addSpacing(4)

        btn_row = QHBoxLayout()
        self.btn_convert = QPushButton("▶  CONVERT")
        self.btn_convert.setObjectName("primary")
        self.btn_convert.setEnabled(False)
        self.btn_convert.clicked.connect(self._convert)

        self.btn_save = QPushButton("SAVE")
        self.btn_save.setObjectName("ghost")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._save)

        btn_row.addWidget(self.btn_convert)
        btn_row.addWidget(self.btn_save)
        lay.addLayout(btn_row)

        return sb

    def _build_canvas(self) -> QWidget:
        c = QWidget()
        c.setStyleSheet(f"background: {C['bg']};")
        lay = QVBoxLayout(c)
        lay.setContentsMargins(0, 0, 0, 0)

        bar = QWidget()
        bar.setFixedHeight(40)
        bar.setStyleSheet(f"background: {C['surface']}; border-bottom: 1px solid {C['border']};")
        bar_lay = QHBoxLayout(bar)
        bar_lay.setContentsMargins(16, 0, 16, 0)
        self.info_lbl = QLabel("NO IMAGE")
        self.info_lbl.setStyleSheet(f"color: {C['muted']}; font-size: 10px; letter-spacing: 2px;")
        bar_lay.addWidget(self.info_lbl)
        bar_lay.addStretch()
        lay.addWidget(bar)

        self.stack = QStackedWidget()

        empty     = QWidget()
        empty_lay = QVBoxLayout(empty)
        empty_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph = QLabel("[ NO OUTPUT YET ]")
        ph.setStyleSheet(f"color: {C['border']}; font-size: 14px; letter-spacing: 4px;")
        ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_lay.addWidget(ph)
        self.stack.addWidget(empty)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setStyleSheet(f"border: none; background: {C['bg']};")
        self.result_lbl = QLabel()
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(self.result_lbl)
        self.stack.addWidget(scroll)

        lay.addWidget(self.stack)

        meta_bar = QWidget()
        meta_bar.setFixedHeight(32)
        meta_bar.setStyleSheet(f"background: {C['surface']}; border-top: 1px solid {C['border']};")
        meta_lay = QHBoxLayout(meta_bar)
        meta_lay.setContentsMargins(16, 0, 16, 0)
        self.meta_lbl = QLabel("")
        self.meta_lbl.setStyleSheet(f"color: {C['muted']}; font-size: 10px;")
        meta_lay.addWidget(self.meta_lbl)
        lay.addWidget(meta_bar)

        return c

    def _hr(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {C['border']};")
        return line

    def _section(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("section")
        return lbl

    def _set_status(self, msg: str, ok: bool = True):
        color = C["accent"] if ok else C["accent2"]
        self.status_lbl.setStyleSheet(f"color: {color}; font-size: 10px; letter-spacing: 1px;")
        self.status_lbl.setText(msg)

    def _pil_to_pixmap(self, img: Image.Image) -> QPixmap:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return QPixmap.fromImage(QImage.fromData(buf.read()))

    def _apply_preset(self, name: str):
        preset = PRESETS.get(name, {})
        if not preset:
            return
        self._applying_preset = True
        self.s_size.set_value(preset["size"])
        self.s_colors.set_value(preset["colors"])
        self.s_detail.set_value(preset["detail_level"])
        self.s_lines.set_value(preset["line_enhancement"])
        self.s_sharp.set_value(preset["sharpness"])
        self.s_contrast.set_value(preset["contrast"])
        self.cb_dither.setChecked(preset["dithering"])
        idx = self.combo_palette.findText(preset["palette"])
        if idx >= 0:
            self.combo_palette.setCurrentIndex(idx)
        self._applying_preset = False

    def _on_manual_change(self, *_):
        if not self._applying_preset:
            self.combo_preset.blockSignals(True)
            self.combo_preset.setCurrentText("Custom")
            self.combo_preset.blockSignals(False)

    def _on_file(self, path: str):
        self._source_path = path
        self.btn_convert.setEnabled(True)
        name = path.replace("\\", "/").split("/")[-1]
        self.info_lbl.setText(f"SOURCE  ›  {name}")
        self._set_status("")

    def _collect_params(self) -> dict:
        return {
            "size":             int(self.s_size.value()),
            "colors":           int(self.s_colors.value()),
            "detail_level":     self.s_detail.value(),
            "line_enhancement": self.s_lines.value(),
            "sharpness":        self.s_sharp.value(),
            "contrast":         self.s_contrast.value(),
            "dithering":        self.cb_dither.isChecked(),
            "palette":          self.combo_palette.currentText(),
        }

    def _convert(self):
        if not self._source_path:
            return
        self.btn_convert.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.progress.setVisible(True)
        self._set_status("processing…")
        self._worker = Worker(self._source_path, self._collect_params())
        self._worker.finished.connect(self._on_result)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_result(self, img: Image.Image, meta: dict):
        self.progress.setVisible(False)
        self.btn_convert.setEnabled(True)
        self.btn_save.setEnabled(True)
        self._result_img = img
        self.result_lbl.setPixmap(self._pil_to_pixmap(img))
        self.stack.setCurrentIndex(1)
        self.meta_lbl.setText(
            f"  {meta['original_size']}  →  {meta['final_size']}  "
            f"│  pixels: {meta['pixel_size']}  "
            f"│  colors: {meta['colors']}  "
            f"│  palette: {meta['palette']}"
        )
        self._set_status("done ✓", ok=True)

    def _on_error(self, msg: str):
        self.progress.setVisible(False)
        self.btn_convert.setEnabled(True)
        self._set_status(f"error: {msg}", ok=False)

    def _save(self):
        if self._result_img is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Pixel Art", "pixel_art.png", "PNG (*.png)")
        if path:
            self._result_img.save(path, "PNG", optimize=True)
            self._set_status(f"saved → {path}", ok=True)


# ─── Entry ────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()