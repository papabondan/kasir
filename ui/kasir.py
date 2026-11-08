
import customtkinter as ctk

from config import NAMA_USAHA
from ui.login import LoginWindow


class KasirWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(f"{NAMA_USAHA} - POS System")
        self.geometry("780x560")
        self.resizable(False, False)

        # Status pengguna
        self.username_aktif = None
        self.role_aktif = None

        # Keranjang belanja
        self.keranjang_belanja = []

        self.buat_ui_kasir()

        # Tampilkan login
        self.after(
            100,
            self.tampilkan_login
        )

    def buat_ui_kasir(self):

        # Header
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.lbl_status = ctk.CTkLabel(
            self.top_frame,
            text="Status: Silakan Login",
            font=ctk.CTkFont(weight="bold")
        )
        self.lbl_status.pack(
            side="left",
            padx=15,
            pady=10
        )

        # Area utama
        self.workspace = ctk.CTkFrame(self)
        self.workspace.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

    def tampilkan_login(self):

        self.login_window = LoginWindow(self)

    def set_aktif_user(self, username, role):

        self.username_aktif = username
        self.role_aktif = role

        self.lbl_status.configure(
            text=f"Kasir Aktif: {username} ({role})"
        )

        # Nanti area transaksi dan hak akses
        # diaktifkan setelah login berhasil.
