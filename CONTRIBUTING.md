# Kontribusi untuk NgapakIn & Larapak

Senang melihat Anda tertarik berkontribusi pada NgapakIn! Sebagai proyek open-source, kami sangat menyambut kontribusi berupa perbaikan bug, penambahan fitur, peningkatan dokumentasi, maupun pembuatan issue.

## Alur Kerja Kontribusi

### 1. Membuat Issue
Sebelum menulis kode baru atau melakukan perubahan besar, silakan buat issue terlebih dahulu di GitHub untuk berdiskusi:
- Jelaskan bug atau fitur yang ingin Anda bahas.
- Lampirkan cuplikan kode atau tangkapan layar jika relevan.
- Berikan usulan solusi.

### 2. Fork & Clone Proyek
Fork repository ini ke akun GitHub Anda, kemudian clone secara lokal:
```bash
git clone https://github.com/IlhamHattaManggala/ngapakin.git
cd ngapakin
```

### 3. Struktur Branching
Kami menggunakan strategi branching berikut:
- **`main`**: Kode stabil siap produksi.
- **`development`**: Branch integrasi utama untuk fitur baru sebelum dirilis ke `main`.
Silakan buat branch baru dari `development` untuk pekerjaan Anda:
```bash
git checkout development
git checkout -b feature/nama-fitur-anda
```

### 4. Menjalankan Unit Test secara Lokal
Sebelum mengirimkan Pull Request, pastikan semua tes berjalan sukses dengan perintah:
```bash
$env:PYTHONPATH="."; pytest
# Atau pada Linux/MacOS:
PYTHONPATH=. pytest
```

### 5. Mengirimkan Pull Request (PR)
- Lakukan commit dengan pesan yang jelas (misal: `feat: tambah metode anyar di ORM`).
- Push branch Anda ke repository fork Anda.
- Buat Pull Request ke branch **`development`** di repository utama.
- Tim kami akan meninjau perubahan Anda secepat mungkin.

## Standar Kode
- Kode harus ditulis menggunakan standard library Python saja (Zero external dependencies).
- Gunakan penamaan variabel dan fungsi yang bersih dan deskriptif.
- Dokumentasikan fungsi atau perubahan baru di file markdown yang relevan.
