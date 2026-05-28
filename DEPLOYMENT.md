# Panduan Deploy Larapak Web Framework 🌐

Dokumen ini menjelaskan langkah-langkah untuk melakukan deployment aplikasi web berbasis Larapak / NgapakIn ke internet agar dapat diakses oleh publik.

---

## 📌 Metode 1: Menggunakan PaaS (Render / Railway) - REKOMENDASI ⭐

Metode ini adalah yang termudah karena terintegrasi langsung dengan repositori GitHub Anda (auto-deploy saat push) dan menangani HTTPS (SSL) secara otomatis secara gratis.

### Langkah-langkah di Render.com:
1. Daftar atau masuk ke **[Render](https://render.com/)**.
2. Klik tombol **New +** dan pilih **Web Service**.
3. Hubungkan akun GitHub Anda dan pilih repositori `ngapakin`.
4. Konfigurasikan detail web service berikut:
   - **Name**: `ngapakin-app` (atau nama pilihan Anda)
   - **Environment/Runtime**: `Python`
   - **Build Command**: `pip install -e .` (untuk memasang CLI secara lokal)
   - **Start Command**: `python ngapakin.py serve $PORT`
5. Klik **Create Web Service**.

> [!NOTE]
> Larapak secara otomatis membaca `$PORT` yang disediakan oleh Render melalui argumen terminal saat server dijalankan.

---

## 📌 Metode 2: Menggunakan VPS Linux (Ubuntu 20.04/22.04)

Untuk performa penuh dan kontrol database SQLite yang lebih baik, Anda bisa menggunakan VPS seperti AWS, DigitalOcean, atau Linode.

### 1. Persiapan Awal
Masuk ke VPS Anda melalui SSH, perbarui sistem, dan kloning repositori:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git nginx -y

# Clone repositori
git clone https://github.com/IlhamHattaManggala/ngapakin.git /var/www/ngapakin
cd /var/www/ngapakin

# Inisialisasi database migrasi & seeder
python3 ngapakin.py migrate
python3 ngapakin.py db:seed
```

### 2. Konfigurasi Systemd Service (Agar berjalan di latar belakang)
Buat berkas service systemd baru agar Larapak tetap menyala walaupun sesi terminal ditutup, dan otomatis menyala kembali jika VPS reboot:

```bash
sudo nano /etc/systemd/system/larapak.service
```

Masukkan konfigurasi berikut:
```ini
[Unit]
Description=Larapak Web Server Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/ngapakin
ExecStart=/usr/bin/python3 ngapakin.py serve 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Aktifkan dan jalankan service:
```bash
sudo systemctl enable larapak
sudo systemctl start larapak
# Periksa status
sudo systemctl status larapak
```

### 3. Konfigurasi Nginx sebagai Reverse Proxy & SSL
Buka konfigurasi server block Nginx default:
```bash
sudo nano /etc/nginx/sites-available/default
```

Ganti isinya menjadi konfigurasi reverse proxy yang mengarah ke port `8000`:
```nginx
server {
    listen 80;
    server_name domain_anda.com www.domain_anda.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Uji konfigurasi dan muat ulang Nginx:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Mengaktifkan SSL Gratis (Let's Encrypt)
Gunakan Certbot untuk mengamankan koneksi (HTTPS) secara gratis:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d domain_anda.com -d www.domain_anda.com
```
Ikuti instruksi di layar, dan Certbot akan otomatis mengonfigurasi SSL pada Nginx Anda!

---

## 💾 Manajemen Database SQLite saat Production
Karena Larapak menggunakan SQLite (`database.sqlite`), pastikan berkas database memiliki izin akses yang tepat agar server web (`www-data`) dapat melakukan operasi penulisan (write):
```bash
sudo chown -R www-data:www-data /var/www/ngapakin
sudo chmod -R 775 /var/www/ngapakin/database
```
