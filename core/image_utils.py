"""
Image utility functions for loading, saving, and processing images.
Handles conversion between PIL and Qt image formats.
"""

import os
from PIL import Image
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt


# Supported image formats for loading
SUPPORTED_FORMATS = (
    ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif",
    ".webp", ".gif", ".ico"
)

SAVE_FORMATS = {
    "PNG (*.png)": ("PNG", ".png"),
    "JPEG (*.jpg *.jpeg)": ("JPEG", ".jpg"),
    "BMP (*.bmp)": ("BMP", ".bmp"),
    "TIFF (*.tiff *.tif)": ("TIFF", ".tiff"),
}


def is_supported_image(file_path):
    """Check if a file has a supported image extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in SUPPORTED_FORMATS


def get_image_info(file_path):
    """
    Get information about an image file.
    
    Returns:
        dict with keys: width, height, format, size_bytes, size_str, filename
    """
    try:
        file_size = os.path.getsize(file_path)
        with Image.open(file_path) as img:
            width, height = img.size
            img_format = img.format or "Unknown"

        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"

        return {
            "width": width,
            "height": height,
            "format": img_format,
            "size_bytes": file_size,
            "size_str": size_str,
            "filename": os.path.basename(file_path),
            "path": file_path,
        }
    except Exception as e:
        return None


def pil_to_qpixmap(pil_image, max_size=None):
    """
    Convert a PIL Image to QPixmap.
    
    Args:
        pil_image: PIL Image object
        max_size: Optional tuple (max_width, max_height) to scale down for display
    
    Returns:
        QPixmap object
    """
    # Convert PIL to QImage
    if pil_image.mode == "RGB":
        data = pil_image.tobytes("raw", "RGB")
        qimage = QImage(data, pil_image.width, pil_image.height,
                        3 * pil_image.width, QImage.Format_RGB888)
    elif pil_image.mode == "RGBA":
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(data, pil_image.width, pil_image.height,
                        4 * pil_image.width, QImage.Format_RGBA8888)
    else:
        # Convert to RGB for unsupported modes
        pil_image = pil_image.convert("RGB")
        data = pil_image.tobytes("raw", "RGB")
        qimage = QImage(data, pil_image.width, pil_image.height,
                        3 * pil_image.width, QImage.Format_RGB888)

    pixmap = QPixmap.fromImage(qimage)

    if max_size:
        pixmap = pixmap.scaled(
            max_size[0], max_size[1],
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

    return pixmap


def load_image_as_pixmap(file_path, max_size=None):
    """
    Load an image file and return it as QPixmap.
    
    Args:
        file_path: Path to the image file
        max_size: Optional tuple (max_width, max_height)
    
    Returns:
        QPixmap or None on error
    """
    try:
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            return None
        if max_size:
            pixmap = pixmap.scaled(
                max_size[0], max_size[1],
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        return pixmap
    except Exception:
        return None


def save_pil_image(pil_image, file_path, format_name="PNG", quality=95):
    """
    Save a PIL image to disk.
    
    Args:
        pil_image: PIL Image object
        file_path: Output file path
        format_name: Image format (PNG, JPEG, BMP, TIFF)
        quality: JPEG quality (1-100), only used for JPEG format
    """
    save_kwargs = {"format": format_name}
    if format_name == "JPEG":
        save_kwargs["quality"] = quality
        # Ensure RGB mode for JPEG
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

    pil_image.save(file_path, **save_kwargs)


def generate_output_filename(input_path, mode_label, output_dir=None):
    """
    Generate output filename with mode suffix.
    Example: photo.jpg → photo_4K.jpg
    
    Args:
        input_path: Original input file path
        mode_label: Mode label string (e.g., "4K")
        output_dir: Optional output directory. If None, uses same dir as input.
    
    Returns:
        Full output file path
    """
    name, ext = os.path.splitext(os.path.basename(input_path))
    output_name = f"{name}_{mode_label}{ext}"

    if output_dir:
        return os.path.join(output_dir, output_name)
    else:
        return os.path.join(os.path.dirname(input_path), output_name)


def get_file_filter_string():
    """Get the file filter string for QFileDialog."""
    return (
        "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.webp);;"
        "PNG (*.png);;"
        "JPEG (*.jpg *.jpeg);;"
        "BMP (*.bmp);;"
        "TIFF (*.tiff *.tif);;"
        "WebP (*.webp);;"
        "All Files (*.*)"
    )


def get_save_filter_string():
    """Get the save file filter string for QFileDialog."""
    return (
        "PNG (*.png);;"
        "JPEG (*.jpg *.jpeg);;"
        "BMP (*.bmp);;"
        "TIFF (*.tiff *.tif)"
    )
