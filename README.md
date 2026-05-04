# 🖼 Image Upscaler Pro

Aplikasi desktop untuk melakukan upscale (peningkatan resolusi) foto menggunakan Python dengan antarmuka grafis modern berbasis PyQt5.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green?logo=qt)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Fitur

- 🖼 **Single Image Upscale** — Upscale satu foto dengan preview before/after
- 📁 **Batch Processing** — Upscale banyak foto sekaligus dengan queue management
- 🎯 **Mode Resolusi** — Pilih target: 2K (2560×1440), 4K (3840×2160), atau 8K (7680×4320)
- 📊 **Progress Bar** — Tampilan progress real-time saat upscale
- 🖱 **Drag & Drop** — Drop file/folder langsung ke aplikasi
- 🔍 **Zoom & Pan** — Preview detail gambar dengan zoom in/out
- 💾 **Multi-Format** — Support PNG, JPEG, BMP, TIFF, WebP
- 🌙 **Dark Mode** — Tampilan modern dark theme

## 📋 Requirements

- Python 3.10+
- PyQt5
- Pillow
- OpenCV (optional)

## 🚀 Installation

1. Clone repository:
```bash
git clone https://github.com/rdmdev2022/upscale_image.git
cd upscale_image
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Jalankan aplikasi:
```bash
python main.py
```

## 🎮 Penggunaan

### Single Upscale
1. Klik **Browse Image** atau drag & drop foto ke area drop zone
2. Pilih mode upscale (2K / 4K / 8K)
3. Klik **Upscale Now**
4. Lihat preview before/after
5. Klik **Save Result** untuk menyimpan

### Batch Processing
1. Pindah ke tab **Batch Processing**
2. Tambah file via **Add Files**, **Add Folder**, atau drag & drop
3. Pilih mode upscale dan output folder
4. Klik **Start Batch**
5. Gunakan **Pause** / **Cancel** untuk kontrol proses
6. Lihat log hasil di panel bawah

## 📁 Struktur Project

```
upscale_image/
├── main.py              # Entry point aplikasi
├── requirements.txt     # Dependencies
├── README.md            # Dokumentasi
├── core/
│   ├── __init__.py
│   ├── upscaler.py      # Logic upscale & worker threads
│   └── image_utils.py   # Utility functions
└── ui/
    ├── __init__.py
    ├── main_window.py   # Main window UI
    ├── widgets.py       # Custom widgets
    └── styles.py        # Dark theme stylesheet
```

## 🛠 Tech Stack

| Komponen | Teknologi |
|---|---|
| Bahasa | Python 3.10+ |
| GUI | PyQt5 |
| Image Processing | Pillow (LANCZOS) |
| Threading | QThread |

## 📄 License

MIT License
