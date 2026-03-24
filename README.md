# 8-Bitify - Pixel Art Converter

A desktop application for converting images to pixel art using PyQt6.

## Features

- Drag-and-drop image loading
- Multiple preset configurations (Game Boy, NES, Retro VGA, etc.)
- Customizable pixelation parameters
- Real-time preview
- Background processing with progress indication
- Save converted images

## Project Structure

```
8_bitify/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── config/
│   └── constants.py       # Presets, theme constants, and styles
├── core/
│   ├── image_processor.py # Image processing functions
│   └── worker.py          # Background worker thread
└── ui/
    ├── components.py      # Reusable UI components
    └── main_window.py     # Main application window
```

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

### How to Use

1. **Load an image**: Drag and drop an image file onto the drop zone, or click to browse
2. **Select a preset**: Choose from predefined configurations (Game Boy, NES, etc.)
3. **Adjust parameters**: Fine-tune pixel size, colors, detail level, and other settings
4. **Convert**: Click the "CONVERT" button to process the image
5. **Save**: Save the converted pixel art to a file

### Presets

- **Main Character**: Optimized for character sprites
- **Enemy**: Suitable for enemy/NPC sprites
- **Item / Object**: For small objects and items
- **Background**: For background/scenery images
- **Game Boy**: Classic 4-color green palette
- **NES**: 16-color NES-style palette
- **Retro VGA**: 256-color VGA palette
- **Ultra Detail**: High-detail preservation
- **Big Pixel**: Large, chunky pixels

## Development

### Code Organization

The application follows clean code principles:

- **Separation of Concerns**: UI, business logic, and image processing are separated
- **Single Responsibility**: Each module has a clear, focused purpose
- **Reusability**: UI components are modular and reusable
- **Maintainability**: Clear naming, documentation, and consistent structure

### Key Design Decisions

1. **Background Processing**: Image processing runs in a worker thread to keep the UI responsive
2. **Preset System**: Predefined configurations for common use cases
3. **Customizable UI**: Theme constants allow easy styling changes
4. **Error Handling**: Graceful error handling with user feedback

## Dependencies

- **PyQt6**: GUI framework
- **Pillow**: Image processing library

## License

This project is for educational/demonstration purposes.