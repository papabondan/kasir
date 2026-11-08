import os
from pathlib import Path

# ============================================================
# DIREKTORI APLIKASI
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

FOLDER_NOTA = BASE_DIR / "Nota"
FOLDER_NOTA.mkdir(parents=True, exist_ok=True)

# ============================================================
# INFORMASI APLIKASI
# ============================================================

APP_NAME = "Caffe Kita"
APP_VERSION = "1.0.0"

# ============================================================
# KONFIGURASI TAMPILAN
# ============================================================

THEME_MODE = "Light"
COLOR_THEME = "blue"

# ============================================================
# INFORMASI USAHA
# ============================================================

NAMA_USAHA = "Caffe Kita"
ALAMAT_USAHA = "Jl. Bantaran 1 Gg 1A no 17 Malang"

# ============================================================
# DATABASE
# ============================================================

DATABASE_NAME = "caffe_kita.db"
DATABASE_PATH = BASE_DIR / DATABASE_NAME

# ============================================================
# NOTA
# ============================================================

LEBAR_NOTA_THERMAL = 58

# ============================================================
# KONFIGURASI EMAIL SMTP GMAIL
# ============================================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_PENGIRIM = os.getenv("EMAIL_PENGIRIM", "")
PASSWORD_APLIKASI = os.getenv("PASSWORD_APLIKASI", "")
