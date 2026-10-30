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
   - Web Server: Multi-threaded development server (`ngapakin serve [host] [port]`) dan production WSGI adapter (`framework.wsgi:app` untuk Gunicorn/uWSGI).
   - Dynamic routing (`routes/web.ngpk`, `routes/api.ngpk`) dengan middleware pipeline, route group, dan HTTP method spoofing (`_method=PUT/PATCH/DELETE`).
   - Proteksi CSRF otomatis pada semua request state-changing (POST, PUT, PATCH, DELETE) dengan token terikat sesi dan dukungan header `X-CSRF-TOKEN`.
   - Rate Limiting / Throttle Middleware bawaan (`throttle:60,1`) dengan header standar (`Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`).
   - Halaman Error Interaktif Modern (Ignition style) saat `APP_DEBUG=bener` dengan cuplikan berkas, call stack, dan tab request/environment; serta halaman 500 aman anti-bocor di mode produksi.
   - Parser request modern yang mendukung JSON, form URL-encoded, dan `multipart/form-data` dengan perlindungan path traversal serta sanitasi berkas aman.
   - Template engine dengan layouting (`@layout`, `@sekat`, `@mlebui`), proteksi `@csrf`, penanganan error `@kleru`, serta auto-escaping `{{ }}` dan raw `{!! !!}`.
   - Serving aset statis (`public/css`, gambar, dsb).
3. **Database dan ORM System**:
   - Database Driver Abstraction: Driver default SQLite dengan WAL mode + busy timeout, serta dukungan penuh untuk **MySQL** (`pymysql`) dan **PostgreSQL** (`psycopg2`).
   - Kelas berorientasi objek (`kelas ... extends Model`).
   - Fluent SQL Query Builder berbasis parameterized query aman di seluruh database driver.
   - ORM Eager Loading: Pengambilan relasi secara batch (`Model.with_("relasi").kabeh()`) untuk mengeliminasi masalah N+1 queries.
   - Pagination & Offset Otomatis: `Model.kaca(10)` / `paginate(10)` dan `Model.lewati(10)` / `offset(10)`.
   - Skema Migrasi (`schema.gawe`, `schema.buang`) dan CLI migration engine lengkap (`migrate`, `migrate:fresh [--seed]`, `migrate:status`, `rollback`).
   - Mode hening query log terintegrasi, dapat diaktifkan kembali melalui `DB_DEBUG=bener`.
4. **Layanan Lanjutan & Hardening**:
   - **Autentikasi & Hashing**: Hashing adaptif berbasis **Argon2id** / **PBKDF2-SHA256** dengan verifikasi constant-time dan migrasi otomatis dari password lama.
   - **Isolasi Penyimpanan (Anti-Locking)**: Pemisahan penyimpanan Sesi, Cache, dan Queue ke berkas database independen untuk mencegah error `database is locked`.
   - **Sesi dan Cookies**: Penyimpanan sesi independen dengan cookie HTTP aman (`HttpOnly`, `SameSite=Lax`, `Secure`).
   - **Validasi**: Validator input dengan aturan `required`, `email`, `numeric`, `min`, `max`.
   - **Cache**: Driver SQLite dengan TTL otomatis dan dukungan opsional backend **Redis**.
   - **Event dan Listener**: Dispatcher event bawaan untuk pemrograman reaktif.
   - **Job Queues**: Pemrosesan latar belakang atomic (`queue:work`) dengan dukungan SQLite non-blocking dan opsi **Redis**.
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
ngapakin new <NamaProyek> [--bahasa=ngapak|indonesia|english]  # Membuat proyek web Larapak baru (pilihan bahasa folder)
ngapakin make:controller <Nama>       # Membuat controller baru (otomatis menyesuaikan struktur proyek)
ngapakin make:model <Nama>            # Membuat model ORM baru (otomatis menyesuaikan struktur proyek)
ngapakin make:middleware <Nama>       # Membuat middleware di app/Middleware
ngapakin make:migration <Nama>        # Membuat berkas migrasi database
ngapakin make:job <Nama>              # Membuat background job di app/Jobs

# Database dan Migrasi
ngapakin migrate                      # Menjalankan seluruh migrasi tertunda
ngapakin migrate:fresh [--seed]       # Membersihkan database dan menjalankan ulang semua migrasi
ngapakin migrate:status               # Menampilkan status eksekusi seluruh berkas migrasi
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

### 4. ORM Eager Loading (Eliminasi N+1 Queries)
```ngapak
# Mengambil seluruh pengguna beserta postingannya hanya dalam 2 query SQL teroptimasi:
pengguna = User.with_("postingan").kabeh()

baleni u neng pengguna ya
    tulis "User: " + u.name
    baleni p neng u.postingan() ya
        tulis " - Judul: " + p.judul
    rampung
rampung
```

### 5. Password Hashing
```ngapak
# Hashing password adaptif (Argon2id / PBKDF2)
hash_pass = hash.hash_password("KunciRahasia2026")

# Verifikasi aman dengan proteksi timing attack
cocok = hash.verify_password("KunciRahasia2026", hash_pass)
```

### 6. File Upload dan Form Method Spoofing
```html
<!-- Form upload dengan proteksi CSRF dan spoofing method PUT -->
<form action="/profil/foto" method="POST" enctype="multipart/form-data">
    @csrf
    <input type="hidden" name="_method" value="PUT">
    <input type="file" name="avatar">
    <button type="submit">Unggah Foto</button>
</form>
```

```python
# Controller penanganan unggahan berkas (app/Controllers/ProfilController.py / .ngpk)
# Berkas otomatis disanitasi dan dilindungi dari path traversal
gawe simpen_avatar(req, res)
    nek req.has_file("avatar") ya
        berkas = req.file("avatar")
        lokasi = berkas.save("storage/uploads/avatars")
        balekna res.html("<p>Foto berhasil disimpan di: " + lokasi + "</p>")
    liyane
        balekna res.html("<p>Tidak ada berkas yang dipilih.</p>")
    rampung
rampung
```

### 5. Pagination & Offset di Model / ORM
```ngapak
# Mengambil data produk per halaman (10 data per halaman, halaman 1)
kaca_produk = Product.kaca(10, 1)

# Mengakses data dan informasi pagination
produk_list = kaca_produk["data"]
total_data = kaca_produk["total"]
kaca_pungkasan = kaca_produk["kaca_pungkasan"]

# Offset manual (ambil 5 data lewati 10 data pertama)
data_pilihan = Product.ambil(5).lewati(10).kabeh()
```

### 6. Rate Limiting / Throttle Middleware
```ngapak
# Batasi maksimal 60 request per 1 menit pada rute tertentu
rute.group(["middleware": "throttle:60,1"], gawe()
    rute.get("/api/data", "ApiController@data")
rampung)
```

---

## Developer Error Debugger (Ignition Style)

Larapak dilengkapi dengan debugger visual interaktif bertenaga tinggi saat `APP_DEBUG=bener`:
- **StackTrace & Cuplikan Kode**: Menampilkan sorotan baris kode error pada berkas terkait.
- **Panyuwunan (Request)**: Memeriksa HTTP Method, Parameter URL, Header, Body, dan Cookie secara detail.
- **Lingkungan (Environment)**: Memeriksa versi runtime Larapak, Python, driver database, serta status cache.
- **Mode Produksi (`APP_DEBUG=salah`)**: Menampilkan halaman 500 error yang elegan, aman, dan tanpa membocorkan trace sensitif ke publik.

---

## Larapak Route & API Studio (`/api-studio`)

Larapak dilengkapi studio dokumentasi rute dan pengujian interaktif otomatis (gabungan Swagger UI + Live Route Explorer) yang dapat diakses di:
```text
http://localhost:8000/api-studio  (atau http://localhost:8000/api/studio)
```

- **Auto Route Discovery**: Memetakan seluruh rute aplikasi, parameter URL dinamis (`{id}`), dan middleware secara instan tanpa konfigurasi manual.
- **Dukungan Penuh Rute View (HTML) & API (JSON)**:
  - **Pratinjau Tampilan (Live View)**: Menampilkan renderan halaman web asli langsung di dalam isolated iframe sandbox dengan tombol responsif Desktop (100%), Tablet (768px), dan Mobile (375px).
  - **Inspeksi Template**: Menampilkan nama berkas `.nview` yang dirender beserta kunci variabel context.
  - **Kode Mentah (Raw)**: Syntax highlight untuk HTML atau JSON dengan tombol salin instan.
- **Interactive Playground (Try It Out)**:
  - Menguji request HTTP langsung dari browser dengan parameter URL dinamis, query string, dan payload body.
  - **Auto-CSRF Injected**: Menyertakan token CSRF otomatis pada permintaan `POST`, `PUT`, `PATCH`, dan `DELETE` agar pengujian form web tidak terbentur error 403 Forbidden.
- **Spesifikasi Standar OpenAPI 3.0**:
  - Menyediakan endpoint `/api-studio/openapi.json` yang kompatibel dengan ekosistem Swagger, Postman, dan Insomnia.

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

Larapak membaca file `.env` secara otomatis saat aplikasi dimulai. Contoh konfigurasi database yang didukung:

```ini
APP_NAME=LarapakApp
APP_ENV=local
APP_DEBUG=bener
APP_PORT=8000
APP_KEY=secret_key_random

# 1. SQLite (Bawaan)
DB_CONNECTION=sqlite
DB_DATABASE=database.sqlite

# 2. MySQL / MariaDB (pip install 'ngapakin[mysql]')
# DB_CONNECTION=mysql
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_DATABASE=larapak_db
# DB_USERNAME=root
# DB_PASSWORD=rahasia

# 3. PostgreSQL (pip install 'ngapakin[postgres]')
# DB_CONNECTION=pgsql
# DB_HOST=127.0.0.1
# DB_PORT=5432
# DB_DATABASE=larapak_db
# DB_USERNAME=postgres
# DB_PASSWORD=rahasia

# 4. Microsoft SQL Server (pip install 'ngapakin[mssql]')
# DB_CONNECTION=sqlsrv
# DB_HOST=127.0.0.1
# DB_PORT=1433
# DB_DATABASE=larapak_db
# DB_USERNAME=sa
# DB_PASSWORD=rahasia

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
