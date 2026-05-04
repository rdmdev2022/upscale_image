"""
Custom widgets for the upscale application.
Includes: DropZoneWidget, ImagePreviewWidget, BeforeAfterWidget
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QScrollArea, QSplitter, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QMimeData
from PyQt5.QtGui import (
    QPixmap, QPainter, QColor, QPen, QFont,
    QDragEnterEvent, QDropEvent, QPaintEvent
)

from core.image_utils import is_supported_image


class DropZoneWidget(QWidget):
    """
    Drag & drop zone widget with visual feedback.
    Emits files_dropped signal with list of file paths.
    """
    files_dropped = pyqtSignal(list)

    def __init__(self, text="Drop images here\nor click Browse", 
                 accept_multiple=False, parent=None):
        super().__init__(parent)
        self.accept_multiple = accept_multiple
        self.text = text
        self._is_hovering = False
        self.setAcceptDrops(True)
        self.setMinimumHeight(160)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, event: QPaintEvent):
        """Draw the drop zone with dashed border."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        if self._is_hovering:
            bg_color = QColor(108, 92, 231, 30)
            border_color = QColor(167, 139, 250)
        else:
            bg_color = QColor(22, 22, 30, 180)
            border_color = QColor(60, 60, 90)

        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 12, 12)

        # Dashed border
        pen = QPen(border_color, 2, Qt.DashLine)
        pen.setDashPattern([8, 6])
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(4, 4, -4, -4), 10, 10)

        # Icon (upload arrow)
        center_x = self.width() // 2
        center_y = self.height() // 2 - 20

        icon_color = QColor(167, 139, 250) if self._is_hovering else QColor(100, 100, 140)
        pen = QPen(icon_color, 3, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)

        # Arrow up
        painter.drawLine(center_x, center_y - 16, center_x, center_y + 10)
        painter.drawLine(center_x - 10, center_y - 6, center_x, center_y - 16)
        painter.drawLine(center_x + 10, center_y - 6, center_x, center_y - 16)

        # Tray
        painter.drawLine(center_x - 18, center_y + 10, center_x - 18, center_y + 18)
        painter.drawLine(center_x + 18, center_y + 10, center_x + 18, center_y + 18)
        painter.drawLine(center_x - 18, center_y + 18, center_x + 18, center_y + 18)

        # Text
        text_color = QColor(180, 180, 200) if self._is_hovering else QColor(120, 120, 150)
        painter.setPen(text_color)
        font = QFont("Segoe UI", 11)
        painter.setFont(font)

        text_rect = self.rect().adjusted(0, 30, 0, 0)
        painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignCenter, self.text)

        painter.end()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter - check if files are images."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            has_image = any(
                is_supported_image(url.toLocalFile()) 
                for url in urls if url.isLocalFile()
            )
            if has_image:
                self._is_hovering = True
                self.update()
                event.acceptProposedAction()
                return
        event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave."""
        self._is_hovering = False
        self.update()

    def dropEvent(self, event: QDropEvent):
        """Handle drop - emit file paths."""
        self._is_hovering = False
        self.update()

        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if os.path.isfile(path) and is_supported_image(path):
                    files.append(path)
                elif os.path.isdir(path):
                    # Scan directory for images
                    for f in os.listdir(path):
                        full = os.path.join(path, f)
                        if os.path.isfile(full) and is_supported_image(full):
                            files.append(full)

        if files:
            if not self.accept_multiple:
                files = files[:1]
            self.files_dropped.emit(files)


class ImagePreviewWidget(QWidget):
    """
    Image preview widget with zoom support (mouse wheel).
    Displays a QPixmap with smooth scaling.
    """

    def __init__(self, placeholder_text="No image loaded", parent=None):
        super().__init__(parent)
        self.placeholder_text = placeholder_text
        self._pixmap = None
        self._zoom = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 5.0
        self._offset_x = 0
        self._offset_y = 0
        self._drag_start = None

        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)

    def set_pixmap(self, pixmap):
        """Set the image to display."""
        self._pixmap = pixmap
        self._zoom = 1.0
        self._offset_x = 0
        self._offset_y = 0
        if pixmap:
            # Auto-fit the image
            self._auto_fit()
        self.update()

    def clear(self):
        """Clear the preview."""
        self._pixmap = None
        self._zoom = 1.0
        self.update()

    def _auto_fit(self):
        """Auto-fit the image to the widget size."""
        if not self._pixmap:
            return
        w_ratio = (self.width() - 20) / self._pixmap.width()
        h_ratio = (self.height() - 20) / self._pixmap.height()
        self._zoom = min(w_ratio, h_ratio, 1.0)

    def paintEvent(self, event):
        """Paint the image or placeholder."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Background
        painter.setBrush(QColor(14, 14, 20))
        painter.setPen(QPen(QColor(42, 42, 58), 1))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)

        if self._pixmap:
            # Calculate display size
            display_w = int(self._pixmap.width() * self._zoom)
            display_h = int(self._pixmap.height() * self._zoom)

            # Center the image
            x = (self.width() - display_w) // 2 + self._offset_x
            y = (self.height() - display_h) // 2 + self._offset_y

            # Draw scaled pixmap
            scaled = self._pixmap.scaled(
                display_w, display_h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            painter.drawPixmap(x, y, scaled)

            # Zoom info
            painter.setPen(QColor(120, 120, 160))
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            painter.drawText(10, self.height() - 10, f"{int(self._zoom * 100)}%")
        else:
            # Placeholder
            painter.setPen(QColor(80, 80, 110))
            font = QFont("Segoe UI", 12)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, self.placeholder_text)

        painter.end()

    def wheelEvent(self, event):
        """Handle mouse wheel for zoom."""
        if not self._pixmap:
            return

        delta = event.angleDelta().y()
        factor = 1.15 if delta > 0 else 0.87

        new_zoom = self._zoom * factor
        new_zoom = max(self._min_zoom, min(self._max_zoom, new_zoom))
        self._zoom = new_zoom
        self.update()

    def mousePressEvent(self, event):
        """Start drag to pan."""
        if event.button() == Qt.LeftButton and self._pixmap:
            self._drag_start = event.pos()

    def mouseMoveEvent(self, event):
        """Handle panning."""
        if self._drag_start and self._pixmap:
            dx = event.pos().x() - self._drag_start.x()
            dy = event.pos().y() - self._drag_start.y()
            self._offset_x += dx
            self._offset_y += dy
            self._drag_start = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """End drag."""
        self._drag_start = None

    def resizeEvent(self, event):
        """Re-fit image on resize."""
        if self._pixmap and self._offset_x == 0 and self._offset_y == 0:
            self._auto_fit()
        super().resizeEvent(event)


class BeforeAfterWidget(QWidget):
    """
    Side-by-side before/after comparison widget.
    Shows original and upscaled images next to each other.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Before panel
        before_container = QVBoxLayout()
        before_label = QLabel("ORIGINAL")
        before_label.setObjectName("sectionLabel")
        before_label.setAlignment(Qt.AlignCenter)
        self.before_preview = ImagePreviewWidget("Original image")
        before_container.addWidget(before_label)
        before_container.addWidget(self.before_preview)
        self.before_info = QLabel("")
        self.before_info.setObjectName("infoLabel")
        self.before_info.setAlignment(Qt.AlignCenter)
        before_container.addWidget(self.before_info)

        # After panel
        after_container = QVBoxLayout()
        after_label = QLabel("UPSCALED")
        after_label.setObjectName("sectionLabel")
        after_label.setAlignment(Qt.AlignCenter)
        self.after_preview = ImagePreviewWidget("Upscaled result")
        after_container.addWidget(after_label)
        after_container.addWidget(self.after_preview)
        self.after_info = QLabel("")
        self.after_info.setObjectName("infoLabel")
        self.after_info.setAlignment(Qt.AlignCenter)
        after_container.addWidget(self.after_info)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("color: #3a3a5a;")

        before_widget = QWidget()
        before_widget.setLayout(before_container)
        after_widget = QWidget()
        after_widget.setLayout(after_container)

        layout.addWidget(before_widget)
        layout.addWidget(separator)
        layout.addWidget(after_widget)

    def set_before(self, pixmap, info_text=""):
        """Set the 'before' image."""
        self.before_preview.set_pixmap(pixmap)
        self.before_info.setText(info_text)

    def set_after(self, pixmap, info_text=""):
        """Set the 'after' image."""
        self.after_preview.set_pixmap(pixmap)
        self.after_info.setText(info_text)

    def clear_all(self):
        """Clear both previews."""
        self.before_preview.clear()
        self.after_preview.clear()
        self.before_info.setText("")
        self.after_info.setText("")
