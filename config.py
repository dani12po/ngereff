# Configuration for browser automation agent

BASE_URL = "https://thenanobutton.com/"
REFERRAL_USERNAME = "danixyz"  # Contoh: username referral Anda
USE_REFERRAL = True
UNIT = "dollars"  # Unit parameter untuk URL

# Browser settings
HEADLESS = False  # Set True untuk headless mode
TIMEOUT = 30000  # milliseconds
VIEWPORT = {"width": 1920, "height": 1080}

# DNS Configuration (untuk variasi IP)
DNS_SERVERS = [
    ["8.8.8.8", "8.8.4.4"],          # Google DNS
    ["208.67.222.222", "208.67.220.220"],  # OpenDNS
    ["1.1.1.1", "1.0.0.1"]           # Cloudflare DNS
]
USE_DNS_ROTATION = True

# Proxy configuration (optional)
USE_PROXY = False  # Set True untuk gunakan proxy
PROXY_SERVER = ""  # Contoh: "http://proxy.example.com:8080"
PROXY_USERNAME = ""
PROXY_PASSWORD = ""

# Proxy rotation (untuk variasi IP)
USE_PROXY_ROTATION = True  # Set True untuk rotasi proxy
PROXY_LIST = [
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-1", "password": "nqf6slu7ws2l"},
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-2", "password": "nqf6slu7ws2l"},
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-3", "password": "nqf6slu7ws2l"},
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-4", "password": "nqf6slu7ws2l"},
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-5", "password": "nqf6slu7ws2l"},
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-6", "password": "nqf6slu7ws2l"},
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-7", "password": "nqf6slu7ws2l"},
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-8", "password": "nqf6slu7ws2l"},
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-9", "password": "nqf6slu7ws2l"},
    {"server": "http://p.webshare.io:80", "username": "wpsvwswv-10", "password": "nqf6slu7ws2l"},
]

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Screenshot settings
SCREENSHOT_ON_ERROR = True
SCREENSHOT_DIR = "screenshots"

# Click settings
CLICK_COUNT = 50  # Jumlah klik pada button Nano
CLICK_DELAY = 0.05  # Delay antar klik (50ms - lebih lambat agar lebih reliable)
WAIT_FOR_DOLLAR = 3  # Tunggu untuk melihat dollar amount (seconds)

# Multi-browser settings
MAX_CONCURRENT_BROWSERS = 5  # Maksimal browser yang berjalan bersamaan
USE_MULTI_BROWSER = True  # Set True untuk menjalankan multiple browser

# CAPTCHA settings
CAPTCHA_WAIT_TIMEOUT = 30  # seconds
CAPTCHA_CHECK_INTERVAL = 1  # seconds
CAPTCHA_CHECKBOX_POSITION = (843, 679)  # Posisi checkbox "Buktikan bahwa Anda adalah manusia"
CAPTCHA_CLICK_DELAY = 1  # Delay setelah klik checkbox (1 detik)
MAX_CAPTCHA_ATTEMPTS = 1  # Hanya 1x klik CAPTCHA, langsung lanjut
SUCCESS_WAIT_TIMEOUT = 3  # seconds untuk tunggu success message (dipercepat)
SKIP_SUCCESS_CHECK = True  # Skip pengecekan success message biar lebih cepat

# Loop settings
AUTO_RESTART = True  # Restart otomatis setelah selesai
RESTART_DELAY = 3  # Delay sebelum restart (seconds) - diperlambat untuk stability

# Nano button position (fallback jika selector gagal)
NANO_BUTTON_POSITION = (350, 430)
