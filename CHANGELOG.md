# Catatan Perubahan (Changelog)

Semua perubahan besar pada proyek NgapakIn akan dicatat di dokumen ini.

## [1.0.7] - 2026-10-30

### Ditambahkan
- **Developer Error Debugger Interaktif (Ignition/Whoops Style)**:
  - Antarmuka visual berestetika tinggi (OLED Dark Mode, Doppelrand double-bezel card, JetBrains Mono code viewer) saat `APP_DEBUG=bener`.
  - Cuplikan baris kode kesalahan dengan sorotan marker merah menyala dan konteks 5 baris atas/bawah.
  - Tab navigasi interaktif: `StackTrace & Berkas`, `Panyuwunan (Request)`, dan `Lingkungan (Environment)`.
  - Halaman 500 minimalis yang aman dan anti-bocor untuk lingkungan produksi (`APP_DEBUG=salah`).
- **CLI Migrasi Tingkat Lanjut**:
  - `ngapakin migrate:fresh [--seed]`: Menghapus seluruh tabel dan menjalankan ulang seluruh migrasi secara bersih, dengan opsi langsung menjalankan seeder database.
  - `ngapakin migrate:status`: Menampilkan tabel ringkasan status eksekusi seluruh berkas migrasi beserta batch nomornya.
- **Pagination & Offset ORM/QueryBuilder**:
  - Dukungan klausa `OFFSET` via `QueryBuilder.lewati(jumlah)` / `offset(jumlah)`.
  - Fitur pagination otomatis via `Model.kaca(saben_kaca, kaca_saiki)` / `Model.paginate(...)` lengkap dengan metadata (`total`, `kaca_pungkasan`, `ana_sadurunge`, `ana_sabanjure`).
- **Rate Limiting / Throttle Middleware**:
  - Middleware pembatas request `throttle:maks_request,menit` (default 60 request per menit per IP).
  - Integrasi header HTTP standar: `Retry-After`, `X-RateLimit-Limit`, dan `X-RateLimit-Remaining`.
  - Dukungan respons ramah pengguna (JSON untuk API atau halaman HTML untuk browser).
- **Dukungan Basis Data SQL Server (MSSQL)**:
  - Driver `SQLServerDriver` baru yang mendukung koneksi via `pymssql` maupun `pyodbc` (ODBC Driver 18).
  - Penyesuaian sintaksis identitas auto-increment (`SCOPE_IDENTITY()`), tanda kurung bracket `[tabel]`, dan pembersihan relasi saat `migrate:fresh`.
  - Dukungan instalasi opsional via `pip install 'ngapakin[mssql]'`.
- **Larapak Route & API Studio (`/api-studio` & `/api/studio`)**:
  - Dokumentasi rute interaktif otomatis yang membaca seluruh endpoint, parameter dinamis (`{id}`), dan middleware tanpa konfigurasi manual.
  - Dukungan penuh untuk rute **View (HTML)** maupun **API (JSON)** dengan tab **Pratinjau Tampilan (Live View)** via isolated responsive iframe sandbox (Desktop / Tablet / Mobile).
  - Sandbox pengujian permintaan (*Try It Out*) dengan injeksi otomatis token proteksi CSRF untuk method `POST`, `PUT`, `PATCH`, dan `DELETE`.
  - Endpoint spesifikasi standar **OpenAPI 3.0.3** otomatis di `/api-studio/openapi.json`.
  - Antarmuka visual berestetika tinggi (Dark OLED, Doppelrand double-bezel, tipografi tajam, zero AI-slop) berlandaskan panduan `/frontend-design` & `/design-taste-frontend`.

## [1.0.6] - 2026-10-30

### Ditambahkan
- **Scaffolding Proyek Multi-Bahasa (`ngapakin new`)**:
  - Penambahan opsi flag `--bahasa=ngapak|indonesia|english` (dan alias `--lang`, `--language`, `-b`).
  - Pembuatan struktur folder dinamis sesuai dialek/bahasa:
    - Dialek Ngapak: `jeroan/`, `lumbung/`, `dalan/`, `sawangan/`, `njobo/`.
    - Bahasa Indonesia: `aplikasi/`, `basisdata/`, `rute/`, `tampilan/`, `publik/`.
    - English standard: `app/`, `database/`, `routes/`, `resources/views/`, `public/`.
  - Integrasi deteksi otomatis bahasa proyek pada perintah CLI (`make:*`, `migrate`, `serve`).
- **Template Welcome Page & Assets**:
  - Penyematan inline aset base64 logo dan CSS pada template awal agar terisolasi dan anti-rusak saat diinstal via pip.

## [1.0.0] - 2026-05-28

### Ditambahkan
- **Ecosystem Core (Phase 5)**:
  - Autentikasi (`Auth`) mendukung `mlebu` (login), `metu` (logout), `cek`, dan `user`.
  - Manajemen Sesi (`Session`) terintegrasi penuh ke HTTP Request lifecycle dan database SQLite.
  - Helper Cookies parsing request & response header.
  - Engine Validasi (`Validator`) mendukung aturan `required`, `email`, `numeric`, `min`, dan `max`.
  - Sistem Cache terdistribusi berbasis SQLite dengan kadaluarsa (TTL).
  - Event Dispatcher & Listener mendukung pemanggilan fungsi Ngapak VM secara real-time.
  - Job Queue bertenaga SQL dengan runner worker `queue:work`.
  - Package Manager & Auto-discovery Service Provider.
  - REPL terminal interaktif via `python ngapakin.py repl`.
  - Breakpoint debugger interaktif (`s` step, `c` continue, `l` locals, `g` globals).
  - VSCode extension grammar & Language Server Protocol (LSP) diagnostics.
- **ORM & Database (Phase 4)**:
  - Pengenalan OOP `kelas extends Model`.
  - Fluent SQL Query Builder.
  - Schema builder migrasi database (`schema.gawe`, `schema.buang`).
  - Autoloading Model.
- **MVC Framework Larapak (Phase 3)**:
  - Web router, Controller loader, HTTP Server, Blade-like Template Engine.
