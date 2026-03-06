# 🤖 Nano Button Auto Clicker Bot

Bot otomatis untuk klik Nano button di thenanobutton.com menggunakan Playwright dengan fitur multi-browser dan proxy rotation.

## ✨ Fitur Utama

- 🚀 **Sequential Browser Launch**: Buka browser satu per satu, max 5 browser berhasil
- 🌐 **Proxy Rotation**: Setiap browser menggunakan proxy berbeda (IP berbeda)
- 🔐 **Auto CAPTCHA**: Deteksi dan klik Cloudflare Turnstile otomatis
- 🖱️ **Smart Auto Click**: Klik lambat (250-500ms) di awal, cepat (80-120ms) setelah sukses
- ✅ **Success Detection**: Deteksi centang hijau +$0.00000001 otomatis
- 🚫 **Auto Close Failed**: Browser yang butuh referral langsung close
- 💰 **Balance Tracking**: Monitor balance via API session
- 💸 **Auto Withdraw**: Withdraw otomatis jika balance >= 0.00001 Nano
- 📊 **Logging**: Log lengkap untuk monitoring
- 🔄 **Infinite Loop**: Terus berjalan sampai dapat 5 browser berhasil

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
CLICK_DELAY_MIN = 0.25  # Delay minimum (250ms) - lambat di awal
CLICK_DELAY_MAX = 0.5  # Delay maximum (500ms) - lambat di awal
CLICK_DELAY_FAST_MIN = 0.08  # Delay cepat (80ms) - setelah sukses
CLICK_DELAY_FAST_MAX = 0.12  # Delay cepat (120ms) - setelah sukses
CLICK_BATCH_SIZE = 10  # Klik per batch
CLICK_BATCH_REST = 2  # Istirahat antar batch (seconds)
```

### Setting Withdraw (OPSIONAL)

```python
# Nano withdrawal settings
NANO_ADDRESS = ""  # ⬅️ ISI dengan alamat Nano Anda
AUTO_WITHDRAW = False  # Set True untuk auto-withdraw
WITHDRAW_THRESHOLD = 0.00001  # Minimum balance untuk withdraw
CHECK_BALANCE_INTERVAL = 50  # Cek balance setiap 50 klik
```

**Cara aktifkan auto-withdraw:**
1. Isi `NANO_ADDRESS` dengan alamat Nano Anda
2. Ubah `AUTO_WITHDRAW = True`
3. Bot akan auto-withdraw setiap balance >= 0.00001 Nano

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

### Sequential Browser Launch:
1. **Launch Browser 1** - Buka dengan proxy 1
2. **Cek Status** - Klik lambat (250-500ms) untuk avoid detection
3. **Deteksi Sukses** - Jika hijau +$0.00000001 terdeteksi:
   - Switch ke FAST MODE (80-120ms per klik)
   - Terus klik sampai tidak hijau lagi
   - Check balance setiap 50 klik
   - Auto-withdraw jika balance >= 0.00001
4. **Deteksi Gagal** - Jika "Please wait" tanpa hijau:
   - Browser langsung close
   - Launch Browser 2 sebagai pengganti
5. **Repeat** - Terus loop sampai dapat 5 browser berhasil

### Timeline Per Browser:
- **Browser Gagal**: ~5-10 detik (langsung close)
- **Browser Berhasil**: Berjalan terus sampai tidak hijau lagi (bisa 10+ menit)

### Multi-Browser Strategy:
- Max 5 browser berhasil berjalan bersamaan
- Browser gagal langsung diganti baru
- Setiap browser pakai IP berbeda (proxy rotation)
- Browser berhasil tetap berjalan sampai earning stop

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

1. **Aktifkan Auto-Withdraw** - Isi `NANO_ADDRESS` dan set `AUTO_WITHDRAW = True`
2. **Ganti Referral** - Jangan lupa ganti `REFERRAL_USERNAME` di `config.py`
3. **Monitor Log** - Cek folder `logs/` untuk melihat progress dan balance
4. **Biarkan Berjalan** - Bot akan terus loop sampai dapat 5 browser berhasil
5. **Proxy Rotation** - Bot otomatis ganti proxy untuk setiap browser baru
6. **Check Balance** - Bot akan log balance setiap 50 klik
7. **Withdraw Otomatis** - Bot akan withdraw otomatis jika balance >= 0.00001

## 🔍 Monitoring

### Log Messages:
- `✓✓✓ Click success confirmed! Switching to FAST MODE` - Browser berhasil
- `⚠️⚠️⚠️ BROWSER NEEDS REFERRAL - CLOSING IMMEDIATELY` - Browser gagal
- `Balance: X Nano` - Current balance
- `✓ Withdraw successful!` - Withdraw berhasil
- `📊 Status: X active, Y successful, Z failed` - Status keseluruhan

### Session Stats:
Bot akan log stats setiap browser selesai:
- Final balance
- Total earned
- Total clicks

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
