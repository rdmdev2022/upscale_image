"""
Main application window with Single and Batch upscale tabs.
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QComboBox, QLabel, QProgressBar, QFileDialog,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QSplitter, QSpacerItem, QSizePolicy, QMessageBox,
    QSlider, QApplication
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap

from core.upscaler import UpscaleMode, UpscaleWorker, BatchUpscaleWorker, get_current_engine
from core.image_utils import (
    get_image_info, pil_to_qpixmap, load_image_as_pixmap,
    save_pil_image, get_file_filter_string, get_save_filter_string,
    SAVE_FORMATS
)
from ui.widgets import DropZoneWidget, ImagePreviewWidget, BeforeAfterWidget


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("✦ Image Upscaler Pro")
        self.setMinimumSize(1100, 750)
        self.resize(1280, 850)

        # State
        self.current_image_path = None
        self.current_result_pil = None
        self.upscale_worker = None
        self.batch_worker = None
        self.batch_files = []

        self._setup_ui()

    def _setup_ui(self):
        """Build the entire UI."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(12)

        # ── Header ──
        header = self._create_header()
        main_layout.addLayout(header)

        # ── Tab Widget ──
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_single_tab(), "🖼  Single Upscale")
        self.tabs.addTab(self._create_batch_tab(), "📁  Batch Processing")
        main_layout.addWidget(self.tabs)

    # ─────────────────────────────────────────────
    #  HEADER
    # ─────────────────────────────────────────────
    def _create_header(self):
        layout = QHBoxLayout()

        title_block = QVBoxLayout()
        title = QLabel("Image Upscaler Pro")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Upscale your photos to 2K, 4K, or 8K resolution with one click")
        subtitle.setObjectName("subtitleLabel")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        title_block.setSpacing(2)

        layout.addLayout(title_block)
        layout.addStretch()

        # Engine status badge
        engine_name = get_current_engine()
        self.lbl_engine = QLabel(f"🤖 Engine: {engine_name}")
        if "Real-ESRGAN" in engine_name:
            self.lbl_engine.setStyleSheet(
                "color: #00b894; font-weight: 600; font-size: 12px;"
                "background-color: rgba(0,184,148,0.12); padding: 6px 14px;"
                "border-radius: 6px; border: 1px solid rgba(0,184,148,0.3);"
            )
        else:
            self.lbl_engine.setStyleSheet(
                "color: #e67e22; font-weight: 600; font-size: 12px;"
                "background-color: rgba(230,126,34,0.12); padding: 6px 14px;"
                "border-radius: 6px; border: 1px solid rgba(230,126,34,0.3);"
            )
        layout.addWidget(self.lbl_engine)

        # Exit button
        self.btn_exit = QPushButton("✕  Exit")
        self.btn_exit.setObjectName("btnDanger")
        self.btn_exit.setMaximumWidth(100)
        self.btn_exit.clicked.connect(self.close)
        layout.addWidget(self.btn_exit)

        return layout

    # ─────────────────────────────────────────────
    #  SINGLE UPSCALE TAB
    # ─────────────────────────────────────────────
    def _create_single_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # ── Top Controls ──
        controls = QHBoxLayout()

        # Drop zone
        self.single_drop = DropZoneWidget(
            "Drop an image here\nor click Browse",
            accept_multiple=False
        )
        self.single_drop.files_dropped.connect(self._on_single_file_dropped)
        self.single_drop.setMaximumHeight(140)

        # Right controls panel
        ctrl_panel = QVBoxLayout()
        ctrl_panel.setSpacing(8)

        # Browse button
        self.btn_browse = QPushButton("📂  Browse Image")
        self.btn_browse.clicked.connect(self._browse_single)
        ctrl_panel.addWidget(self.btn_browse)

        # File info
        self.lbl_file_info = QLabel("No file selected")
        self.lbl_file_info.setObjectName("infoLabel")
        self.lbl_file_info.setWordWrap(True)
        ctrl_panel.addWidget(self.lbl_file_info)

        # Mode selector
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Upscale Mode:")
        mode_label.setObjectName("sectionLabel")
        self.combo_mode = QComboBox()
        for mode in UpscaleMode:
            self.combo_mode.addItem(
                f"{mode.label}  ({mode.target_width}×{mode.target_height})",
                mode
            )
        self.combo_mode.setCurrentIndex(1)  # Default 4K
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.combo_mode)
        mode_layout.addStretch()
        ctrl_panel.addLayout(mode_layout)

        # Resolution info
        self.lbl_resolution = QLabel("")
        self.lbl_resolution.setObjectName("infoLabel")
        ctrl_panel.addWidget(self.lbl_resolution)

        ctrl_panel.addStretch()

        # Upscale button
        self.btn_upscale = QPushButton("⚡  Upscale Now")
        self.btn_upscale.setEnabled(False)
        self.btn_upscale.setMinimumHeight(44)
        self.btn_upscale.clicked.connect(self._start_single_upscale)
        ctrl_panel.addWidget(self.btn_upscale)

        controls.addWidget(self.single_drop, 3)
        ctrl_widget = QWidget()
        ctrl_widget.setLayout(ctrl_panel)
        controls.addWidget(ctrl_widget, 2)
        layout.addLayout(controls)

        # ── Progress Bar ──
        progress_layout = QHBoxLayout()
        self.single_progress = QProgressBar()
        self.single_progress.setValue(0)
        self.single_progress.setVisible(False)
        self.lbl_progress_status = QLabel("")
        self.lbl_progress_status.setObjectName("infoLabel")
        progress_layout.addWidget(self.single_progress)
        progress_layout.addWidget(self.lbl_progress_status)
        layout.addLayout(progress_layout)

        # ── Before / After Preview ──
        self.before_after = BeforeAfterWidget()
        layout.addWidget(self.before_after, 1)

        # ── Save Button ──
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.btn_save = QPushButton("💾  Save Result")
        self.btn_save.setObjectName("btnSuccess")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._save_single_result)
        save_layout.addWidget(self.btn_save)
        layout.addLayout(save_layout)

        return tab

    # ─────────────────────────────────────────────
    #  BATCH PROCESSING TAB
    # ─────────────────────────────────────────────
    def _create_batch_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # ── Top: File selection ──
        top_row = QHBoxLayout()

        # Batch drop zone
        self.batch_drop = DropZoneWidget(
            "Drop multiple images or a folder here",
            accept_multiple=True
        )
        self.batch_drop.files_dropped.connect(self._on_batch_files_dropped)
        self.batch_drop.setMaximumHeight(120)

        # Buttons panel
        btn_panel = QVBoxLayout()
        self.btn_add_files = QPushButton("📂  Add Files")
        self.btn_add_files.clicked.connect(self._browse_batch_files)
        self.btn_add_folder = QPushButton("📁  Add Folder")
        self.btn_add_folder.setObjectName("btnSecondary")
        self.btn_add_folder.clicked.connect(self._browse_batch_folder)
        self.btn_clear_batch = QPushButton("🗑  Clear List")
        self.btn_clear_batch.setObjectName("btnDanger")
        self.btn_clear_batch.clicked.connect(self._clear_batch_list)

        btn_panel.addWidget(self.btn_add_files)
        btn_panel.addWidget(self.btn_add_folder)
        btn_panel.addWidget(self.btn_clear_batch)
        btn_panel.addStretch()

        top_row.addWidget(self.batch_drop, 3)
        btn_widget = QWidget()
        btn_widget.setLayout(btn_panel)
        top_row.addWidget(btn_widget, 1)
        layout.addLayout(top_row)

        # ── Settings Row ──
        settings_row = QHBoxLayout()

        # Mode selector
        mode_lbl = QLabel("Mode:")
        mode_lbl.setObjectName("sectionLabel")
        self.batch_combo_mode = QComboBox()
        for mode in UpscaleMode:
            self.batch_combo_mode.addItem(
                f"{mode.label}  ({mode.target_width}×{mode.target_height})",
                mode
            )
        self.batch_combo_mode.setCurrentIndex(1)

        # Output folder
        out_lbl = QLabel("Output Folder:")
        out_lbl.setObjectName("sectionLabel")
        self.lbl_output_dir = QLabel("Same as source")
        self.lbl_output_dir.setObjectName("infoLabel")
        self.btn_output_dir = QPushButton("📂  Choose")
        self.btn_output_dir.setObjectName("btnSecondary")
        self.btn_output_dir.setMaximumWidth(120)
        self.btn_output_dir.clicked.connect(self._choose_output_dir)

        settings_row.addWidget(mode_lbl)
        settings_row.addWidget(self.batch_combo_mode)
        settings_row.addSpacing(20)
        settings_row.addWidget(out_lbl)
        settings_row.addWidget(self.lbl_output_dir, 1)
        settings_row.addWidget(self.btn_output_dir)

        layout.addLayout(settings_row)

        # ── File Queue Table ──
        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(4)
        self.batch_table.setHorizontalHeaderLabels(["Filename", "Size", "Status", "Message"])
        self.batch_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.batch_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.batch_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.batch_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.batch_table.setAlternatingRowColors(True)
        self.batch_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.batch_table.verticalHeader().setVisible(False)
        layout.addWidget(self.batch_table, 1)

        # ── Progress ──
        progress_row = QHBoxLayout()
        self.batch_progress = QProgressBar()
        self.batch_progress.setValue(0)
        self.lbl_batch_status = QLabel("Ready")
        self.lbl_batch_status.setObjectName("infoLabel")
        progress_row.addWidget(self.batch_progress, 1)
        progress_row.addWidget(self.lbl_batch_status)
        layout.addLayout(progress_row)

        # ── Control Buttons ──
        ctrl_row = QHBoxLayout()
        ctrl_row.addStretch()

        self.btn_batch_start = QPushButton("▶  Start Batch")
        self.btn_batch_start.setObjectName("btnSuccess")
        self.btn_batch_start.setEnabled(False)
        self.btn_batch_start.clicked.connect(self._start_batch)

        self.btn_batch_pause = QPushButton("⏸  Pause")
        self.btn_batch_pause.setObjectName("btnSecondary")
        self.btn_batch_pause.setEnabled(False)
        self.btn_batch_pause.clicked.connect(self._pause_batch)

        self.btn_batch_cancel = QPushButton("⏹  Cancel")
        self.btn_batch_cancel.setObjectName("btnDanger")
        self.btn_batch_cancel.setEnabled(False)
        self.btn_batch_cancel.clicked.connect(self._cancel_batch)

        ctrl_row.addWidget(self.btn_batch_start)
        ctrl_row.addWidget(self.btn_batch_pause)
        ctrl_row.addWidget(self.btn_batch_cancel)
        layout.addLayout(ctrl_row)

        # ── Log ──
        self.batch_log = QTextEdit()
        self.batch_log.setReadOnly(True)
        self.batch_log.setMaximumHeight(120)
        self.batch_log.setPlaceholderText("Batch processing log...")
        layout.addWidget(self.batch_log)

        # State
        self.output_dir = None

        return tab

    # ═════════════════════════════════════════════
    #  SINGLE TAB HANDLERS
    # ═════════════════════════════════════════════
    def _browse_single(self):
        """Open file dialog to select a single image."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            get_file_filter_string()
        )
        if path:
            self._load_single_image(path)

    def _on_single_file_dropped(self, files):
        """Handle file dropped in single mode."""
        if files:
            self._load_single_image(files[0])

    def _load_single_image(self, path):
        """Load and display a single image."""
        self.current_image_path = path
        self.current_result_pil = None
        self.btn_save.setEnabled(False)

        # Get image info
        info = get_image_info(path)
        if not info:
            self.lbl_file_info.setText("Error: Could not load image")
            return

        self.lbl_file_info.setText(
            f"📄 {info['filename']}\n"
            f"📐 {info['width']}×{info['height']}  |  {info['format']}  |  {info['size_str']}"
        )

        # Show original in before panel
        pixmap = load_image_as_pixmap(path)
        if pixmap:
            self.before_after.set_before(
                pixmap,
                f"{info['width']}×{info['height']}  ({info['size_str']})"
            )
            self.before_after.set_after(None, "")

        # Update resolution info
        self._update_resolution_info()
        self.btn_upscale.setEnabled(True)
        self.single_progress.setValue(0)

    def _update_resolution_info(self):
        """Update the target resolution label."""
        if not self.current_image_path:
            return
        mode = self.combo_mode.currentData()
        info = get_image_info(self.current_image_path)
        if info and mode:
            from core.upscaler import calculate_target_size
            tw, th = calculate_target_size(info["width"], info["height"], mode)
            self.lbl_resolution.setText(
                f"📐 {info['width']}×{info['height']}  →  {tw}×{th}  ({mode.label})"
            )

    def _start_single_upscale(self):
        """Start the upscale process in a background thread."""
        if not self.current_image_path:
            return

        mode = self.combo_mode.currentData()

        # UI feedback
        self.btn_upscale.setEnabled(False)
        self.btn_browse.setEnabled(False)
        self.single_progress.setVisible(True)
        self.single_progress.setValue(0)
        engine = get_current_engine()
        self.lbl_progress_status.setText(f"Upscaling with {engine}...")

        # Create and start worker
        self.upscale_worker = UpscaleWorker(self.current_image_path, mode)
        self.upscale_worker.progress.connect(self._on_single_progress)
        self.upscale_worker.finished.connect(self._on_single_finished)
        self.upscale_worker.error.connect(self._on_single_error)
        self.upscale_worker.start()

    def _on_single_progress(self, value):
        """Update progress bar."""
        self.single_progress.setValue(value)

    def _on_single_finished(self, pil_image):
        """Handle upscale completion."""
        self.current_result_pil = pil_image
        self.single_progress.setValue(100)
        engine = get_current_engine()
        self.lbl_progress_status.setText(f"✅ Done! ({engine})")

        # Show result in after panel
        pixmap = pil_to_qpixmap(pil_image)
        if pixmap:
            self.before_after.set_after(
                pixmap,
                f"{pil_image.width}×{pil_image.height}"
            )

        # Re-enable controls
        self.btn_upscale.setEnabled(True)
        self.btn_browse.setEnabled(True)
        self.btn_save.setEnabled(True)

    def _on_single_error(self, error_msg):
        """Handle upscale error."""
        self.lbl_progress_status.setText(f"❌ Error: {error_msg}")
        self.single_progress.setValue(0)
        self.btn_upscale.setEnabled(True)
        self.btn_browse.setEnabled(True)
        QMessageBox.critical(self, "Upscale Error", f"Failed to upscale image:\n{error_msg}")

    def _save_single_result(self):
        """Save the upscaled result."""
        if not self.current_result_pil:
            return

        filter_str = get_save_filter_string()
        path, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Upscaled Image", "", filter_str
        )

        if path:
            # Determine format from selected filter
            format_name = "PNG"
            for label, (fmt, ext) in SAVE_FORMATS.items():
                if label == selected_filter:
                    format_name = fmt
                    break

            try:
                save_pil_image(self.current_result_pil, path, format_name)
                self.lbl_progress_status.setText(f"💾 Saved: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save:\n{e}")

    # ═════════════════════════════════════════════
    #  BATCH TAB HANDLERS
    # ═════════════════════════════════════════════
    def _browse_batch_files(self):
        """Open file dialog to select multiple images."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "",
            get_file_filter_string()
        )
        if files:
            self._add_batch_files(files)

    def _browse_batch_folder(self):
        """Select a folder and add all images from it."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            from core.image_utils import is_supported_image
            files = [
                os.path.join(folder, f) for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f)) and is_supported_image(f)
            ]
            if files:
                self._add_batch_files(sorted(files))
            else:
                QMessageBox.information(
                    self, "No Images",
                    "No supported image files found in the selected folder."
                )

    def _on_batch_files_dropped(self, files):
        """Handle files dropped in batch mode."""
        self._add_batch_files(files)

    def _add_batch_files(self, files):
        """Add files to the batch queue table."""
        for f in files:
            if f not in self.batch_files:
                self.batch_files.append(f)
                row = self.batch_table.rowCount()
                self.batch_table.insertRow(row)

                info = get_image_info(f)
                filename = os.path.basename(f)
                size_str = info["size_str"] if info else "?"
                res_str = f"{info['width']}×{info['height']}" if info else "?"

                self.batch_table.setItem(row, 0, QTableWidgetItem(filename))
                self.batch_table.setItem(row, 1, QTableWidgetItem(f"{res_str}  ({size_str})"))
                status_item = QTableWidgetItem("Pending")
                status_item.setForeground(QColor(136, 136, 160))
                self.batch_table.setItem(row, 2, status_item)
                self.batch_table.setItem(row, 3, QTableWidgetItem(""))

        self.btn_batch_start.setEnabled(len(self.batch_files) > 0)
        self.lbl_batch_status.setText(f"{len(self.batch_files)} files in queue")

    def _clear_batch_list(self):
        """Clear the batch file list."""
        self.batch_files.clear()
        self.batch_table.setRowCount(0)
        self.batch_progress.setValue(0)
        self.btn_batch_start.setEnabled(False)
        self.lbl_batch_status.setText("Ready")
        self.batch_log.clear()

    def _choose_output_dir(self):
        """Choose output directory for batch results."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir = folder
            # Show shortened path
            display = folder if len(folder) < 50 else f"...{folder[-47:]}"
            self.lbl_output_dir.setText(display)
            self.lbl_output_dir.setToolTip(folder)

    def _start_batch(self):
        """Start batch processing."""
        if not self.batch_files:
            return

        mode = self.batch_combo_mode.currentData()
        output_dir = self.output_dir

        if not output_dir:
            # Use each file's own directory
            output_dir = os.path.dirname(self.batch_files[0])

        # Ensure output dir exists
        os.makedirs(output_dir, exist_ok=True)

        # Reset UI
        self.batch_progress.setValue(0)
        self.batch_log.clear()
        self._set_batch_running(True)

        # Reset table statuses
        for row in range(self.batch_table.rowCount()):
            status_item = self.batch_table.item(row, 2)
            if status_item:
                status_item.setText("Pending")
                status_item.setForeground(QColor(136, 136, 160))
            msg_item = self.batch_table.item(row, 3)
            if msg_item:
                msg_item.setText("")

        engine = get_current_engine()
        self._log("🚀 Batch processing started")
        self._log(f"   Engine: {engine}")
        self._log(f"   Mode: {mode.label} ({mode.target_width}×{mode.target_height})")
        self._log(f"   Files: {len(self.batch_files)}")
        self._log(f"   Output: {output_dir}")
        self._log("─" * 40)

        # Create and start batch worker
        self.batch_worker = BatchUpscaleWorker(
            self.batch_files, mode, output_dir
        )
        self.batch_worker.file_started.connect(self._on_batch_file_started)
        self.batch_worker.file_progress.connect(self._on_batch_file_progress)
        self.batch_worker.file_completed.connect(self._on_batch_file_completed)
        self.batch_worker.overall_progress.connect(self._on_batch_overall_progress)
        self.batch_worker.batch_finished.connect(self._on_batch_finished)
        self.batch_worker.start()

    def _pause_batch(self):
        """Toggle pause on batch processing."""
        if self.batch_worker:
            self.batch_worker.pause()
            if self.batch_worker.is_paused():
                self.btn_batch_pause.setText("▶  Resume")
                self.lbl_batch_status.setText("⏸ Paused")
                self._log("⏸ Batch paused")
            else:
                self.btn_batch_pause.setText("⏸  Pause")
                self.lbl_batch_status.setText("Processing...")
                self._log("▶ Batch resumed")

    def _cancel_batch(self):
        """Cancel batch processing."""
        if self.batch_worker:
            self.batch_worker.cancel()
            self._log("⏹ Batch cancelled by user")
            self._set_batch_running(False)
            self.lbl_batch_status.setText("Cancelled")

    def _on_batch_file_started(self, index, filename):
        """Update table when a file starts processing."""
        if index < self.batch_table.rowCount():
            status_item = self.batch_table.item(index, 2)
            if status_item:
                status_item.setText("Processing...")
                status_item.setForeground(QColor(167, 139, 250))
            self.batch_table.scrollToItem(self.batch_table.item(index, 0))
        self._log(f"📄 Processing: {filename}")

    def _on_batch_file_progress(self, index, progress):
        """Update individual file progress (shown in status column)."""
        if index < self.batch_table.rowCount():
            status_item = self.batch_table.item(index, 2)
            if status_item:
                status_item.setText(f"{progress}%")

    def _on_batch_file_completed(self, index, filename, success, message):
        """Update table when a file completes."""
        if index < self.batch_table.rowCount():
            status_item = self.batch_table.item(index, 2)
            msg_item = self.batch_table.item(index, 3)
            if success:
                if status_item:
                    status_item.setText("✅ Done")
                    status_item.setForeground(QColor(0, 184, 148))
                self._log(f"   ✅ {filename} → {message}")
            else:
                if status_item:
                    status_item.setText("❌ Failed")
                    status_item.setForeground(QColor(231, 76, 60))
                self._log(f"   ❌ {filename} — {message}")
            if msg_item:
                msg_item.setText(message)

    def _on_batch_overall_progress(self, value):
        """Update overall progress bar."""
        self.batch_progress.setValue(value)
        self.lbl_batch_status.setText(f"Processing... {value}%")

    def _on_batch_finished(self, results):
        """Handle batch completion."""
        self._set_batch_running(False)
        self.batch_progress.setValue(100)

        success = sum(1 for _, s, _ in results if s)
        failed = sum(1 for _, s, _ in results if not s)

        self._log("─" * 40)
        self._log(f"🏁 Batch finished: {success} succeeded, {failed} failed")
        self.lbl_batch_status.setText(f"Done — {success}✅  {failed}❌")

        if failed == 0:
            QMessageBox.information(
                self, "Batch Complete",
                f"All {success} images upscaled successfully!"
            )
        else:
            QMessageBox.warning(
                self, "Batch Complete",
                f"Batch finished with {failed} error(s).\n"
                f"{success} images upscaled successfully."
            )

    def _set_batch_running(self, running):
        """Enable/disable batch controls based on running state."""
        self.btn_batch_start.setEnabled(not running)
        self.btn_add_files.setEnabled(not running)
        self.btn_add_folder.setEnabled(not running)
        self.btn_clear_batch.setEnabled(not running)
        self.btn_output_dir.setEnabled(not running)
        self.batch_combo_mode.setEnabled(not running)
        self.batch_drop.setAcceptDrops(not running)

        self.btn_batch_pause.setEnabled(running)
        self.btn_batch_cancel.setEnabled(running)
        self.btn_batch_pause.setText("⏸  Pause")

    def _log(self, text):
        """Append text to the batch log."""
        self.batch_log.append(text)
        # Auto-scroll
        scrollbar = self.batch_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


# Need QColor import at module level for table colors
from PyQt5.QtGui import QColor
