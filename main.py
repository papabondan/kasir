
# ============================================================
# CAFFE KITA - POINT OF SALE
# MAIN APPLICATION
# ============================================================

import customtkinter as ctk
import sys

from config import (
    APP_NAME,
    APP_VERSION,
    THEME_MODE,
    COLOR_THEME
)

from database.schema import init_db
from ui.kasir import KasirWindow


# ============================================================
# INISIALISASI APLIKASI
# ============================================================

def setup_application():

    # Pengaturan tampilan
    ctk.set_appearance_mode(THEME_MODE)
    ctk.set_default_color_theme(COLOR_THEME)

    # Inisialisasi database
    init_db()


# ============================================================
# MENJALANKAN APLIKASI
# ============================================================

def main():

    try:

        # Persiapan aplikasi
        setup_application()

        # Membuat jendela utama
        app = KasirWindow()

        # Informasi aplikasi
        app.title(f"{APP_NAME} v{APP_VERSION}")

        # Menjalankan aplikasi
        app.mainloop()

    except KeyboardInterrupt:
        print("\nAplikasi dihentikan.")

    except Exception as error:
        print(f"\nTerjadi kesalahan: {error}")
        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
