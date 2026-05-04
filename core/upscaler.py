"""
Upscaler module - Core logic for image upscaling with QThread workers.
Supports Real-ESRGAN AI upscaling (primary) and Pillow fallback.
Supports single image and batch processing with progress reporting.
"""

import os
import sys
import time
import subprocess
import tempfile
import shutil
from enum import Enum
from PIL import Image, ImageFilter
from PyQt5.QtCore import QThread, pyqtSignal


class UpscaleMode(Enum):
    """Available upscale resolution modes."""
    MODE_2K = ("2K", 2560, 1440)
    MODE_4K = ("4K", 3840, 2160)
    MODE_8K = ("8K", 7680, 4320)

    def __init__(self, label, width, height):
        self.label = label
        self.target_width = width
        self.target_height = height

    @staticmethod
    def from_label(label):
        """Get UpscaleMode from its label string."""
        for mode in UpscaleMode:
            if mode.label == label:
                return mode
        raise ValueError(f"Unknown mode: {label}")


# ─────────────────────────────────────────────────
#  Real-ESRGAN AI Engine
# ─────────────────────────────────────────────────

def _get_realesrgan_exe():
    """Find the realesrgan-ncnn-vulkan executable."""
    # Look in tools/ directory relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exe_path = os.path.join(
        project_root, "tools", "realesrgan-ncnn-vulkan",
        "realesrgan-ncnn-vulkan.exe"
    )
    if os.path.isfile(exe_path):
        return exe_path
    return None


def is_realesrgan_available():
    """Check if Real-ESRGAN ncnn-vulkan is available."""
    return _get_realesrgan_exe() is not None


def _get_realesrgan_scale_for_mode(original_w, original_h, mode):
    """
    Determine the best Real-ESRGAN scale factor (2 or 4) for the target mode.
    Real-ESRGAN ncnn-vulkan supports scale factors: 2, 3, 4.
    We'll use 4x as default since it gives the best quality.
    """
    target_w, target_h = calculate_target_size(original_w, original_h, mode)
    scale_x = target_w / original_w
    scale_y = target_h / original_h
    scale = max(scale_x, scale_y)

    if scale <= 2.0:
        return 4  # Still use 4x for better quality, resize down after
    elif scale <= 3.0:
        return 4
    else:
        return 4  # Always 4x for best quality, can chain if needed



def upscale_with_realesrgan(image_path, mode, progress_callback=None):
    """
    Upscale an image using Real-ESRGAN AI model.
    This produces dramatically better results than traditional interpolation.
    
    The process:
    1. Run realesrgan-ncnn-vulkan.exe with 4x scale (AI super-resolution)
    2. If target resolution needs more than 4x, chain multiple passes
    3. Final resize to exact target dimensions with LANCZOS
    
    Args:
        image_path: Path to the input image
        mode: UpscaleMode enum value
        progress_callback: Optional callback function(int) for progress 0-100
    
    Returns:
        PIL.Image object of the upscaled image
    """
    exe_path = _get_realesrgan_exe()
    if not exe_path:
        raise RuntimeError("Real-ESRGAN executable not found in tools/ directory")

    if progress_callback:
        progress_callback(2)

    # Load original to get dimensions
    img = Image.open(image_path)
    img = img.convert("RGB")
    original_w, original_h = img.size
    img.close()

    # Calculate target size
    target_w, target_h = calculate_target_size(original_w, original_h, mode)
    
    # Determine how many 4x passes we need
    scale_needed = max(target_w / original_w, target_h / original_h)
    
    if progress_callback:
        progress_callback(5)

    # Create temp directory for processing
    temp_dir = tempfile.mkdtemp(prefix="upscaler_")
    
    try:
        # Copy input to temp dir (Real-ESRGAN needs clean paths)
        input_ext = os.path.splitext(image_path)[1].lower()
        if input_ext not in (".png", ".jpg", ".jpeg"):
            # Convert to PNG for compatibility
            temp_input = os.path.join(temp_dir, "input.png")
            img_temp = Image.open(image_path).convert("RGB")
            img_temp.save(temp_input, "PNG")
            img_temp.close()
        else:
            temp_input = os.path.join(temp_dir, f"input{input_ext}")
            shutil.copy2(image_path, temp_input)

        temp_output = os.path.join(temp_dir, "output.png")
        
        if progress_callback:
            progress_callback(10)

        # Determine number of 4x passes needed
        current_input = temp_input
        passes_needed = 1
        if scale_needed > 4:
            passes_needed = 2  # 4x * 4x = 16x, enough for 8K from most images

        # Give 85% of the progress bar to the subprocess (the real work).
        # Post-processing (load + resize + sharpen) gets the remaining 5%.
        total_progress_per_pass = 85 // passes_needed

        for pass_num in range(passes_needed):
            pass_output = os.path.join(temp_dir, f"pass{pass_num}_output.png")

            # Build command
            # -n realesrgan-x4plus is the best quality model for photos
            cmd = [
                exe_path,
                "-i", current_input,
                "-o", pass_output,
                "-n", "realesrgan-x4plus",  # Best quality photo model
                "-s", "4",                   # 4x scale
                "-f", "png",                 # Output format
            ]

            if progress_callback:
                base_progress = 10 + (pass_num * total_progress_per_pass)
                progress_callback(base_progress + 2)

            # Run Real-ESRGAN
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE

            # Redirect stderr to a temp file instead of PIPE.
            # Using PIPE causes a deadlock when the 64 KB OS buffer fills
            # up (the subprocess blocks on write, poll() never returns).
            # A temp file avoids this entirely — no pipes, no threads needed.
            stderr_path = os.path.join(temp_dir, f"stderr_{pass_num}.log")
            stderr_fh = open(stderr_path, "w")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=stderr_fh,
                startupinfo=startupinfo,
                cwd=os.path.dirname(exe_path)
            )

            last_reported = base_progress + 2
            pass_start = time.time()
            EST_DURATION = 60.0  # seconds — tuned for typical photo upscale

            while process.poll() is None:
                time.sleep(0.5)
                if progress_callback:
                    elapsed = time.time() - pass_start
                    frac = min(elapsed / EST_DURATION, 0.97)
                    new_progress = base_progress + int(2 + frac * (total_progress_per_pass - 3))
                    new_progress = min(new_progress, base_progress + total_progress_per_pass - 1)
                    if new_progress > last_reported:
                        last_reported = new_progress
                        progress_callback(last_reported)

            process.wait()
            stderr_fh.close()

            if process.returncode != 0:
                error_text = ""
                try:
                    with open(stderr_path, "r", errors="replace") as f:
                        error_text = f.read()
                except Exception:
                    pass
                raise RuntimeError(f"Real-ESRGAN failed (code {process.returncode}): {error_text}")

            if not os.path.isfile(pass_output):
                raise RuntimeError("Real-ESRGAN did not produce output file")

            current_input = pass_output

            if progress_callback:
                progress_callback(10 + ((pass_num + 1) * total_progress_per_pass))

        # ── Post-processing (95% → 100%) ──
        if progress_callback:
            progress_callback(95)

        # Load the AI-upscaled result
        result_img = Image.open(current_input)
        result_img = result_img.convert("RGB")

        if progress_callback:
            progress_callback(96)

        # Final resize to exact target dimensions if needed
        if result_img.size != (target_w, target_h):
            result_img = result_img.resize((target_w, target_h), Image.LANCZOS)

        if progress_callback:
            progress_callback(98)

        # Light final sharpening (AI output is already very clean)
        result_img = result_img.filter(ImageFilter.UnsharpMask(
            radius=0.5, percent=20, threshold=4
        ))

        if progress_callback:
            progress_callback(100)

        return result_img

    finally:
        # Clean up temp directory
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


# ─────────────────────────────────────────────────
#  Pillow Fallback Engine (when Real-ESRGAN is not available)
# ─────────────────────────────────────────────────

def calculate_target_size(original_width, original_height, mode):
    """
    Calculate target dimensions preserving aspect ratio.
    The image is scaled so that the longer side matches the mode's
    corresponding dimension.
    """
    aspect = original_width / original_height

    if aspect >= 1:
        # Landscape or square
        target_w = mode.target_width
        target_h = int(target_w / aspect)
    else:
        # Portrait
        target_h = mode.target_height
        target_w = int(target_h * aspect)

    return target_w, target_h


def _pil_to_cv2(pil_img):
    """Convert PIL Image to OpenCV numpy array (BGR)."""
    import numpy as np
    rgb = np.array(pil_img)
    bgr = rgb[:, :, ::-1].copy()
    return bgr


def _cv2_to_pil(cv2_img):
    """Convert OpenCV numpy array (BGR) to PIL Image."""
    rgb = cv2_img[:, :, ::-1]
    return Image.fromarray(rgb)


def _enhance_with_opencv(pil_img, strength=1.0):
    """
    Apply OpenCV-based enhancement for sharper, more detailed pixels.
    """
    try:
        import cv2
        import numpy as np

        cv_img = _pil_to_cv2(pil_img)

        # Bilateral filter — edge-preserving denoise
        d = 5
        sigma_color = int(40 * strength)
        sigma_space = int(40 * strength)
        cv_img = cv2.bilateralFilter(cv_img, d, sigma_color, sigma_space)

        # Unsharp mask via OpenCV
        gaussian = cv2.GaussianBlur(cv_img, (0, 0), sigmaX=2.0)
        sharpened = cv2.addWeighted(cv_img, 1.0 + (0.6 * strength), gaussian, -(0.6 * strength), 0)

        # Detail enhancement
        sigma_s_val = 8
        sigma_r_val = max(0.05, 0.12 * strength)
        enhanced = cv2.detailEnhance(sharpened, sigma_s=sigma_s_val, sigma_r=sigma_r_val)

        # CLAHE on luminance
        lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        clip_limit = max(1.0, 1.5 * strength)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l_channel)

        blend_factor = min(0.5, 0.35 * strength)
        l_final = cv2.addWeighted(l_channel, 1.0 - blend_factor, l_enhanced, blend_factor, 0)

        lab_enhanced = cv2.merge([l_final, a_channel, b_channel])
        result = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

        return _cv2_to_pil(result)

    except ImportError:
        return pil_img


def upscale_with_pillow(image_path, mode, progress_callback=None):
    """
    Fallback upscale using Pillow + OpenCV enhancement.
    Used when Real-ESRGAN is not available.
    """
    import math

    if progress_callback:
        progress_callback(2)

    img = Image.open(image_path)
    img = img.convert("RGB")
    original_w, original_h = img.size

    if progress_callback:
        progress_callback(5)

    target_w, target_h = calculate_target_size(original_w, original_h, mode)

    if progress_callback:
        progress_callback(10)

    # Progressive multi-pass upscale
    scale_x = target_w / original_w
    scale_y = target_h / original_h
    total_scale = max(scale_x, scale_y)

    if total_scale <= 1.0:
        return img.resize((target_w, target_h), Image.LANCZOS)

    num_steps = max(1, min(4, int(math.ceil(math.log2(total_scale)))))
    current_img = img

    for step in range(num_steps):
        is_final = (step == num_steps - 1)
        if is_final:
            step_w, step_h = target_w, target_h
        else:
            step_w = min(current_img.width * 2, target_w)
            step_h = min(current_img.height * 2, target_h)

        current_img = current_img.resize((step_w, step_h), Image.LANCZOS)

        if is_final:
            current_img = current_img.filter(ImageFilter.UnsharpMask(radius=1.8, percent=80, threshold=2))
        else:
            current_img = current_img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=3))

        if progress_callback:
            progress_callback(10 + int(60 * (step + 1) / num_steps))

    if progress_callback:
        progress_callback(72)

    # OpenCV enhancement
    current_img = _enhance_with_opencv(current_img, strength=1.0)

    if progress_callback:
        progress_callback(90)

    # Final refinement
    current_img = current_img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=30, threshold=3))
    current_img = current_img.filter(ImageFilter.DETAIL)

    if progress_callback:
        progress_callback(100)

    return current_img


# ─────────────────────────────────────────────────
#  Main upscale function (auto-selects best engine)
# ─────────────────────────────────────────────────

def upscale_image(image_path, mode, progress_callback=None):
    """
    Upscale an image using the best available engine.
    
    Priority:
    1. Real-ESRGAN AI (if available) — Best quality
    2. Pillow + OpenCV — Fallback
    
    Args:
        image_path: Path to the input image
        mode: UpscaleMode enum value
        progress_callback: Optional callback function(int) for progress 0-100
    
    Returns:
        PIL.Image object of the upscaled image
    """
    if is_realesrgan_available():
        return upscale_with_realesrgan(image_path, mode, progress_callback)
    else:
        return upscale_with_pillow(image_path, mode, progress_callback)


def get_current_engine():
    """Get the name of the currently active upscale engine."""
    if is_realesrgan_available():
        return "Real-ESRGAN AI"
    else:
        return "Pillow + OpenCV (Basic)"


# ─────────────────────────────────────────────────
#  QThread Workers
# ─────────────────────────────────────────────────

class UpscaleWorker(QThread):
    """
    Worker thread for single image upscaling.
    Emits progress updates and the finished result.
    """
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)  # PIL Image
    error = pyqtSignal(str)

    def __init__(self, image_path, mode, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.mode = mode
        self._is_cancelled = False

    def cancel(self):
        """Request cancellation of the upscale process."""
        self._is_cancelled = True

    def run(self):
        """Execute the upscale process in background thread."""
        try:
            result = upscale_image(
                self.image_path,
                self.mode,
                progress_callback=self._report_progress
            )
            if not self._is_cancelled:
                self.finished.emit(result)
        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(str(e))

    def _report_progress(self, value):
        """Report progress back to the main thread."""
        if not self._is_cancelled:
            self.progress.emit(value)


class BatchUpscaleWorker(QThread):
    """
    Worker thread for batch image upscaling.
    Processes multiple files sequentially with pause/cancel support.
    """
    file_started = pyqtSignal(int, str)       # (index, filename)
    file_progress = pyqtSignal(int, int)       # (index, progress 0-100)
    file_completed = pyqtSignal(int, str, bool, str)  # (index, filename, success, message)
    overall_progress = pyqtSignal(int)         # overall progress 0-100
    batch_finished = pyqtSignal(list)          # list of (filename, success, message)
    error = pyqtSignal(str)

    def __init__(self, file_list, mode, output_dir, parent=None):
        super().__init__(parent)
        self.file_list = file_list
        self.mode = mode
        self.output_dir = output_dir
        self._is_cancelled = False
        self._is_paused = False
        self.results = []

    def cancel(self):
        """Request cancellation of the batch process."""
        self._is_cancelled = True

    def pause(self):
        """Toggle pause state."""
        self._is_paused = not self._is_paused

    def is_paused(self):
        """Check if the batch process is paused."""
        return self._is_paused

    def run(self):
        """Execute batch upscale process."""
        total = len(self.file_list)
        self.results = []
        completed_files = 0
        last_overall = 0  # Track highest overall to prevent going backwards

        for idx, file_path in enumerate(self.file_list):
            # Check for cancellation
            if self._is_cancelled:
                break

            # Handle pause
            while self._is_paused and not self._is_cancelled:
                time.sleep(0.1)

            if self._is_cancelled:
                break

            filename = os.path.basename(file_path)
            self.file_started.emit(idx, filename)

            try:
                # Capture idx and completed_files by value using default args
                # to avoid the closure-over-loop-variable bug.
                _file_idx = idx
                _done = completed_files

                def file_progress_cb(value, _i=_file_idx, _d=_done):
                    self.file_progress.emit(_i, value)
                    fraction = max(0, min(value, 100)) / 100.0
                    overall = int((_d + fraction) / total * 100)
                    self.overall_progress.emit(overall)

                # Upscale the image
                result_img = upscale_image(file_path, self.mode, file_progress_cb)

                # Generate output filename
                name, ext = os.path.splitext(filename)
                output_name = f"{name}_{self.mode.label}{ext}"
                output_path = os.path.join(self.output_dir, output_name)

                # Determine save format and quality
                save_kwargs = {}
                ext_lower = ext.lower()
                if ext_lower in (".jpg", ".jpeg"):
                    save_kwargs["format"] = "JPEG"
                    save_kwargs["quality"] = 95
                elif ext_lower == ".png":
                    save_kwargs["format"] = "PNG"
                elif ext_lower == ".bmp":
                    save_kwargs["format"] = "BMP"
                elif ext_lower == ".tiff" or ext_lower == ".tif":
                    save_kwargs["format"] = "TIFF"
                else:
                    # Default to PNG for unknown formats
                    output_name = f"{name}_{self.mode.label}.png"
                    output_path = os.path.join(self.output_dir, output_name)
                    save_kwargs["format"] = "PNG"

                result_img.save(output_path, **save_kwargs)
                result_img.close()  # Free memory immediately

                self.results.append((filename, True, f"Saved: {output_name}"))
                self.file_completed.emit(idx, filename, True, f"Saved: {output_name}")

            except Exception as e:
                self.results.append((filename, False, str(e)))
                self.file_completed.emit(idx, filename, False, str(e))

            # Increment after each file so overall never drops
            completed_files += 1
            overall_done = int(completed_files / total * 100)
            if overall_done > last_overall:
                last_overall = overall_done
            self.overall_progress.emit(last_overall)

        # Update overall progress to 100 if completed
        if not self._is_cancelled:
            self.overall_progress.emit(100)

        self.batch_finished.emit(self.results)
