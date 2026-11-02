# Layanan Informasi Cerdas FILKOM UB — prototipe penelitian

Prototipe penelitian **bukan produk resmi FILKOM UB**. Konten berasal dari `Konten_10_Menu_Layanan_Informasi_Cerdas_FILKOM_UB.docx`, draf 2 November 2026, bukan materi yang disahkan fakultas. Logo, foto ruangan, model orang pada PNG rancangan tidak digunakan sebagai aset yang mengesankan dokumentasi resmi. UI ditulis menggunakan widget Qt nyata.

## Instalasi

**Python 3.11 x64 direkomendasikan.** Webcam, audio output, dan (untuk pertama kali) akses internet diperlukan agar seluruh fungsi berjalan. Gunakan virtual environment pada Windows/Linux:

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python scripts/download_model.py
python main.py
```

Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python scripts/download_model.py
python main.py
```

Pada Linux, mungkin perlu menginstal pustaka sistem Qt/XCB, OpenGL, kamera V4L2, dan codec multimedia FFmpeg/GStreamer melalui distro. Jendela grafis harus tersedia. Jika `scripts/download_model.py` gagal, unduh secara manual `hand_landmarker.task` dari URL model resmi di `config.py` dan simpan pada `assets/models/hand_landmarker.task`. Model sengaja tidak disertakan dalam ZIP karena akses jaringan lingkungan pembuat terbatas. Jika tersedia jaringan saat aplikasi pertama dijalankan, worker kamera mencoba mengunduh model tersebut otomatis.

## Pemakaian

1. Izinkan akses kamera. Model memproses hingga dua tangan (21 landmark/tangan).
2. Gestur **1–5**: telunjuk, telunjuk+tengah, lalu tambah jari berurutan, empat jari tanpa ibu jari, lima jari. **6–10**: lima jari di salah satu tangan dan 1–5 jari di tangan lain. Angka dengan konfigurasi berbeda mungkin dinilai tidak dikenali.
3. Tahan gestur stabil sekurang-kurangnya 0,8 detik. Pada layar konfirmasi, lakukan gestur **Thumbs Up** (hanya ibu jari diangkat) untuk membuka informasi. Gestur **Fist** membatalkan atau kembali; pada halaman detail pemutaran suara dihentikan. Menahan gestur sama tidak mengaktifkan perintah berulang.
4. Untuk mouse dan keyboard: klik kartu, klik konfirmasi, klik kembali, gunakan `1`–`9`, `0` (menu 10), `Enter` (konfirmasi), `Esc` (batal/kembali). Aplikasi tetap bisa dieksplorasi tanpa webcam.
5. Tombol `⚙` membuka pilihan indeks kamera, durasi stabil, volume, pilihan suara Indonesia, kecepatan suara, mirror preview, overlay landmark, dan debugging FPS.
6. Tombol `?` untuk bantuan; `♙` untuk informasi prototipe. Semua tautan sumber detail dapat diklik. "Putar ulang" akan memulai audio kembali secara eksplisit; tanpa tindakan itu, audio hanya dipicu sekali per konfirmasi.

## MediaPipe dan akurasi

Implementasi menggunakan **MediaPipe Tasks Hand Landmarker** dalam mode `VIDEO`; inferensi berada di `QThread` yang menangani kamera. Aturan penghitungan jari menggunakan sudut sendi dan jarak relatif untuk mengurangi ketergantungan ukuran tangan. Gestur dikenali sebagai *canonical finger patterns* dan gesture lain menghasilkan `UNKNOWN`. Algoritme berbasis aturan **belum dinyatakan akurat secara empiris**; perlu pengujian subjek dan kondisi nyata (perbedaan arah, occlusion, cahaya, tangan kiri/kanan) serta pembuatan confusion matrix sebelum kesimpulan penelitian. Thumbs Up mensyaratkan hanya ibu jari lurus dan mengarah atas pada citra; tidak disamakan dengan telunjuk lurus.

## Audio dan cache

Narasi **hanya memakai suara neural bahasa Indonesia** (`id-ID-GadisNeural`/`id-ID-ArdiNeural`) menggunakan `edge-tts` ketika online. MP3 per kombinasi teks+suara+kecepatan di-cache pada `~/.cache/filkom-gesture-info/audio` (Windows: folder profil pengguna setara). Setelah sintesis pertama, file cache dapat diputar offline. Bila internet terputus dan cache tidak ada, UI menampilkan error audio secara eksplisit dan tetap membuka konten visual; tidak menggunakan TTS bahasa Inggris. Pemutaran Qt Multimedia menggunakan `QMediaPlayer` dengan `QAudioOutput`; audio distop langsung pada Fist, dan token permintaan mencegah audio lama diputar setelah berpindah state. Audio yang tersimpan dapat dibersihkan manual dari cache pengguna.

## Konten dan validasi

`data/menus.json` memuat 10 menu dari DOCX. `last_verified_at:null` dan `verification_status:DRAF_BELUM_DISAHKAN` disengaja: tanggal dokumen **bukan** tanggal verifikasi institusional. Sumber berupa URL di situs UB/FILKOM yang diberikan dokumen. Situs tersebut belum diverifikasi ulang pada waktu build. Menu informasi dinamis menampilkan pengingat periksa sumber terbaru. Setelah perubahan dokumen, jalankan `python scripts/import_docx_content.py path/dokumen.docx --output data/menus.json`, lakukan validasi kembali sebelum distribusi. Foto dan logo resmi dapat ditambahkan setelah izin/persetujuan; ikon `assets/icons/` berupa SVG generik.

## Tes

```bash
python -m compileall -q .
python -m pytest -q tests
```

Unit test tidak memerlukan webcam/speaker. Pengujian GUI dapat dijalankan pada workstation dengan PySide6 terpasang: `pytest -q tests/test_gui.py`. Mode uji GUI menggunakan `QT_QPA_PLATFORM=offscreen` (tidak membuktikan tampilan GPU/Windows). Tes perangkat manual: periksa semua angka, tangan kiri/kanan, perbedaan 1 vs Thumbs Up, Fist, duplikasi pemutaran, putus webcam, offline cache, dan resolusi 1366×768, 1600×900, 1672×941, 1920×1080.

## Penanganan error

- **Kamera tidak ditemukan:** pilih indeks 0, 1, 2 di Pengaturan. Cek izin Windows Camera atau `/dev/video*` di Linux.
- **MediaPipe tidak berjalan:** model `assets/models/hand_landmarker.task` harus tersedia; jalankan `scripts/download_model.py` online. Pastikan Python dan arsitektur paket cocok.
- **Suara tidak tersedia:** cek koneksi untuk sintesis pertama; cek audio output dan codec Qt Multimedia pada Linux; coba suara lain bila perlu. Cache yang korup dapat dihapus.
- **Layar terpotong atau font berbeda:** atur scaling OS dan maximize. Grid dan kartu detail disediakan scroll vertikal. Pastikan font Segoe UI atau Noto Sans terpasang.
- **Log:** `~/.local/state/filkom-gesture-info/app.log` atau lokasi `FILKOM_LOG`. Tidak merekam maupun menyimpan video otomatis.

## Struktur

- `app/screens`: 3 layar GUI
- `app/widgets`: kamera, footer, dan kartu
- `app/services`: CV, klasifikasi, debounce, FSM, TTS, audio, konten
- `config.py`: pengaturan tersimpan di profil pengguna
- `scripts`: importer DOCX dan downloader model
- `tests`: tes murni serta smoke test GUI opsional

**Keterbatasan:** tidak ada jaminan akurasi gestur dari unit test sintetis, atau kompatibilitas peranti webcam/speaker, tanpa uji fisik. Model AI awal perlu diunduh. Konten belum disahkan fakultas.
