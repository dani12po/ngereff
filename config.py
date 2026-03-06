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
    # Webshare.io proxies (10 proxies)
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
    
    # Backup proxies (10 proxies)
    {"server": "http://31.59.20.176:6754", "username": "uarfrzyh", "password": "w1csugrzhvlh"},
    {"server": "http://23.95.150.145:6114", "username": "uarfrzyh", "password": "w1csugrzhvlh"},
    {"server": "http://198.23.239.134:6540", "username": "uarfrzyh", "password": "w1csugrzhvlh"},
    {"server": "http://45.38.107.97:6014", "username": "uarfrzyh", "password": "w1csugrzhvlh"},
    {"server": "http://107.172.163.27:6543", "username": "uarfrzyh", "password": "w1csugrzhvlh"},
    {"server": "http://198.105.121.200:6462", "username": "uarfrzyh", "password": "w1csugrzhvlh"},
    {"server": "http://64.137.96.74:6641", "username": "uarfrzyh", "password": "w1csugrzhvlh"},
    {"server": "http://216.10.27.159:6837", "username": "uarfrzyh", "password": "w1csugrzhvlh"},
    {"server": "http://142.111.67.146:5611", "username": "uarfrzyh", "password": "w1csugrzhvlh"},
    {"server": "http://194.39.32.164:6461", "username": "uarfrzyh", "password": "w1csugrzhvlh"},
]

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Screenshot settings
SCREENSHOT_ON_ERROR = False  # Disable screenshot untuk hemat disk space
SCREENSHOT_DIR = "screenshots"

# Click settings
CLICK_COUNT = 200  # Jumlah klik pada button Nano (dinaikkan karena akan terus klik sampai tidak ada notif)
CLICK_DELAY = 0.35  # Delay antar klik (350ms) - default sebelum terdeteksi sukses
CLICK_DELAY_RANDOM = True  # Randomize delay untuk lebih natural
CLICK_DELAY_MIN = 0.25  # Minimum delay (250ms) - lebih lambat untuk avoid detection
CLICK_DELAY_MAX = 0.5  # Maximum delay (500ms) - lebih lambat untuk avoid detection
CLICK_DELAY_FAST_MIN = 0.08  # Fast delay setelah terdeteksi sukses (80ms)
CLICK_DELAY_FAST_MAX = 0.12  # Fast delay setelah terdeteksi sukses (120ms)
CLICK_BATCH_SIZE = 10  # Jumlah klik per batch sebelum istirahat
CLICK_BATCH_REST = 2  # Istirahat antar batch (seconds)
CLICK_CHECK_INTERVAL = 5  # Cek notif hijau setiap X klik
WAIT_FOR_DOLLAR = 3  # Tunggu untuk melihat dollar amount (seconds)

# Multi-browser settings
MAX_CONCURRENT_BROWSERS = 5  # Maksimal browser yang berjalan bersamaan
USE_MULTI_BROWSER = True  # Set True untuk menjalankan multiple browser
BROWSER_TIMEOUT = 300  # Timeout per browser dalam detik (5 menit) - diabaikan jika klik sukses
BROWSER_LAUNCH_DELAY = 10  # Delay antar launch browser (detik) untuk avoid rate limit
IGNORE_TIMEOUT_ON_SUCCESS = True  # Abaikan timeout jika klik berhasil (hijau terdeteksi)

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
