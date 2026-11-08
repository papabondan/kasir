
import customtkinter as ctk
from tkinter import messagebox


class LoginWindow(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("Login Sistem")
        self.geometry("380x320")
        self.resizable(False, False)
        self.grab_set()

        self.buat_ui()

    def buat_ui(self):

        # Judul
        ctk.CTkLabel(
            self,
            text="Sistem Kasir",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).pack(pady=(25, 15))

        # Username
        self.txt_username = ctk.CTkEntry(
            self,
            placeholder_text="Username",
            width=240
        )
        self.txt_username.pack(pady=8)

        # Password
        self.txt_password = ctk.CTkEntry(
            self,
            placeholder_text="Password",
            show="*",
            width=240
        )
        self.txt_password.pack(pady=8)

        self.txt_password.bind(
            "<Return>",
            lambda event: self.proses_login()
        )

        # Tombol login
        ctk.CTkButton(
            self,
            text="Masuk ke Sistem",
            width=240,
            command=self.proses_login
        ).pack(pady=15)

        # Lupa password
        ctk.CTkButton(
            self,
            text="Lupa Password?",
            fg_color="transparent",
            text_color="#1565C0",
            hover_color="#E3F2FD",
            command=self.proses_lupa_password
        ).pack()

    def proses_login(self):

        username = self.txt_username.get().strip()
        password = self.txt_password.get().strip()

        if not username or not password:
            messagebox.showwarning(
                "Peringatan",
                "Username dan password harus diisi!",
                parent=self
            )
            return

        # Autentikasi akan dihubungkan
        # dengan services/auth_service.py

        messagebox.showinfo(
            "Informasi",
            "Modul autentikasi belum dihubungkan.",
            parent=self
        )

    def proses_lupa_password(self):

        # Akan dihubungkan dengan otp_service.py

        messagebox.showinfo(
            "Informasi",
            "Modul reset password belum dihubungkan.",
            parent=self
        )
