# NgapakIn & Larapak MVC 🚀

[![NgapakLang CI Pipeline](https://github.com/IlhamHattaManggala/ngapakin/actions/workflows/python.yml/badge.svg)](https://github.com/IlhamHattaManggala/ngapakin/actions/workflows/python.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/)

NgapakIn adalah bahasa pemrograman open-source dengan ekstensi `.ngpk`, dirancang dengan sintaksis berbasis bahasa Ngapak / Banyumasan / Indonesia. 
Larapak adalah MVC Web Framework lengkap yang berjalan di atas VM NgapakIn, dirancang meniru arsitektur elegan Laravel dengan fungsionalitas modern seperti ORM, Migrasi, Job Queues, Session/Cookies, Validasi, Caching, Event Dispatcher, Package Manager, hingga Language Server Protocol (LSP).

---

## 🌟 Fitur Utama Ekosistem (Phase 1 - Phase 5)

1. **Inti Bahasa NgapakIn (Phase 1 & 2)**:
   - Sintaksis berbasis dialek Banyumasan (`gawe`, `rampung`, `nek - ya - liyane`, `balekna`).
   - Tipe data lengkap: Angka, Teks, Boolean (`bener`/`salah`), dan Null (`kosong`).
   - Stack-based Virtual Machine (VM) yang efisien dengan eksekusi bytecode cepat.
2. **Larapak MVC Framework (Phase 3)**:
   - Web Server berbasis standard library HTTP.
   - Routing dinamis (`routes/web.ngpk`, `routes/api.ngpk`).
   - Blade-like Template Engine dengan layouting (`@layout`, `@sekat`, `@mlebui`).
3. **Database & ORM System (Phase 4)**:
   - Kelas berorientasi objek (`kelas ... extends Model`).
   - Fluent SQL Query Builder berbasis SQLite.
   - Skema Migrasi (`schema.gawe`, `schema.buang`) dan CLI migration engine.
4. **Ecosystem & Advanced Features (Phase 5)**:
   - **Autentikasi**: Fitur `auth` bawaan (`mlebu`, `metu`, `user`, `cek`).
   - **Sesi & Cookies**: Penyimpanan sesi berbasis database SQLite, helper cookies.
   - **Validasi**: Validator input dengan aturan `required`, `email`, `numeric`, `min`, `max`.
   - **Cache**: Penyimpanan data sementara berbasis SQLite dengan waktu kedaluwarsa (TTL).
   - **Event/Listener**: Dispatcher event bawaan untuk pemrograman reaktif.
   - **Job Queues**: Pemrosesan latar belakang (background queue workers) dengan `queue:work`.
   - **Package Manager**: Pemasangan paket otomatis beserta auto-discovery Service Provider.
   - **REPL Terminal**: Interactive terminal interaktif via `repl`.
   - **Step Debugger**: Breakpoint debugger interaktif (`s` step, `c` continue, `l` locals, `g` globals).
   - **VSCode Support & LSP**: Syntax highlighting TextMate & diagnostik LSP syntax errors.

---

## 📁 Struktur Folder Proyek

```text
ngapakin/
├── .github/workflows/   # CI/CD Pipeline
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
├── routes/              # Rute web & API (.ngpk)
├── tests/               # Berkas Unit Testing
├── ngapakin.py          # Entrypoint CLI
└── README.md
```

---

## 🛠️ Instalasi & Penggunaan

### Prasyarat
- Python 3.8 ke atas (tanpa ketergantungan pustaka pihak ketiga).

### Cara Kloning & Memulai Proyek
```bash
git clone https://github.com/IlhamHattaManggala/ngapakin.git
cd ngapakin
```

---

## 💻 Panduan CLI Command

Larapak menyediakan CLI helper komprehensif melalui `ngapakin.py`:

```bash
# Menjalankan berkas kode biasa
python ngapakin.py run berkas.ngpk

# Menjalankan server web Larapak (port default: 8000)
python ngapakin.py serve 8000

# Melihat daftar rute terdaftar
python ngapakin.py route:list

# Membuat komponen baru (Scaffolding)
python ngapakin.py make:controller UserController
python ngapakin.py make:model Member
python ngapakin.py make:middleware AuthMiddleware
python ngapakin.py make:migration create_users_table
python ngapakin.py make:job SendEmailJob

# Migrasi Database
python ngapakin.py migrate       # Jalankan migrasi
python ngapakin.py rollback      # Kembalikan migrasi terakhir
python ngapakin.py db:seed       # Jalankan seeder database

# Layanan Ekosistem
python ngapakin.py cache:clear                    # Hapus data cache
python ngapakin.py queue:work                     # Jalankan pemroses job queue
python ngapakin.py package:install auth-helper    # Pasang paket baru
python ngapakin.py repl                           # Masuk ke REPL interaktif
python ngapakin.py debug berkas.ngpk              # Debug bytecode berkas
```

---

## 📖 Cara Menggunakan Fitur Ekosistem

### 1. Validasi & Autentikasi
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

### 2. Caching & Sesi
```ngapak
# Sesi
sesi.pasang("cart_total", 150000)
total = sesi.entuk("cart_total")

# Cache (Simpan data 60 detik)
cache.pasang("weather_jakarta", "Hujan", 60)
cuaca = cache.entuk("weather_jakarta")
```

### 3. Event & Queue
```ngapak
# Event
gawe kirimNotif(data)
    tulis "Mengirim notifikasi ke user ID: " + data
rampung
event.listen("user.registered", kirimNotif)
event.dispatch("user.registered", 99)

# Queue Job
queue.push("SendEmailJob", ["pesan": "Halo Selamat Datang!"])
```

---

## 🔍 Interactive Breakpoint Debugger

Jalankan debug program menggunakan perintah `python ngapakin.py debug <file.ngpk>`. Ketika VM menyala di mode tracing debugger, Anda dapat memasukkan perintah berikut di shell `dbg>`:
- `s` atau [Enter]: Melangkah 1 instruksi bytecode (Step Over/Into).
- `c`: Lanjutkan eksekusi normal tanpa jeda (Continue).
- `l` atau `locals`: Cetak semua variabel lokal di call frame aktif.
- `g` atau `globals`: Cetak semua variabel global yang terdaftar.
- `st` or `stack`: Cetak kondisi VM stack saat ini.
- `q` atau `quit`: Hentikan program seketika.

---

## 🎨 VSCode Extension & LSP Setup

1. Salin seluruh isi direktori `editors/vscode` ke dalam folder ekstensi VSCode lokal Anda:
   - Windows: `%USERPROFILE%\.vscode\extensions\ngapaklang-vscode`
   - Linux/macOS: `~/.vscode/extensions/ngapaklang-vscode`
2. Jalankan ulang VSCode. Berkas berekstensi `.ngpk` kini mendapatkan pewarnaan sintaksis.
3. Language Server otomatis memindai sintaksis dan menampilkan tanda garis bawah merah jika terjadi error penulisan (LSP Diagnostics).

---

## 🧪 Pengujian Pipeline

Kami menjaga kualitas ekosistem dengan unit testing komprehensif. Jalankan perintah berikut untuk memvalidasi:
```bash
$env:PYTHONPATH="."; pytest
```

---

## 🗺️ Roadmap Masa Depan

- **v1.1.0**: Dukungan HTTP Client terintegrasi untuk komunikasi API eksternal.
- **v1.2.0**: Relasi ORM Polimorfik (Many-to-Many dinamis).
- **v1.3.0**: Enkripsi berkas bytecode `.ngpkc` terkompresi tingkat lanjut.
- **v2.0.0**: Compiler NgapakIn JIT (Just-In-Time) untuk kecepatan setara kode mesin.

---

## 📄 Lisensi
Dilindungi oleh Lisensi **MIT** - Lihat berkas [LICENSE](file:///d:/Ilham%20Hatta%20Manggala/Joki%20Project/NgapakLang/LICENSE) untuk detail.
