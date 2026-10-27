<p align="center">
  <img src="public/images/logo.png" width="160" alt="NgapakIn & Larapak Logo" />
</p>

# NgapakIn & Larapak MVC

[![PyPI Version](https://img.shields.io/pypi/v/ngapakin.svg)](https://pypi.org/project/ngapakin/)
[![CI Test Suite](https://github.com/IlhamHattaManggala/ngapakin/actions/workflows/ci.yml/badge.svg)](https://github.com/IlhamHattaManggala/ngapakin/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)

NgapakIn adalah bahasa pemrograman open-source berekstensi `.ngpk`, dirancang dengan sintaksis berbasis dialek Ngapak / Banyumasan / Indonesia.

Larapak adalah MVC Web Framework lengkap yang berjalan di atas virtual machine (VM) NgapakIn, dirancang dengan arsitektur terstruktur seperti Laravel, menyediakan fungsionalitas modern mulai dari ORM, skema migrasi, antrean latar belakang (job queues), sesi dan cookie, validasi data, sistem cache, event dispatcher, package manager, hingga Language Server Protocol (LSP).

---

## Fitur Utama Ekosistem

1. **Inti Bahasa NgapakIn**:
   - Sintaksis berbasis dialek Banyumasan (`gawe`, `rampung`, `nek - ya - liyane`, `balekna`, `baleni ... neng`).
   - Operator logika (`lan`, `utawa`, `ora`) dan kontrol perulangan (`mandeg`, `terusna`).
   - Tipe data lengkap: Angka, Teks, List/Array, Dictionary, Boolean (`bener`/`salah`), dan Null (`kosong`).
   - Stack-based Virtual Machine (VM) efisien dengan eksekusi bytecode cepat.
2. **Larapak MVC Framework**:
   - Web Server berbasis standard library HTTP.
   - Dynamic routing (`routes/web.ngpk`, `routes/api.ngpk`) dengan middleware pipeline.
   - Template engine dengan layouting (`@layout`, `@sekat`, `@mlebui`), proteksi `@csrf`, penanganan error `@kleru`, serta auto-escaping `{{ }}` dan raw `{!! !!}`.
   - Serving aset statis (`public/css`, gambar, dsb).
3. **Database dan ORM System**:
   - Kelas berorientasi objek (`kelas ... extends Model`).
   - Fluent SQL Query Builder berbasis SQLite.
   - Skema Migrasi (`schema.gawe`, `schema.buang`) dan CLI migration engine.
   - Mode hening query log terintegrasi, dapat diaktifkan kembali melalui `DB_DEBUG=bener`.
4. **Layanan Lanjutan**:
   - **Autentikasi**: Fitur `auth` bawaan (`mlebu`, `metu`, `user`, `cek`).
   - **Sesi dan Cookies**: Penyimpanan sesi berbasis SQLite dengan helper cookie HTTP.
   - **Validasi**: Validator input dengan aturan `required`, `email`, `numeric`, `min`, `max`.
   - **Cache**: Penyimpanan data sementara berbasis SQLite dengan waktu kedaluwarsa (TTL).
   - **Event dan Listener**: Dispatcher event bawaan untuk pemrograman reaktif.
   - **Job Queues**: Pemrosesan latar belakang (background queue workers) dengan `queue:work`.
   - **Package Manager**: Pemasangan paket otomatis beserta auto-discovery Service Provider.
   - **REPL Terminal**: Terminal interaktif via `ngapakin repl`.
   - **Step Debugger**: Breakpoint debugger interaktif (`s` step, `c` continue, `l` locals, `g` globals).
   - **VSCode Support dan LSP**: Syntax highlighting TextMate dan diagnostik LSP syntax errors.

---

## Instalasi dan Memulai Cepat

### Metode 1: Menggunakan pip (Rekomendasi)
Anda dapat menginstal NgapakIn langsung dari PyPI:

```bash
pip install ngapakin
```

Setelah terpasang, buat proyek aplikasi web baru secara instan:

```bash
# Membuat struktur proyek baru
ngapakin new nama-proyek

# Masuk ke direktori dan jalankan server
cd nama-proyek
ngapakin serve 8000
```

Buka peramban di `http://localhost:8000`.

### Metode 2: Kloning Repositori Sumber

```bash
git clone https://github.com/IlhamHattaManggala/ngapakin.git
cd ngapakin
python ngapakin.py serve 8000
```

---

## Panduan Perintah CLI

CLI NgapakIn / Larapak menyediakan perintah pembantu:

```bash
# Eksekusi dan Kompilasi
ngapakin run berkas.ngpk              # Menjalankan berkas sumber
ngapakin compile berkas.ngpk          # Mengompilasi ke bytecode .ngpkc
ngapakin debug berkas.ngpk            # Menjalankan bytecode trace debugger
ngapakin repl                         # Membuka terminal interaktif

# Server dan Rute
ngapakin serve [port]                 # Menjalankan server web lokal (default: 8000)
ngapakin route:list                   # Menampilkan daftar seluruh rute aktif

# Scaffolding Komponen Baru
ngapakin new <NamaProyek>             # Membuat proyek web Larapak baru
ngapakin make:controller <Nama>       # Membuat controller baru di app/Controllers
ngapakin make:model <Nama>            # Membuat model ORM baru di app/Models
ngapakin make:middleware <Nama>       # Membuat middleware di app/Middleware
ngapakin make:migration <Nama>        # Membuat berkas migrasi database
ngapakin make:job <Nama>              # Membuat background job di app/Jobs

# Database dan Migrasi
ngapakin migrate                      # Menjalankan seluruh migrasi tertunda
ngapakin rollback                     # Membatalkan migrasi batch terakhir
ngapakin db:seed                      # Menjalankan berkas seeder database

# Layanan Ekosistem
ngapakin queue:work                   # Menjalankan background queue worker
ngapakin cache:clear                  # Membersihkan seluruh cache sistem
ngapakin package:install <nama>       # Memasang package dari registry
ngapakin test                         # Menjalankan seluruh rangkaian test suite
```

---

## Struktur Folder Proyek

```text
ngapakin/
├── .github/workflows/   # CI/CD Pipeline (Automated Tests & PyPI Release)
├── app/
│   ├── Controllers/     # Controller Kelas Larapak
│   ├── Jobs/            # Background Jobs
│   ├── Middleware/      # Request Middlewares
│   └── Models/          # Model Database (Autoloaded)
├── database/
│   ├── migrations/      # Berkas Migrasi Database
│   └── seeders/         # Berkas Database Seeder
├── editors/vscode/      # Ekstensi VSCode & LSP Server
├── framework/           # Modul Internal Larapak Core
├── ngapak/              # Compiler, Lexer, Parser & VM NgapakLang
├── packages/            # Lokasi Paket yang Diinstal
├── public/              # Berkas Aset Statis Publik (CSS, JS, media)
├── resources/views/     # Berkas Template View (.nview)
├── routes/              # Rute web & API (.ngpk)
├── tests/               # Berkas Rangkaian Unit Testing
├── ngapakin.py          # Entrypoint CLI
├── setup.py             # Konfigurasi Paket Distribusi PyPI
└── README.md
```

---

## Panduan Sintaksis dan Penggunaan

### 1. Validasi Input dan Autentikasi
```ngapak
# Validasi data request
data = ["email": "ilham@example.com", "umur": 20]
aturan = ["email": "required|email", "umur": "required|numeric|min:18"]

val = validator.gawe(data, aturan)
nek val.gagal() ya
    tulis "Validasi Gagal!"
    tulis val.errors()
liyane
    tulis "Validasi Sukses!"
rampung

# Login user
nek auth.mlebu("ilham@example.com", "password123") ya
    tulis "Berhasil Login!"
    tulis auth.user().name
liyane
    tulis "Login Gagal!"
rampung
```

### 2. Caching dan Pengelolaan Sesi
```ngapak
# Pengelolaan Sesi
sesi.pasang("cart_total", 150000)
total = sesi.entuk("cart_total")

# Pengelolaan Cache (Simpan data dengan TTL 60 detik)
cache.pasang("weather_jakarta", "Hujan", 60)
cuaca = cache.entuk("weather_jakarta")
```

### 3. Event Dispatcher dan Background Queue
```ngapak
# Event Listener
gawe kirimNotif(data)
    tulis "Mengirim notifikasi ke user ID: " + data
rampung
event.listen("user.registered", kirimNotif)
event.dispatch("user.registered", 99)

# Antrean Pekerjaan Latar Belakang (Queue Job)
queue.push("SendEmailJob", ["pesan": "Halo Selamat Datang!"])
```

---

## Interactive Breakpoint Debugger

Jalankan debug program menggunakan perintah `ngapakin debug <berkas.ngpk>`. Ketika VM menyala di mode tracing debugger, masukkan perintah berikut di shell `dbg>`:
- `s` atau [Enter]: Melangkah 1 instruksi bytecode (Step Over/Into).
- `c`: Lanjutkan eksekusi normal tanpa jeda (Continue).
- `l` atau `locals`: Cetak semua variabel lokal di frame aktif.
- `g` atau `globals`: Cetak semua variabel global yang terdaftar.
- `st` atau `stack`: Cetak kondisi VM stack saat ini.
- `q` atau `quit`: Hentikan program seketika.

---

## Konfigurasi Environment (.env)

Larapak membaca file `.env` secara otomatis saat aplikasi dimulai. Contoh konfigurasi default:

```ini
APP_NAME=LarapakApp
APP_ENV=local
APP_DEBUG=bener
APP_PORT=8000
APP_KEY=secret_key_random

DB_CONNECTION=sqlite
DB_DATABASE=database.sqlite
DB_DEBUG=salah
```

- Jika `DB_DEBUG=salah`, server berjalan tenang tanpa mencetak log SQL internal ke terminal.
- Jika `DB_DEBUG=bener`, seluruh query SQL internal akan dicetak ke terminal untuk mempermudah penelusuran data.

---

## Ekstensi VSCode dan LSP

1. Salin seluruh isi direktori `editors/vscode` ke dalam folder ekstensi VSCode lokal Anda:
   - Windows: `%USERPROFILE%\.vscode\extensions\ngapaklang-vscode`
   - Linux/macOS: `~/.vscode/extensions/ngapaklang-vscode`
2. Jalankan ulang VSCode. Berkas berekstensi `.ngpk` kini mendapatkan pewarnaan sintaksis TextMate.
3. Language Server otomatis memindai sintaksis dan menampilkan tanda diagnostik jika terjadi kesalahan penulisan kode.

---

## Pengujian Rangkaian Test

Kualitas ekosistem dipelihara dengan unit testing komprehensif. Jalankan perintah berikut untuk menguji seluruh komponen:

```bash
ngapakin test
```

---

## Roadmap Pengembangan

- **v1.1.0**: Dukungan HTTP Client terintegrasi untuk komunikasi API eksternal.
- **v1.2.0**: Relasi ORM Polimorfik (Many-to-Many dinamis).
- **v1.3.0**: Enkripsi berkas bytecode `.ngpkc` terkompresi tingkat lanjut.
- **v2.0.0**: Compiler NgapakIn JIT (Just-In-Time) untuk eksekusi setara kode mesin.

---

## Penulis dan Pengembang

- **Nama**: Ilham Hatta Manggala
- **Email**: [ilhamhattamanggala123@gmail.com](mailto:ilhamhattamanggala123@gmail.com)
- **Portofolio**: [ilhamhattamanggala.my.id](https://ilhamhattamanggala.my.id)
- **GitHub**: [github.com/IlhamHattaManggala](https://github.com/IlhamHattaManggala)

---

## Lisensi

Didistribusikan di bawah Lisensi **MIT** - Lihat berkas [LICENSE](LICENSE) untuk informasi lebih lanjut.
