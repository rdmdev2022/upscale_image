# Rancangan Aplikasi Upscale Foto

## Deskripsi
Aplikasi desktop untuk melakukan upscale (peningkatan resolusi) foto menggunakan Python dengan antarmuka grafis berbasis PyQt/PySide.

## Fitur Utama

### 1. Interface menggunakan Qt GUI (PyQt5/PySide6)
- Tampilan modern dan user-friendly
- Drag & drop support untuk memuat foto
- Tombol browse untuk memilih file foto
- Preview foto sebelum dan sesudah upscale (side-by-side)

### 2. Upscale Foto
- Menggunakan library/model AI untuk meningkatkan resolusi foto (misal: Real-ESRGAN, OpenCV Super Resolution, atau Pillow resize dengan filter LANCZOS)
- Menjaga kualitas gambar saat di-upscale

### 3. Mode Upscale yang Dapat Dipilih
- **2K** (2560 x 1440)
- **4K** (3840 x 2160)
- **8K** (7680 x 4320)
- User dapat memilih mode melalui dropdown/combobox

### 4. Progress Bar saat Upscale
- Menampilkan progress bar selama proses upscale berlangsung
- Proses upscale berjalan di background thread agar UI tidak freeze
- Menampilkan persentase progress

### 5. Simpan Foto Hasil Upscale
- Dialog "Save As" untuk memilih lokasi penyimpanan
- Support format output: PNG, JPEG, BMP, TIFF
- Opsi kualitas output (untuk JPEG)

### 6. Tampilkan Foto Hasil Upscale
- Preview hasil upscale langsung di aplikasi
- Zoom in/out untuk melihat detail
- Perbandingan before/after

### 7. Batch Processing (Multi-File Upscale)
- Dapat memilih banyak file gambar sekaligus untuk di-upscale
- Drag & drop multiple files atau select folder
- Tampilkan daftar antrian (queue list) file yang akan diproses
- Progress bar per-file dan progress keseluruhan batch
- Pilih output folder untuk menyimpan semua hasil batch
- Opsi penamaan otomatis file hasil (misal: `namafile_4K.png`)
- Tombol Start/Pause/Cancel untuk kontrol batch process
- Log/report hasil batch (berhasil/gagal per file)

---

## Tech Stack
| Komponen | Teknologi |
|---|---|
| Bahasa | Python 3.10+ |
| GUI Framework | PyQt5 / PySide6 |
| Image Processing | Pillow, OpenCV |
| AI Upscale (opsional) | Real-ESRGAN / OpenCV DNN |
| Threading | QThread / threading |

## Struktur Project (Rencana)
```
upscale_image/
├── main.py              # Entry point aplikasi
├── ui/
│   ├── main_window.py   # Main window UI
│   └── widgets.py       # Custom widgets (preview, progress)
├── core/
│   ├── upscaler.py      # Logic upscale foto
│   └── image_utils.py   # Utility fungsi image
├── resources/
│   └── icons/           # Icon aplikasi
├── requirements.txt     # Dependencies
└── README.md
```

## Checklist
- [ ] Setup project dan dependencies
- [ ] Buat main window dengan Qt GUI
- [ ] Implementasi fitur load/browse foto
- [ ] Implementasi dropdown pilihan mode upscale (2K, 4K, 8K)
- [ ] Implementasi logic upscale foto
- [ ] Implementasi progress bar dengan background thread
- [ ] Implementasi fitur simpan foto hasil upscale
- [ ] Implementasi preview foto hasil upscale
- [ ] Implementasi batch processing (multi-file select, queue, batch progress)
- [ ] Testing dan bug fixing
- [ ] Dokumentasi README
