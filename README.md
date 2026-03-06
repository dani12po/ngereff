# 🤖 Nano Button Auto Clicker Bot

Bot otomatis untuk klik Nano button di thenanobutton.com menggunakan Playwright dengan fitur multi-browser dan proxy rotation.

## ✨ Fitur Utama

- 🚀 **Multi-Browser**: Jalankan hingga 5 browser bersamaan
- 🌐 **Proxy Rotation**: Setiap browser menggunakan proxy berbeda (IP berbeda)
- 🔐 **Auto CAPTCHA**: Deteksi dan klik Cloudflare Turnstile otomatis
- 🖱️ **Auto Click**: Klik Nano button 200x otomatis per browser
- 🔄 **Auto Restart**: Loop otomatis setelah selesai
- 📊 **Logging**: Log lengkap untuk monitoring
- 📸 **Screenshot**: Capture otomatis saat error

## 📋 Persyaratan

- Python 3.11 atau lebih tinggi
- Windows/Linux/Mac
- Koneksi internet
- Proxy list (sudah disediakan 10 proxy Webshare.io)

## 🚀 Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/dani12po/ngereff.git
cd ngereff
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Browser Chromium

```bash
playwright install chromium
```

## ⚙️ Konfigurasi

Edit file `config.py` untuk mengatur bot:

### Setting Referral (PENTING!)

Ganti dengan username referral Anda:

```python
# Referral settings
REFERRAL_USERNAME = "danixyz"  # ⬅️ GANTI INI dengan username referral Anda
USE_REFERRAL = True
UNIT = "dollars"
```

URL yang akan dibuka: `https://thenanobutton.com/danixyz?unit=dollars`

### Setting Multi-Browser

```python
# Multi-browser settings
USE_MULTI_BROWSER = True  # True = jalankan 5 browser sekaligus
MAX_CONCURRENT_BROWSERS = 5  # Maksimal 5 browser bersamaan
```

### Setting Klik

```python
# Click settings
CLICK_COUNT = 200  # Jumlah klik Nano button per browser
CLICK_DELAY = 0.05  # 50ms delay antar klik
```

### Setting CAPTCHA

```python
# CAPTCHA settings
MAX_CAPTCHA_ATTEMPTS = 1  # Hanya 1x klik CAPTCHA (cepat)
SKIP_SUCCESS_CHECK = True  # Skip pengecekan success message (lebih cepat)
```

### Setting Proxy

Bot sudah dilengkapi 10 proxy Webshare.io:

```python
PROXY_LIST = [
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-1", "password": "nqf6slu7ws2l"},
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-2", "password": "nqf6slu7ws2l"},
    # ... 8 proxy lainnya
]
```

Setiap browser akan menggunakan proxy berbeda secara otomatis.

## 🎮 Cara Menjalankan

### Mode Multi-Browser (Recommended)

Jalankan 5 browser sekaligus:

```bash
python main.py
```

Atau double-click file `run_bot.bat` (Windows)

### Mode Single Browser

Edit `config.py`, ubah:
```python
USE_MULTI_BROWSER = False
```

Lalu jalankan:
```bash
python main.py
```

### Custom Jumlah Browser

Jalankan 3 browser saja:
```bash
python main.py --browsers 3
```

### Mode Loop dengan Limit

Loop 10x lalu stop:
```bash
python main.py --iterations 10
```

## 📊 Cara Kerja Bot

1. **Launch Browser** - Buka browser dengan proxy berbeda
2. **Navigate** - Buka URL dengan referral Anda
3. **Auto CAPTCHA** - Klik CAPTCHA Cloudflare 1x
4. **Auto Click** - Klik Nano button 200x (10 detik)
5. **Screenshot** - Ambil screenshot hasil
6. **Restart** - Ulangi dengan proxy baru

### Timeline Per Browser:
- Load page: ~3 detik
- Klik CAPTCHA: ~1 detik
- Klik Nano 200x: ~10 detik
- **Total: ~15 detik per cycle**

### Multi-Browser (5 browser):
- Semua browser jalan bersamaan (parallel)
- 5 browser = 5x lebih cepat
- Setiap browser pakai IP berbeda

## 📁 Struktur Project

```
ngereff/
├── main.py                 # Entry point utama
├── multi_browser.py        # Controller multi-browser
├── agent.py                # Logic workflow
├── browser_controller.py   # Management browser
├── actions.py              # Aksi-aksi browser
├── config.py               # Konfigurasi (EDIT INI!)
├── logger.py               # System logging
├── requirements.txt        # Dependencies Python
├── run_bot.bat            # Shortcut Windows
├── .gitignore             # Git ignore
├── logs/                  # Folder log files
└── screenshots/           # Folder screenshot
```

## 🔧 Troubleshooting

### Browser tidak terbuka

```bash
playwright install chromium
```

Jika masih error:
```bash
playwright install --force chromium
```

### Proxy error

Cek username/password proxy di `config.py`. Pastikan proxy masih aktif.

### CAPTCHA tidak hilang

Bot akan klik 1x lalu lanjut. Jika masih ada CAPTCHA, bot tetap lanjut ke Nano klik.

### Error "Actions object has no attribute"

Pastikan semua file sudah ter-update. Coba pull ulang dari GitHub.

## 📝 Command Line Options

```bash
# Multi-browser mode (5 browser)
python main.py

# Custom jumlah browser
python main.py --browsers 3

# Single browser mode
python main.py --browsers 1

# Loop dengan limit
python main.py --iterations 10

# Loop tanpa batas
python main.py --loop
```

## 🎯 Tips & Trik

1. **Gunakan Multi-Browser** - Jalankan 5 browser untuk hasil maksimal
2. **Ganti Referral** - Jangan lupa ganti `REFERRAL_USERNAME` di `config.py`
3. **Monitor Log** - Cek folder `logs/` untuk melihat progress
4. **Cek Screenshot** - Lihat folder `screenshots/` untuk hasil
5. **Proxy Rotation** - Bot otomatis ganti proxy setiap restart

## ⚠️ Disclaimer

Bot ini dibuat untuk tujuan edukasi dan testing automation. Gunakan dengan bijak dan patuhi Terms of Service website yang dituju.

## 📄 License

MIT License - Bebas digunakan dan dimodifikasi

## 🤝 Kontribusi

Pull request dan issue welcome! Silakan fork dan contribute.

## 📧 Kontak

GitHub: [@dani12po](https://github.com/dani12po)

---

⭐ Jangan lupa star repo ini jika bermanfaat!
