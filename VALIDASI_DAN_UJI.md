# Catatan QA dan batas bukti

## Pemeriksaan sumber dan desain

- **Sumber konten:** dokumen DOCX asli diperiksa sampai bagian Panduan Pengelolaan Konten dan Daftar Sumber Resmi. Terdapat sepuluh kumpulan paragraf pembuka, subinformasi, ringkasan, narasi TTS, catatan validasi, dan kode sumber. Semuanya dimigrasi ke `data/menus.json` melalui parser dokumen, bukan disalin sebagai teks generik.
- **Gambar 01 Halaman Utama (1672×941):** header bertingkat biru tua + biru pucat, kamera kiri 38%, grid kanan 62%, banner, dua kolom × lima baris, footer gestur. Semua dibuat dengan widget Qt; tidak memakai PNG sebagai background.
- **Gambar 02 Halaman Konfirmasi (1672×941):** pilihan ditandai border biru, menu lain diredupkan, panel sentral dengan pilihan dan tombol konfirmasi/batal aktual. Panel juga muncul setelah gestur angka stabil.
- **Gambar 03 Halaman Detail (1672×941):** kamera tetap hidup, judul, intro, kartu subinformasi, ringkasan kanan, status audio aktual, dan tombol kembali. Semua menu memakai template yang sama dengan data berbeda.
- **Perbedaan disengaja:** contoh foto manusia, logo resmi, serta foto ruang pada mockup tidak dimasukkan karena tidak ada berkas asli berizin; aset vektor generik dipakai sebagai pengganti. Daftar Fasilitas mengikuti teks draft yang lebih berhati-hati daripada klaim spesifik di mockup.

## Bukti yang dapat diuji

| Kriteria | Pemeriksaan | Status |
|---|---|---|
| 10 menu lengkap | Parse DOCX + validasi JSON + unit test | Lulus |
| Angka 1–5; kiri/kanan | Landmark sintetis, klasifikasi murni | Lulus secara sintetis |
| Angka 6–10; urutan kedua tangan | Kombinasi landmark sintetis dua tangan | Lulus secara sintetis |
| Thumbs Up berbeda dari 1 dan Fist | Klasifikasi landmark sintetis | Lulus secara sintetis |
| Temporal debounce, latch, release | Unit test dengan waktu terkontrol | Lulus |
| HOME–CONFIRMATION–DETAIL–HOME | Unit test FSM | Lulus |
| Audio sekali per konfirmasi, stop saat Fist, replay kunjungan lain | Fake audio backend + FSM | Lulus pada logika; speaker belum diuji |
| Narasi unik/sumber sesuai menu | Validator JSON + unit test | Lulus |
| Sintaks seluruh Python | `compileall` | Lulus |
| QT GUI 4 resolusi | Smoke test tersedia, bukan dieksekusi | Belum teruji (PySide6 tidak terpasang) |
| Webcam nyata + MediaPipe | Implementasi nyata tersedia | Belum teruji perangkat; model butuh download |
| Edge TTS + output Qt multimedia | Implementasi dan cache tersedia | Belum teruji jaringan/perangkat |
| Screenshot dari aplikasi Qt | Skrip untuk menangkap 3 state tersedia | Tidak dihasilkan (PySide6 tidak tersedia) |

## Pengujian lanjutan yang dibutuhkan untuk penelitian

1. Ukur accuracy, macro F1, false activation rate, inference latency dari data rekaman berbasis persetujuan dan partisipan berbeda; unit test landmark sintetis tidak bisa membuktikan akurasi nyata.
2. Uji minimal dua kamera, kedua tangan, occlusion, mirror preview, intensitas cahaya, orientasi relatif, dan transisi 1 ↔ Thumbs Up.
3. Uji durasi gestur 0,3 sampai 3 detik, penahanan ≥5 detik, kesalahan frames, dan pergantian state.
4. Uji online, offline dengan cache, offline tanpa cache, output speaker terlepas, narasi kunjungan kedua, perubahan suara/kecepatan, dan ketepatan pengucapan nomor telepon/email.
5. Jalankan `QT_QPA_PLATFORM=offscreen python scripts/capture_screens.py` di lingkungan dengan PySide6 untuk mengambil screenshot widget Qt asli tanpa kamera; untuk validasi visual final lakukan screenshot lagi pada Windows/Linux dengan webcam.
6. Dapatkan persetujuan fakultas untuk konten dinamis serta izin logo dan foto sebelum publikasi.

Tidak ada klaim pengujian fisik dalam proyek ini. `last_verified_at` sengaja kosong meskipun naskah bertanggal 2 November 2026.
