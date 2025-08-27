# ========================
# USER CONFIGURATION FILE
# ========================
# Easy settings for non-technical users!
# Just change the values below - no code editing needed!

# App Settings
APP_NAME = "File Share"
APP_VERSION = "1.0"
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True

# File Upload Settings
MAX_FILE_SIZE = 1000* 1024 * 1024  # 1000MB in bytes
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "doc", "docx", "xls", "xlsx", "mp4", "log","mkv","bat"}
UPLOAD_FOLDER = "uploads"
LOG_FOLDER = "logs"

# Server Timeout Settings (for large files)
MAX_UPLOAD_TIME = 3600  # 1 hour in seconds
SERVER_TIMEOUT = 3600   # 1 hour in seconds

# User Accounts (Add new users here!)
USERS = {
    "admin": {
        "password": "admin123", 
        "role": "admin"
    },
    "user": {
        "password": "user123", 
        "role": "user"
    },
}

# Theme Settings
BACKGROUND_GRADIENT = "linear-gradient(135deg, #74ebd5, #9face6)"
PRIMARY_COLOR = "#5a67d8"
ACCENT_COLOR = "#48bb78"

# Security Settings
SESSION_TIMEOUT = 60  # minutes
LOGIN_ATTEMPTS = 5

# SECURITY SETTINGS - BE CAREFUL WITH THESE!
SECURITY = {
    "allowed_networks": ["192.168.1.0/24"],  # Only your home network
    "bind_interface": "auto",  # "auto", "localhost", or "192.168.1.105"
    "admin_require_local": True,  # Admin panel only from local network
    "disable_debug_in_production": True
}