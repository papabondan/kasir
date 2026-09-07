import os
import random
import smtplib
import sqlite3
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
import pandas as pd


# ============================================================
# KONFIGURASI APLIKASI
# ============================================================

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

NAMA_USAHA = "Caffe Kita"
ALAMAT_USAHA = "Jl. Bantaran 1 Gg 1A no 17 Malang"
DATABASE_NAME = "caffe_kita.db"
LEBAR_NOTA_THERMAL = 58
FOLDER_NOTA = "Nota"


# Buat folder Nota otomatis jika belum ada
if not os.path.exists(FOLDER_NOTA):
    os.makedirs(FOLDER_NOTA)


# ============================================================
# KONFIGURASI EMAIL SMTP GMAIL
# ============================================================

SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
EMAIL_PENGIRIM = "akun@gmail"
PASSWORD_APLIKASI = "pasword aplikasi"


# ============================================================
# INISIALISASI DATABASE
# ============================================================

def inisialisasi_database():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()

        # Tabel Produk
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_barang TEXT UNIQUE NOT NULL,
                harga INTEGER NOT NULL,
                stok INTEGER NOT NULL
            )
        """)

        # Tabel User
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL
            )
        """)

        # Tabel Riwayat Transaksi Penjualan
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT NOT NULL,
                id_nota TEXT NOT NULL,
                nama_barang TEXT NOT NULL,
                harga INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                subtotal INTEGER NOT NULL,
                kasir TEXT NOT NULL
            )
        """)

        # User Default jika tabel kosong
        cursor.execute("SELECT COUNT(*) FROM user")

        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO user
                (username, password, email, role)
                VALUES (?, ?, ?, ?)
                """,
                (
                    "owner",
                    "owner123",
                    "sdijatim@gmail.com",
                    "Admin",
                ),
            )

            cursor.execute(
                """
                INSERT INTO user
                (username, password, email, role)
                VALUES (?, ?, ?, ?)
                """,
                (
                    "kasir1",
                    "kasir123",
                    "sdijatim@gmail.com",
                    "Kasir",
                ),
            )

            conn.commit()


# ============================================================
# KIRIM EMAIL OTP
# ============================================================

def kirim_email_otp(email_tujuan, username, otp_code):
    msg = MIMEMultipart()

    msg["From"] = EMAIL_PENGIRIM
    msg["To"] = email_tujuan
    msg["Subject"] = (
        f"Reset Password Akun {username} - {NAMA_USAHA}"
    )

    body = (
        f"Halo {username},\n\n"
        f"Berikut adalah kode OTP verifikasi untuk mereset "
        f"password Anda:\n\n"
        f"    >> {otp_code} <<\n\n"
        f"Jangan bagikan kode ini kepada siapa pun.\n\n"
        f"Salam,\n"
        f"Sistem Keamanan {NAMA_USAHA}"
    )

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(
                EMAIL_PENGIRIM,
                PASSWORD_APLIKASI,
            )
            server.sendmail(
                EMAIL_PENGIRIM,
                email_tujuan,
                msg.as_string(),
            )

        return True

    except Exception as error:
        print(f"Gagal mengirim email: {error}")
        return False


# ============================================================
# JENDELA LOGIN
# ============================================================

class JendelaLogin(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("Login Sistem")
        self.geometry("380x320")
        self.resizable(False, False)
        self.grab_set()

        self.buat_ui()

    def buat_ui(self):
        lbl_judul = ctk.CTkLabel(
            self,
            text="Sistem Kasir",
            font=ctk.CTkFont(
                size=20,
                weight="bold",
            ),
        )
        lbl_judul.pack(pady=(25, 15))

        self.txt_username = ctk.CTkEntry(
            self,
            placeholder_text="Username",
            width=240,
        )
        self.txt_username.pack(pady=8)

        self.txt_password = ctk.CTkEntry(
            self,
            placeholder_text="Password",
            show="*",
            width=240,
        )
        self.txt_password.pack(pady=8)

        self.txt_password.bind(
            "<Return>",
            lambda event: self.proses_login(),
        )

        btn_login = ctk.CTkButton(
            self,
            text="Masuk ke Sistem",
            width=240,
            command=self.proses_login,
        )
        btn_login.pack(pady=15)

        btn_lupa = ctk.CTkButton(
            self,
            text="Lupa Password?",
            fg_color="transparent",
            text_color="#1565C0",
            hover_color="#E3F2FD",
            command=self.proses_lupa_password,
        )
        btn_lupa.pack()

    def proses_login(self):
        username = self.txt_username.get().strip()
        password = self.txt_password.get().strip()

        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT role
                FROM user
                WHERE username = ? AND password = ?
                """,
                (username, password),
            )

            user_data = cursor.fetchone()

        if user_data:
            role_user = user_data[0]

            messagebox.showinfo(
                "Berhasil",
                f"Selamat Datang, {username}",
                parent=self,
            )

            self.destroy()
            self.parent.set_aktif_user(
                username,
                role_user,
            )

        else:
            messagebox.showerror(
                "Gagal",
                "Username atau Password salah!",
                parent=self,
            )

    def proses_lupa_password(self):
        dialog_user = ctk.CTkInputDialog(
            text="Masukkan Username Anda:",
            title="Lupa Password",
        )

        username = dialog_user.get_input()

        if not username:
            return

        username = username.strip()

        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT email FROM user WHERE username = ?",
                (username,),
            )

            data = cursor.fetchone()

        if not data:
            messagebox.showerror(
                "Error",
                "Username tidak ditemukan!",
                parent=self,
            )
            return

        email_tujuan = data[0]
        otp = str(random.randint(100000, 999999))

        messagebox.showinfo(
            "OTP",
            f"Mengirim kode verifikasi ke {email_tujuan}...",
            parent=self,
        )

        if kirim_email_otp(
            email_tujuan,
            username,
            otp,
        ):
            dialog_otp = ctk.CTkInputDialog(
                text="Masukkan 6 digit kode OTP:",
                title="Verifikasi",
            )

            if dialog_otp.get_input() == otp:
                dialog_pass = ctk.CTkInputDialog(
                    text="Masukkan Password Baru:",
                    title="Reset",
                )

                pw_baru = dialog_pass.get_input()

                if pw_baru and pw_baru.strip() != "":
                    with sqlite3.connect(DATABASE_NAME) as conn:
                        cursor = conn.cursor()

                        cursor.execute(
                            """
                            UPDATE user
                            SET password = ?
                            WHERE username = ?
                            """,
                            (
                                pw_baru.strip(),
                                username,
                            ),
                        )

                        conn.commit()

                    messagebox.showinfo(
                        "Sukses",
                        "Password berhasil diubah!",
                        parent=self,
                    )

            else:
                messagebox.showerror(
                    "Gagal",
                    "Kode OTP salah!",
                    parent=self,
                )

        else:
            messagebox.showerror(
                "Gagal",
                "Gagal mengirim email verifikasi.",
                parent=self,
            )


# ============================================================
# JENDELA KELOLA STOK (ADMIN ONLY)
# ============================================================

class JendelaKelolaStok(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title("Kelola Stok Barang")
        self.geometry("550x500")
        self.resizable(False, False)
        self.grab_set()

        self.buat_ui()
        self.muat_produk()

    def buat_ui(self):
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(
            fill="x",
            padx=15,
            pady=15,
        )

        self.txt_nama = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Nama Menu",
            width=200,
        )
        self.txt_nama.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
        )

        self.txt_harga = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Harga",
            width=120,
        )
        self.txt_harga.grid(
            row=0,
            column=1,
            padx=10,
            pady=10,
        )

        self.txt_stok = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Stok",
            width=80,
        )
        self.txt_stok.grid(
            row=0,
            column=2,
            padx=10,
            pady=10,
        )

        self.btn_simpan = ctk.CTkButton(
            self.form_frame,
            text="Simpan",
            fg_color="#2E7D32",
            command=self.simpan_produk,
        )
        self.btn_simpan.grid(
            row=0,
            column=3,
            padx=10,
            pady=10,
        )

        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15),
        )

        self.tabel = ttk.Treeview(
            self.table_frame,
            columns=("ID", "Nama", "Harga", "Stok"),
            show="headings",
            height=10,
        )

        self.tabel.heading("ID", text="ID")
        self.tabel.heading("Nama", text="Nama Menu")
        self.tabel.heading("Harga", text="Harga")
        self.tabel.heading("Stok", text="Stok")

        self.tabel.column(
            "ID",
            width=40,
            anchor="center",
        )
        self.tabel.column(
            "Nama",
            width=220,
        )
        self.tabel.column(
            "Harga",
            width=120,
            anchor="e",
        )
        self.tabel.column(
            "Stok",
            width=60,
            anchor="center",
        )

        self.tabel.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5,
        )

        self.tabel.bind(
            "<ButtonRelease-1>",
            self.pilih_baris,
        )

        self.btn_hapus = ctk.CTkButton(
            self,
            text="Hapus Terpilih",
            fg_color="#C62828",
            command=self.hapus_produk,
        )
        self.btn_hapus.pack(
            pady=5,
            padx=25,
            anchor="e",
        )

    def muat_produk(self):
        for item in self.tabel.get_children():
            self.tabel.delete(item)

        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, nama_barang, harga, stok
                FROM produk
                """
            )

            for r in cursor.fetchall():
                self.tabel.insert(
                    "",
                    "end",
                    values=(
                        r[0],
                        r[1],
                        f"Rp {r[2]:,}".replace(",", "."),
                        r[3],
                    ),
                )

        self.parent.perbarui_dropdown_kasir()

    def pilih_baris(self, _event):
        sel = self.tabel.selection()

        if not sel:
            return

        val = self.tabel.item(
            sel,
            "values",
        )

        self.txt_nama.delete(0, "end")
        self.txt_nama.insert(0, val[1])

        self.txt_harga.delete(0, "end")
        self.txt_harga.insert(
            0,
            val[2].replace("Rp ", "").replace(".", ""),
        )

        self.txt_stok.delete(0, "end")
        self.txt_stok.insert(0, val[3])

    def simpan_produk(self):
        n = self.txt_nama.get().strip()
        h_raw = self.txt_harga.get().strip()
        s_raw = self.txt_stok.get().strip()

        if not n or not h_raw or not s_raw:
            return

        try:
            h = int(h_raw)
            s = int(s_raw)

            with sqlite3.connect(DATABASE_NAME) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO produk
                    (nama_barang, harga, stok)
                    VALUES (?, ?, ?)

                    ON CONFLICT(nama_barang)
                    DO UPDATE SET
                        harga = excluded.harga,
                        stok = excluded.stok
                    """,
                    (n, h, s),
                )

                conn.commit()

            self.muat_produk()

            self.txt_nama.delete(0, "end")
            self.txt_harga.delete(0, "end")
            self.txt_stok.delete(0, "end")

        except ValueError:
            messagebox.showerror(
                "Error",
                "Input harga/stok harus angka!",
            )

    def hapus_produk(self):
        sel = self.tabel.selection()

        if not sel:
            return

        val = self.tabel.item(
            sel,
            "values",
        )

        if messagebox.askyesno(
            "Hapus",
            f"Hapus {val[1]}?",
        ):
            with sqlite3.connect(DATABASE_NAME) as conn:
                conn.cursor().execute(
                    "DELETE FROM produk WHERE id = ?",
                    (val[0],),
                )

                conn.commit()

            self.muat_produk()


# ============================================================
# JENDELA UTAMA: INTERFACE TRANSAKSI KASIR
# ============================================================

class AplikasiKasir(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(
            f"{NAMA_USAHA} - POS System"
        )
        self.geometry("780x560")
        self.resizable(False, False)

        inisialisasi_database()

        self.username_aktif = None
        self.role_aktif = None
        self.keranjang_belanja = []

        self.buat_ui_kasir()

        self.after(
            100,
            lambda: JendelaLogin(self),
        )

    def buat_ui_kasir(self):
        # Top Panel
        self.top_frame = ctk.CTkFrame(
            self,
            height=50,
        )
        self.top_frame.pack(
            fill="x",
            padx=10,
            pady=5,
        )

        self.lbl_status = ctk.CTkLabel(
            self.top_frame,
            text="Status: Silakan Login",
            font=ctk.CTkFont(
                weight="bold",
            ),
        )
        self.lbl_status.pack(
            side="left",
            padx=15,
            pady=10,
        )

        # Tombol Download Laporan (Admin Only)
        self.btn_laporan = ctk.CTkButton(
            self.top_frame,
            text="Download Laporan Excel",
            fg_color="#E65100",
            state="disabled",
            command=self.download_laporan_keuangan,
        )
        self.btn_laporan.pack(
            side="right",
            padx=10,
            pady=10,
        )

        self.btn_kelola = ctk.CTkButton(
            self.top_frame,
            text="Kelola Stok (Admin)",
            state="disabled",
            command=lambda: JendelaKelolaStok(self),
        )
        self.btn_kelola.pack(
            side="right",
            padx=10,
            pady=10,
        )

        # Workspace Split
        self.workspace = ctk.CTkFrame(self)
        self.workspace.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5,
        )

        # Kiri Pane
        self.left_pane = ctk.CTkFrame(
            self.workspace,
            width=300,
        )
        self.left_pane.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5,
            pady=5,
        )

        ctk.CTkLabel(
            self.left_pane,
            text="Pilih Menu Kopi/Makanan:",
            font=ctk.CTkFont(
                size=13,
                weight="bold",
            ),
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 0),
        )

        self.drop_produk = ctk.CTkComboBox(
            self.left_pane,
            values=[],
            width=240,
        )
        self.drop_produk.pack(
            padx=15,
            pady=5,
        )

        self.txt_qty = ctk.CTkEntry(
            self.left_pane,
            placeholder_text="Jumlah Beli (Qty)",
            width=240,
        )
        self.txt_qty.pack(
            padx=15,
            pady=5,
        )

        self.btn_tambah = ctk.CTkButton(
            self.left_pane,
            text="Tambah ke Keranjang",
            fg_color="#1565C0",
            command=self.tambah_ke_keranjang,
        )
        self.btn_tambah.pack(
            padx=15,
            pady=10,
        )

        ctk.CTkLabel(
            self.left_pane,
            text="Total Belanja:",
            font=ctk.CTkFont(size=12),
        ).pack(
            anchor="w",
            padx=15,
            pady=(20, 0),
        )

        self.lbl_total_bayar = ctk.CTkLabel(
            self.left_pane,
            text="Rp 0",
            font=ctk.CTkFont(
                size=24,
                weight="bold",
            ),
            text_color="#C62828",
        )
        self.lbl_total_bayar.pack(
            anchor="w",
            padx=15,
            pady=2,
        )

        self.txt_bayar = ctk.CTkEntry(
            self.left_pane,
            placeholder_text="Nominal Uang Tunai",
            width=240,
        )
        self.txt_bayar.pack(
            padx=15,
            pady=10,
        )

        self.btn_cetak = ctk.CTkButton(
            self.left_pane,
            text="Bayar & Cetak Nota",
            fg_color="#2E7D32",
            height=40,
            font=ctk.CTkFont(
                weight="bold",
            ),
            command=self.proses_cetak_nota,
        )
        self.btn_cetak.pack(
            padx=15,
            pady=10,
        )

        # Kanan Pane
        self.right_pane = ctk.CTkFrame(
            self.workspace
        )
        self.right_pane.pack(
            side="right",
            fill="both",
            expand=True,
            padx=5,
            pady=5,
        )

        ctk.CTkLabel(
            self.right_pane,
            text="Daftar Item Belanja:",
            font=ctk.CTkFont(
                weight="bold",
            ),
        ).pack(
            anchor="w",
            padx=10,
            pady=5,
        )

        self.tabel_kasir = ttk.Treeview(
            self.right_pane,
            columns=(
                "Nama",
                "Harga",
                "Qty",
                "Subtotal",
            ),
            show="headings",
        )

        self.tabel_kasir.heading(
            "Nama",
            text="Menu",
        )
        self.tabel_kasir.heading(
            "Harga",
            text="Harga",
        )
        self.tabel_kasir.heading(
            "Qty",
            text="Qty",
        )
        self.tabel_kasir.heading(
            "Subtotal",
            text="Subtotal",
        )

        self.tabel_kasir.column(
            "Nama",
            width=150,
        )
        self.tabel_kasir.column(
            "Harga",
            width=80,
            anchor="e",
        )
        self.tabel_kasir.column(
            "Qty",
            width=40,
            anchor="center",
        )
        self.tabel_kasir.column(
            "Subtotal",
            width=90,
            anchor="e",
        )

        self.tabel_kasir.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5,
        )

        self.btn_bersih = ctk.CTkButton(
            self.right_pane,
            text="Kosongkan Keranjang",
            fg_color="#E65100",
            command=self.reset_keranjang,
        )
        self.btn_bersih.pack(
            anchor="e",
            padx=10,
            pady=5,
        )

    def set_aktif_user(self, username, role):
        self.username_aktif = username
        self.role_aktif = role

        self.lbl_status.configure(
            text=f"Kasir Aktif: {username} ({role})"
        )

        # Tombol khusus Admin/Owner aktif jika role sesuai
        is_admin = (
            "normal"
            if role == "Admin"
            else "disabled"
        )

        self.btn_kelola.configure(
            state=is_admin
        )
        self.btn_laporan.configure(
            state=is_admin
        )

        self.perbarui_dropdown_kasir()

    def perbarui_dropdown_kasir(self):
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT nama_barang
                FROM produk
                WHERE stok > 0
                """
            )

            daftar = [
                r[0]
                for r in cursor.fetchall()
            ]

        self.drop_produk.configure(
            values=daftar
        )

        if daftar:
            self.drop_produk.set(
                daftar[0]
            )
        else:
            self.drop_produk.set("")

    def tambah_ke_keranjang(self):
        menu = self.drop_produk.get()
        qty_in = self.txt_qty.get().strip()

        if not menu or not qty_in.isdigit():
            return

        qty = int(qty_in)

        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT harga, stok
                FROM produk
                WHERE nama_barang = ?
                """,
                (menu,),
            )

            prod = cursor.fetchone()

        if prod:
            harga = prod[0]
            stok_tersedia = prod[1]

            if qty > stok_tersedia:
                messagebox.showwarning(
                    "Stok Habis",
                    f"Stok kurang! Tersisa: {stok_tersedia}",
                )
                return

            subtotal = harga * qty

            self.keranjang_belanja.append(
                {
                    "nama": menu,
                    "harga": harga,
                    "qty": qty,
                    "subtotal": subtotal,
                }
            )

            self.tabel_kasir.insert(
                "",
                "end",
                values=(
                    menu,
                    f"{harga:,}",
                    qty,
                    f"{subtotal:,}",
                ),
            )

            self.hitung_total_belanja()

            self.txt_qty.delete(
                0,
                "end",
            )

    def hitung_total_belanja(self):
        total = sum(
            item["subtotal"]
            for item in self.keranjang_belanja
        )

        self.lbl_total_bayar.configure(
            text=f"Rp {total:,}".replace(",", ".")
        )

    def reset_keranjang(self):
        self.keranjang_belanja.clear()

        for i in self.tabel_kasir.get_children():
            self.tabel_kasir.delete(i)

        self.lbl_total_bayar.configure(
            text="Rp 0"
        )

        self.txt_bayar.delete(
            0,
            "end",
        )

    def proses_cetak_nota(self):
        if not self.keranjang_belanja:
            return

        total = sum(
            item["subtotal"]
            for item in self.keranjang_belanja
        )

        bayar_in = self.txt_bayar.get().strip()

        if (
            not bayar_in.isdigit()
            or int(bayar_in) < total
        ):
            messagebox.showwarning(
                "Gagal",
                "Uang pembayaran kurang atau salah input!",
            )
            return

        bayar = int(bayar_in)
        kembali = bayar - total

        waktu_sekarang = datetime.now()

        str_tanggal = waktu_sekarang.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        id_nota = waktu_sekarang.strftime(
            "NOTA%Y%m%d%H%M%S"
        )

        # ====================================================
        # PROSES UPDATE DB & SIMPAN TRANSAKSI
        # ====================================================

        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()

            for item in self.keranjang_belanja:
                # Kurangi stok barang
                cursor.execute(
                    """
                    UPDATE produk
                    SET stok = stok - ?
                    WHERE nama_barang = ?
                    """,
                    (
                        item["qty"],
                        item["nama"],
                    ),
                )

                # Catat ke riwayat transaksi keuangan
                cursor.execute(
                    """
                    INSERT INTO transaksi
                    (
                        tanggal,
                        id_nota,
                        nama_barang,
                        harga,
                        qty,
                        subtotal,
                        kasir
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str_tanggal,
                        id_nota,
                        item["nama"],
                        item["harga"],
                        item["qty"],
                        item["subtotal"],
                        self.username_aktif,
                    ),
                )

            conn.commit()

        # ====================================================
        # GENERATE TEKS STRUK NOTA
        # ====================================================

        garis_sama = "=" * LEBAR_NOTA_THERMAL
        garis_strip = "-" * LEBAR_NOTA_THERMAL

        isi_nota = []

        isi_nota.append(garis_sama)
        isi_nota.append(
            NAMA_USAHA.center(
                LEBAR_NOTA_THERMAL
            )
        )
        isi_nota.append(
            ALAMAT_USAHA.center(
                LEBAR_NOTA_THERMAL
            )
        )
        isi_nota.append(garis_strip)

        isi_nota.append(
            f"No Nota : {id_nota}".ljust(
                LEBAR_NOTA_THERMAL
            )
        )
        isi_nota.append(
            f"Tanggal : {str_tanggal}".ljust(
                LEBAR_NOTA_THERMAL
            )
        )
        isi_nota.append(
            f"Kasir   : {self.username_aktif}".ljust(
                LEBAR_NOTA_THERMAL
            )
        )

        isi_nota.append(garis_strip)

        for item in self.keranjang_belanja:
            isi_nota.append(
                f"{item['nama']}"
            )

            detail = (
                f"  {item['qty']} x "
                f"{item['harga']:,}"
            )

            sub_str = f"{item['subtotal']:,}"

            spasi = (
                LEBAR_NOTA_THERMAL
                - len(detail)
                - len(sub_str)
            )

            isi_nota.append(
                detail
                + (" " * spasi)
                + sub_str
            )

        isi_nota.append(garis_strip)

        isi_nota.append(
            f"TOTAL   : Rp {total:,}".rjust(
                LEBAR_NOTA_THERMAL
            )
        )
        isi_nota.append(
            f"TUNAI   : Rp {bayar:,}".rjust(
                LEBAR_NOTA_THERMAL
            )
        )
        isi_nota.append(
            f"KEMBALI : Rp {kembali:,}".rjust(
                LEBAR_NOTA_THERMAL
            )
        )

        isi_nota.append(garis_strip)

        isi_nota.append(
            "Terima Kasih Atas Kunjungan Anda!".center(
                LEBAR_NOTA_THERMAL
            )
        )

        isi_nota.append(garis_sama)

        teks_nota_lengkap = "\n".join(
            isi_nota
        )

        # 1. CETAK DI TERMINAL
        print(
            "\n"
            + teks_nota_lengkap
            + "\n"
        )

        # 2. SIMPAN SEBAGAI FILE TXT
        nama_file_nota = os.path.join(
            FOLDER_NOTA,
            f"{id_nota}.txt",
        )

        with open(
            nama_file_nota,
            "w",
        ) as file_nota:
            file_nota.write(
                teks_nota_lengkap
            )

        messagebox.showinfo(
            "Sukses",
            "Pembayaran berhasil!\n"
            f"Nota telah disimpan di folder "
            f"'{FOLDER_NOTA}/{id_nota}.txt'.",
        )

        self.reset_keranjang()
        self.perbarui_dropdown_kasir()

    def download_laporan_keuangan(self):
        """
        Fitur eksklusif Owner untuk mendownload
        riwayat penjualan ke format Excel.
        """

        # Minta lokasi penyimpanan file dari user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel Files", "*.xlsx")
            ],
            title="Simpan Laporan Keuangan",
            initialfile=(
                f"Laporan_Keuangan_"
                f"{datetime.now().strftime('%Y%m%d')}"
            ),
        )

        if not file_path:
            return

        try:
            with sqlite3.connect(
                DATABASE_NAME
            ) as conn:

                # Tarik seluruh riwayat pembukuan
                df = pd.read_sql_query(
                    """
                    SELECT *
                    FROM transaksi
                    ORDER BY id DESC
                    """,
                    conn,
                )

            if df.empty:
                messagebox.showwarning(
                    "Kosong",
                    "Belum ada riwayat transaksi "
                    "keuangan yang tercatat.",
                    parent=self,
                )
                return

            # Mengubah nama kolom di Excel
            df.columns = [
                "ID",
                "Waktu Transaksi",
                "ID Nota",
                "Nama Menu",
                "Harga Satuan",
                "Jumlah (Qty)",
                "Subtotal Pendapatan",
                "Kasir Operator",
            ]

            # Ekspor ke file Excel menggunakan pandas
            df.to_excel(
                file_path,
                index=False,
            )

            messagebox.showinfo(
                "Berhasil",
                "Laporan keuangan berhasil diunduh "
                "dan disimpan di:\n"
                f"{file_path}",
                parent=self,
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                "Gagal mengekspor laporan keuangan:\n"
                f"{e}",
                parent=self,
            )


# ============================================================
# MENJALANKAN APLIKASI
# ============================================================

if __name__ == "__main__":
    app = AplikasiKasir()
    app.mainloop()
