"""
Application constants and presets.
"""

# ─── Presets ──────────────────────────────────────────────────────────────────

PRESETS: dict[str, dict] = {
    "Custom": {},
    "Main Character": {
        "size": 4, "colors": 32, "detail_level": 0.9,
        "line_enhancement": 0.6, "sharpness": 1.3, "contrast": 1.1,
        "dithering": False, "palette": "None",
    },
    "Enemy": {
        "size": 5, "colors": 24, "detail_level": 0.7,
        "line_enhancement": 0.5, "sharpness": 1.2, "contrast": 1.1,
        "dithering": False, "palette": "None",
    },
    "Item / Object": {
        "size": 3, "colors": 16, "detail_level": 0.8,
        "line_enhancement": 0.7, "sharpness": 1.4, "contrast": 1.1,
        "dithering": False, "palette": "None",
    },
    "Background": {
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
    "Retro VGA": {
        "size": 3, "colors": 256, "detail_level": 1.0,
        "line_enhancement": 0.3, "sharpness": 1.1, "contrast": 1.05,
        "dithering": True, "palette": "vga",
    },
    "Ultra Detail": {
        "size": 3, "colors": 64, "detail_level": 1.5,
        "line_enhancement": 0.6, "sharpness": 1.4, "contrast": 1.1,
        "dithering": False, "palette": "None",
    },
    "Big Pixel": {
        "size": 12, "colors": 16, "detail_level": 0.3,
        "line_enhancement": 0.2, "sharpness": 1.0, "contrast": 1.0,
        "dithering": False, "palette": "None",
    },
}

# ─── Theme ────────────────────────────────────────────────────────────────────

COLORS = {
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

MONO_FONT = "Courier New"

STYLESHEET = f"""
QMainWindow, QWidget {{
    background: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: "{MONO_FONT}";
    font-size: 12px;
}}
QLabel#title {{
    color: {COLORS['accent']};
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 4px;
}}
QLabel#subtitle {{
    color: {COLORS['muted']};
    font-size: 10px;
    letter-spacing: 3px;
}}
QLabel#section {{
    color: {COLORS['accent3']};
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
}}
QLabel#value {{
    color: {COLORS['accent']};
    font-size: 11px;
    min-width: 36px;
}}
QPushButton#primary {{
    background: {COLORS['accent']};
    color: {COLORS['bg']};
    border: none;
    padding: 10px 24px;
    font-family: "{MONO_FONT}";
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 2px;
}}
QPushButton#primary:hover   {{ background: #00ffaa; }}
QPushButton#primary:pressed {{ background: {COLORS['pixel']}; }}
QPushButton#primary:disabled {{ background: {COLORS['border']}; color: {COLORS['muted']}; }}
QPushButton#ghost {{
    background: transparent;
    color: {COLORS['muted']};
    border: 1px solid {COLORS['border']};
    padding: 6px 16px;
    font-family: "{MONO_FONT}";
    font-size: 11px;
}}
QPushButton#ghost:hover {{ color: {COLORS['text']}; border-color: {COLORS['muted']}; }}
QSlider::groove:horizontal {{ height: 3px; background: {COLORS['border']}; }}
QSlider::handle:horizontal {{
    background: {COLORS['accent']};
    width: 12px; height: 12px;
    margin: -5px 0;
}}
QSlider::sub-page:horizontal {{ background: {COLORS['accent']}; height: 3px; }}
QComboBox {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    color: {COLORS['text']};
    padding: 4px 10px;
    font-family: "{MONO_FONT}";
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    color: {COLORS['text']};
    selection-background-color: {COLORS['accent']};
    selection-color: {COLORS['bg']};
}}
QCheckBox {{ color: {COLORS['text']}; spacing: 8px; }}
QCheckBox::indicator {{
    width: 14px; height: 14px;
    border: 1px solid {COLORS['border']};
    background: {COLORS['surface']};
}}
QCheckBox::indicator:checked {{
    background: {COLORS['accent']};
    border-color: {COLORS['accent']};
}}
QProgressBar {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    height: 4px;
    color: transparent;
}}
QProgressBar::chunk {{ background: {COLORS['accent']}; }}
QScrollBar:vertical {{
    background: {COLORS['surface']};
    width: 6px; border: none;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {COLORS['muted']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""