# Panduan Deployment Larapak Web Framework 🌐

Dokumen ini menjelaskan langkah-langkah untuk melakukan deployment aplikasi web berbasis Larapak / NgapakIn ke lingkungan produksi menggunakan standar industri Python WSGI (Gunicorn / uWSGI) maupun server development lokal.

---

## 📌 Ringkasan Mode Server

| Mode | Entrypoint / Perintah | Karakteristik | Target Penggunaan |
|---|---|---|---|
| **Development Server** | `python ngapakin.py serve [host] [port]` | Multi-threaded HTTP server bawaan Python, auto-reload & debugging ramah lokal | Pengembangan lokal (Local Dev) |
| **Production WSGI** | `gunicorn "framework.wsgi:app"` | Multi-worker process pooling, robust isolation, high-throughput | Lingkungan Produksi (VPS, Docker, Cloud) |

---

## 📌 Metode 1: Production Deployment Menggunakan WSGI & Gunicorn (Rekomendasi Produksi)

Larapak menyediakan adapter WSGI standar di `framework.wsgi:app` yang sepenuhnya kompatibel dengan server WSGI modern seperti Gunicorn dan uWSGI.

### 1. Pemasangan Dependency Produksi
```bash
pip install gunicorn
# Atau pasang bundle dependensi produksi:
pip install "ngapakin[production]"
```

### 2. Menjalankan Gunicorn
Jalankan aplikasi dengan worker proses terisolasi:
```bash
# Menjalankan dengan 4 worker pada port 8000
gunicorn --workers 4 --bind 0.0.0.0:8000 "framework.wsgi:app"
```

Untuk menentukan jumlah worker yang optimal, gunakan formula standar: `(2 x CPU Cores) + 1`.

---

## 📌 Metode 2: Deployment VPS Linux (Ubuntu / Debian) dengan Systemd & Nginx

### 1. Persiapan Direktori & Virtualenv
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git nginx -y

# Clone repositori
git clone https://github.com/IlhamHattaManggala/ngapakin.git /var/www/ngapakin
cd /var/www/ngapakin

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e ".[production,all]"

# Jalankan migrasi database
python3 ngapakin.py migrate
```

### 2. Konfigurasi Systemd Service untuk Gunicorn
Buat berkas service systemd:
```bash
sudo nano /etc/systemd/system/larapak.service
```

Isi berkas service:
```ini
[Unit]
Description=Larapak WSGI Gunicorn Application Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ngapakin
Environment="PATH=/var/www/ngapakin/venv/bin"
EnvironmentFile=/var/www/ngapakin/.env
ExecStart=/var/www/ngapakin/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/larapak/access.log \
    --error-logfile /var/log/larapak/error.log \
    "framework.wsgi:app"
Restart=always

[Install]
WantedBy=multi-user.target
```

Buat direktori log dan aktifkan service:
```bash
sudo mkdir -p /var/log/larapak && sudo chown -R www-data:www-data /var/log/larapak
sudo systemctl daemon-reload
sudo systemctl enable larapak
sudo systemctl start larapak
sudo systemctl status larapak
```

### 3. Konfigurasi Nginx sebagai Reverse Proxy & Static File Server
Buka konfigurasi Nginx:
```bash
sudo nano /etc/nginx/sites-available/larapak
```

Isi konfigurasi:
```nginx
server {
    listen 80;
    server_name domain_anda.com www.domain_anda.com;

    client_max_body_size 20M;

    # Melayani aset statis langsung melalui Nginx
    location /static/ {
        alias /var/www/ngapakin/public/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Reverse proxy ke Gunicorn WSGI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Aktifkan konfigurasi Nginx dan pasang SSL via Certbot:
```bash
sudo ln -s /etc/nginx/sites-available/larapak /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Pasang SSL gratis (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d domain_anda.com -d www.domain_anda.com
```

---

## 📌 Metode 3: PaaS (Render / Railway / Fly.io)

### Pengaturan di Render:
1. Hubungkan repositori GitHub Anda di **[Render](https://render.com/)**.
2. Konfigurasi:
   - **Environment**: `Python`
   - **Build Command**: `pip install -e ".[production]"`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT "framework.wsgi:app"`
3. Tambahkan environment variables sesuai kebutuhan (`APP_ENV=production`, `APP_KEY=...`).
