# Catatan Perubahan (Changelog)

Semua perubahan besar pada proyek NgapakIn akan dicatat di dokumen ini.

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
