"""
Image processing functions for pixel art conversion.
"""

from typing import Tuple, Dict
from PIL import Image, ImageEnhance, ImageFilter


def enhance_lines(image: Image.Image, strength: float) -> Image.Image:
    """
    Enhance lines/edges in an image.
    
    Args:
        image: Input PIL Image
        strength: Enhancement strength (0.0 to 1.0)
        
    Returns:
        Enhanced PIL Image
    """
    if strength <= 0:
        return image

    # Detect edges
    edges = image.filter(ImageFilter.FIND_EDGES).convert("L")
    edges = edges.point(lambda x: min(255, int(x * (1 + strength))))

    # Darken image slightly
    factor = 1 - strength * 0.3
    channels = [ch.point(lambda x: int(x * factor)) for ch in image.split()]
    darkened = Image.merge(image.mode, channels)

    # Apply edge mask
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
    """
    Advanced pixelation with multiple enhancement options.
    
    Args:
        image: Input PIL Image
        pixel_size: Size of each pixel block
        colors: Number of colors to reduce to
        dithering: Whether to apply dithering
        detail_level: Detail preservation level (0.0 to 2.0)
        line_enhancement: Line enhancement strength (0.0 to 1.0)
        
    Returns:
        Pixelated PIL Image
    """
    width, height = image.size

    # Determine resize method based on detail level
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

    # Apply line enhancement before resizing if detail is high enough
    if line_enhancement > 0 and detail_level > 0.6:
        image = enhance_lines(image, line_enhancement * 0.5)

    # Resize to smaller dimensions
    small = image.resize((small_w, small_h), resize_method)

    # Apply sharpness based on detail level
    if detail_level > 0.5:
        sharpness = 1.0 + (detail_level - 0.5) * 0.5
        small = ImageEnhance.Sharpness(small).enhance(min(sharpness, 1.8))

    # Color reduction
    if colors < 256:
        dither_mode = Image.Dither.FLOYDSTEINBERG if dithering else Image.Dither.NONE
        small = small.quantize(colors=colors, dither=dither_mode).convert("RGB")

    # Scale back up with nearest neighbor
    result = small.resize((small_w * pixel_size, small_h * pixel_size), Image.Resampling.NEAREST)

    # Apply post-processing enhancements
    if line_enhancement > 0:
        result = enhance_lines(result, line_enhancement * 0.7)

    if detail_level > 0.7:
        result = ImageEnhance.Sharpness(result).enhance(1.1)

    return result


def apply_palette(image: Image.Image, palette: str) -> Image.Image:
    """
    Apply a specific color palette to an image.
    
    Args:
        image: Input PIL Image
        palette: Palette name ("gameboy", "nes", "vga", or "None")
        
    Returns:
        Image with applied palette
    """
    if palette == "gameboy":
        # Game Boy classic green palette
        colors = [(15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)]
        palette_img = Image.new("P", (1, 1))
        palette_img.putpalette([c for color in colors for c in color] * 64)
        return image.convert("L").quantize(colors=4, palette=palette_img).convert("RGB")

    if palette in ("nes", "vga"):
        # NES (16 colors) or VGA (256 colors) palette
        num_colors = 16 if palette == "nes" else 256
        return image.quantize(
            colors=num_colors,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.FLOYDSTEINBERG,
        ).convert("RGB")

    return image


def process_image(source_path: str, params: dict) -> Tuple[Image.Image, Dict]:
    """
    Main image processing pipeline.
    
    Args:
        source_path: Path to source image
        params: Processing parameters dictionary
        
    Returns:
        Tuple of (processed_image, metadata)
    """
    # Load and prepare image
    img = Image.open(source_path)

    if img.mode == "RGBA":
        # Convert RGBA to RGB with white background
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Apply pre-processing enhancements
    contrast = params.get("contrast", 1.0)
    sharpness = params.get("sharpness", 1.0)
    detail = params.get("detail_level", 0.8)

    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if sharpness != 1.0 and detail > 0.5:
        img = ImageEnhance.Sharpness(img).enhance(sharpness)

    # Main pixelation
    result = pixelate_advanced(
        img,
        pixel_size=params.get("size", 4),
        colors=params.get("colors", 32),
        dithering=params.get("dithering", False),
        detail_level=detail,
        line_enhancement=params.get("line_enhancement", 0.5),
    )

    # Apply color palette
    palette = params.get("palette", "None")
    if palette and palette != "None":
        result = apply_palette(result, palette.lower())

    # Apply post-processing enhancements
    if sharpness != 1.0:
        result = ImageEnhance.Sharpness(result).enhance(sharpness)
    if contrast != 1.0:
        result = ImageEnhance.Contrast(result).enhance(contrast)

    # Generate metadata
    meta = {
        "original_size": f"{img.width}x{img.height}",
        "final_size": f"{result.width}x{result.height}",
        "pixel_size": params.get("size", 4),
        "colors": params.get("colors", 32),
        "palette": palette,
    }
    
    return result, meta