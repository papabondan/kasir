
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from config import NAMA_USAHA
from printing.nota import buat_teks_nota, simpan_nota
from printing.thermal import cetak_nota
from services.laporan_service import (
    export_laporan_excel,
    get_jumlah_transaksi,
    get_total_pendapatan,
)
from services.produk_service import (
    get_all_produk,
    get_produk_tersedia,
    hapus_produk,
    simpan_produk,
)
from services.transaksi_service import (
    hitung_total,
    periksa_stok,
    proses_pembayaran,
)
from ui.login import LoginWindow
from utils.formatter import bersihkan_angka, format_rupiah


class KasirWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(f"{NAMA_USAHA} - POS System")
        self.geometry("920x620")
        self.resizable(False, False)

        # Status pengguna
        self.username_aktif = None
        self.role_aktif = None

        # Keranjang belanja
        self.keranjang_belanja = []
        self.produk_map = {}

        self.buat_ui_kasir()

        # Tampilkan login
        self.after(100, self.tampilkan_login)

    # ============================================================
    # UI UTAMA
    # ============================================================

    def buat_ui_kasir(self):
        # Header
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(
            fill="x",
            padx=10,
            pady=(10, 5),
        )

        self.lbl_status = ctk.CTkLabel(
            self.top_frame,
            text="Status: Silakan Login",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.lbl_status.pack(
            side="left",
            padx=15,
            pady=10,
        )

        self.btn_logout = ctk.CTkButton(
            self.top_frame,
            text="Ganti Akun / Logout",
            width=150,
            fg_color="#C62828",
            hover_color="#B71C1C",
            command=self.logout_user,
        )

        # Area utama
        self.workspace = ctk.CTkFrame(self)
        self.workspace.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(5, 10),
        )

    def tampilkan_login(self):
        self.login_window = LoginWindow(self)

    def logout_user(self):
        self.username_aktif = None
        self.role_aktif = None
        self.keranjang_belanja = []
        self.produk_map = {}

        self.lbl_status.configure(
            text="Status: Silakan Login"
        )
        self.btn_logout.pack_forget()

        for widget in self.workspace.winfo_children():
            widget.destroy()

        self.tampilkan_login()

    def set_aktif_user(self, username, role):
        self.username_aktif = username
        self.role_aktif = role

        self.lbl_status.configure(
            text=f"Kasir Aktif: {username} ({role})"
        )

        self.btn_logout.pack(
            side="right",
            padx=15,
            pady=8,
        )

        self.bangun_workspace()

    # ============================================================
    # MEMBANGUN AREA KERJA SESUAI ROLE
    # ============================================================

    def bangun_workspace(self):
        for widget in self.workspace.winfo_children():
            widget.destroy()

        self.tabview = ctk.CTkTabview(self.workspace)
        self.tabview.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        self.tab_transaksi = self.tabview.add("Transaksi Kasir")
        self.bangun_tab_transaksi()

        if self.role_aktif == "Admin":
            self.tab_produk = self.tabview.add("Kelola Produk")
            self.tab_laporan = self.tabview.add("Laporan Keuangan")

            self.bangun_tab_produk()
            self.bangun_tab_laporan()

        self.muat_ulang_data()

    # ============================================================
    # TAB 1: TRANSAKSI KASIR
    # ============================================================

    def bangun_tab_transaksi(self):
        # Frame atas: pilih produk dan jumlah
        frame_input = ctk.CTkFrame(self.tab_transaksi)
        frame_input.pack(
            fill="x",
            padx=10,
            pady=(5, 10),
        )

        ctk.CTkLabel(
            frame_input,
            text="Pilih Menu:",
        ).pack(
            side="left",
            padx=(10, 5),
            pady=10,
        )

        self.cmb_produk = ctk.CTkComboBox(
            frame_input,
            width=280,
            state="readonly",
            values=[],
        )
        self.cmb_produk.pack(
            side="left",
            padx=5,
            pady=10,
        )

        ctk.CTkLabel(
            frame_input,
            text="Jumlah:",
        ).pack(
            side="left",
            padx=(15, 5),
            pady=10,
        )

        self.txt_qty = ctk.CTkEntry(
            frame_input,
            width=70,
        )
        self.txt_qty.insert(0, "1")
        self.txt_qty.pack(
            side="left",
            padx=5,
            pady=10,
        )
        self.txt_qty.bind(
            "<Return>",
            lambda event: self.tambah_ke_keranjang(),
        )

        ctk.CTkButton(
            frame_input,
            text="+ Tambah ke Keranjang",
            command=self.tambah_ke_keranjang,
        ).pack(
            side="left",
            padx=15,
            pady=10,
        )

        # Frame tengah: tabel keranjang
        frame_tabel = ctk.CTkFrame(self.tab_transaksi)
        frame_tabel.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5,
        )

        kolom = ("nama", "harga", "qty", "subtotal")

        self.tree_keranjang = ttk.Treeview(
            frame_tabel,
            columns=kolom,
            show="headings",
            height=11,
        )

        self.tree_keranjang.heading("nama", text="Nama Menu")
        self.tree_keranjang.heading("harga", text="Harga Satuan")
        self.tree_keranjang.heading("qty", text="Qty")
        self.tree_keranjang.heading("subtotal", text="Subtotal")

        self.tree_keranjang.column("nama", width=340)
        self.tree_keranjang.column("harga", width=150, anchor="e")
        self.tree_keranjang.column("qty", width=80, anchor="center")
        self.tree_keranjang.column("subtotal", width=170, anchor="e")

        self.tree_keranjang.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0),
            pady=10,
        )

        scrollbar = ttk.Scrollbar(
            frame_tabel,
            orient="vertical",
            command=self.tree_keranjang.yview,
        )
        self.tree_keranjang.configure(
            yscrollcommand=scrollbar.set
        )
        scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 10),
            pady=10,
        )

        # Frame bawah: aksi keranjang dan pembayaran
        frame_bawah = ctk.CTkFrame(self.tab_transaksi)
        frame_bawah.pack(
            fill="x",
            padx=10,
            pady=(5, 5),
        )

        # Kiri: hapus item dan reset keranjang
        frame_kiri = ctk.CTkFrame(
            frame_bawah,
            fg_color="transparent",
        )
        frame_kiri.pack(
            side="left",
            padx=10,
            pady=10,
        )

        ctk.CTkButton(
            frame_kiri,
            text="Hapus Item Terpilih",
            fg_color="#E65100",
            hover_color="#EF6C00",
            width=150,
            command=self.hapus_item_keranjang,
        ).pack(pady=(0, 6))

        ctk.CTkButton(
            frame_kiri,
            text="Kosongkan Keranjang",
            fg_color="#616161",
            hover_color="#424242",
            width=150,
            command=self.kosongkan_keranjang,
        ).pack()

        # Kanan: total dan pembayaran
        frame_kanan = ctk.CTkFrame(
            frame_bawah,
            fg_color="transparent",
        )
        frame_kanan.pack(
            side="right",
            padx=15,
            pady=10,
        )

        self.lbl_total = ctk.CTkLabel(
            frame_kanan,
            text="Total Belanja: Rp 0",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.lbl_total.pack(
            anchor="e",
            pady=(0, 8),
        )

        baris_bayar = ctk.CTkFrame(
            frame_kanan,
            fg_color="transparent",
        )
        baris_bayar.pack(anchor="e")

        ctk.CTkLabel(
            baris_bayar,
            text="Uang Bayar (Rp):",
        ).pack(
            side="left",
            padx=(0, 8),
        )

        self.txt_bayar = ctk.CTkEntry(
            baris_bayar,
            width=160,
            placeholder_text="Contoh: 50000",
        )
        self.txt_bayar.pack(
            side="left",
            padx=(0, 10),
        )
        self.txt_bayar.bind(
            "<Return>",
            lambda event: self.proses_transaksi_bayar(),
        )

        ctk.CTkButton(
            baris_bayar,
            text="Bayar & Cetak Nota",
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            width=160,
            command=self.proses_transaksi_bayar,
        ).pack(side="left")

    def tambah_ke_keranjang(self):
        pilihan = self.cmb_produk.get()

        if not pilihan or pilihan not in self.produk_map:
            messagebox.showwarning(
                "Peringatan",
                "Pilih menu terlebih dahulu!",
                parent=self,
            )
            return

        qty_str = bersihkan_angka(self.txt_qty.get())

        if not qty_str or int(qty_str) <= 0:
            messagebox.showwarning(
                "Peringatan",
                "Jumlah pesanan minimal 1!",
                parent=self,
            )
            return

        qty_tambah = int(qty_str)
        produk = self.produk_map[pilihan]

        nama = produk["nama_barang"]
        harga = int(produk["harga"])

        # Cek apakah item sudah ada di keranjang
        item_ada = next(
            (
                item
                for item in self.keranjang_belanja
                if item["nama"] == nama
            ),
            None,
        )

        qty_baru = (
            item_ada["qty"] + qty_tambah
            if item_ada
            else qty_tambah
        )

        # Validasi stok ke database
        valid_stok, pesan_stok = periksa_stok(
            [{"nama": nama, "qty": qty_baru}]
        )

        if not valid_stok:
            messagebox.showwarning(
                "Stok Tidak Cukup",
                pesan_stok,
                parent=self,
            )
            return

        if item_ada:
            item_ada["qty"] = qty_baru
        else:
            self.keranjang_belanja.append(
                {
                    "nama": nama,
                    "harga": harga,
                    "qty": qty_baru,
                }
            )

        self.txt_qty.delete(0, "end")
        self.txt_qty.insert(0, "1")

        self.refresh_tabel_keranjang()

    def hapus_item_keranjang(self):
        terpilih = self.tree_keranjang.selection()

        if not terpilih:
            messagebox.showinfo(
                "Informasi",
                "Pilih baris item yang ingin dihapus dari keranjang.",
                parent=self,
            )
            return

        index = self.tree_keranjang.index(terpilih[0])
        del self.keranjang_belanja[index]

        self.refresh_tabel_keranjang()

    def kosongkan_keranjang(self):
        self.keranjang_belanja = []
        self.txt_bayar.delete(0, "end")

        self.refresh_tabel_keranjang()

    def refresh_tabel_keranjang(self):
        for row in self.tree_keranjang.get_children():
            self.tree_keranjang.delete(row)

        for item in self.keranjang_belanja:
            subtotal = int(item["harga"]) * int(item["qty"])

            self.tree_keranjang.insert(
                "",
                "end",
                values=(
                    item["nama"],
                    format_rupiah(item["harga"]),
                    item["qty"],
                    format_rupiah(subtotal),
                ),
            )

        total = hitung_total(self.keranjang_belanja)

        self.lbl_total.configure(
            text=f"Total Belanja: {format_rupiah(total)}"
        )

    def proses_transaksi_bayar(self):
        if not self.keranjang_belanja:
            messagebox.showwarning(
                "Peringatan",
                "Keranjang masih kosong!",
                parent=self,
            )
            return

        uang_bayar = bersihkan_angka(self.txt_bayar.get())

        if not uang_bayar:
            messagebox.showwarning(
                "Peringatan",
                "Masukkan nominal uang pembayaran!",
                parent=self,
            )
            self.txt_bayar.focus()
            return

        try:
            hasil = proses_pembayaran(
                self.keranjang_belanja,
                int(uang_bayar),
                self.username_aktif,
            )

            # Simpan file nota TXT
            file_nota = simpan_nota(
                hasil,
                self.keranjang_belanja,
            )

            teks_nota = buat_teks_nota(
                hasil,
                self.keranjang_belanja,
            )

            # Coba cetak ke printer thermal USB
            try:
                cetak_nota(teks_nota)
                status_cetak = (
                    "\nNota berhasil dicetak ke printer thermal."
                )

            except Exception:
                status_cetak = (
                    f"\nNota disimpan ke file: {file_nota.name}"
                    "\n(Printer thermal USB tidak terdeteksi)"
                )

            messagebox.showinfo(
                "Transaksi Berhasil",
                f"No. Nota : {hasil['id_nota']}\n"
                f"Total    : {format_rupiah(hasil['total'])}\n"
                f"Bayar    : {format_rupiah(hasil['bayar'])}\n"
                f"Kembali  : {format_rupiah(hasil['kembali'])}"
                f"{status_cetak}",
                parent=self,
            )

            self.kosongkan_keranjang()
            self.muat_ulang_data()

        except ValueError as err:
            messagebox.showerror(
                "Gagal Memproses",
                str(err),
                parent=self,
            )

        except Exception as err:
            messagebox.showerror(
                "Kesalahan Sistem",
                str(err),
                parent=self,
            )

    # ============================================================
    # TAB 2: KELOLA PRODUK (KHUSUS ADMIN)
    # ============================================================

    def bangun_tab_produk(self):
        frame_form = ctk.CTkFrame(self.tab_produk)
        frame_form.pack(
            fill="x",
            padx=10,
            pady=(5, 10),
        )

        ctk.CTkLabel(
            frame_form,
            text="Nama Menu:",
        ).pack(
            side="left",
            padx=(10, 5),
            pady=10,
        )

        self.txt_nama_produk = ctk.CTkEntry(
            frame_form,
            width=220,
        )
        self.txt_nama_produk.pack(
            side="left",
            padx=5,
            pady=10,
        )

        ctk.CTkLabel(
            frame_form,
            text="Harga:",
        ).pack(
            side="left",
            padx=(10, 5),
            pady=10,
        )

        self.txt_harga_produk = ctk.CTkEntry(
            frame_form,
            width=110,
        )
        self.txt_harga_produk.pack(
            side="left",
            padx=5,
            pady=10,
        )

        ctk.CTkLabel(
            frame_form,
            text="Stok:",
        ).pack(
            side="left",
            padx=(10, 5),
            pady=10,
        )

        self.txt_stok_produk = ctk.CTkEntry(
            frame_form,
            width=80,
        )
        self.txt_stok_produk.pack(
            side="left",
            padx=5,
            pady=10,
        )

        ctk.CTkButton(
            frame_form,
            text="Simpan / Update",
            command=self.aksi_simpan_produk,
        ).pack(
            side="left",
            padx=10,
            pady=10,
        )

        ctk.CTkButton(
            frame_form,
            text="Hapus Terpilih",
            fg_color="#C62828",
            hover_color="#B71C1C",
            width=110,
            command=self.aksi_hapus_produk,
        ).pack(
            side="left",
            padx=(0, 10),
            pady=10,
        )

        # Tabel produk
        frame_tabel = ctk.CTkFrame(self.tab_produk)
        frame_tabel.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5,
        )

        kolom = ("id", "nama", "harga", "stok")

        self.tree_produk = ttk.Treeview(
            frame_tabel,
            columns=kolom,
            show="headings",
            height=14,
        )

        self.tree_produk.heading("id", text="ID")
        self.tree_produk.heading("nama", text="Nama Menu")
        self.tree_produk.heading("harga", text="Harga")
        self.tree_produk.heading("stok", text="Stok")

        self.tree_produk.column(
            "id",
            width=60,
            anchor="center",
        )
        self.tree_produk.column("nama", width=380)
        self.tree_produk.column(
            "harga",
            width=180,
            anchor="e",
        )
        self.tree_produk.column(
            "stok",
            width=120,
            anchor="center",
        )

        self.tree_produk.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0),
            pady=10,
        )

        self.tree_produk.bind(
            "<ButtonRelease-1>",
            self.pilih_baris_produk,
        )

        scrollbar = ttk.Scrollbar(
            frame_tabel,
            orient="vertical",
            command=self.tree_produk.yview,
        )
        self.tree_produk.configure(
            yscrollcommand=scrollbar.set
        )
        scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 10),
            pady=10,
        )

    def pilih_baris_produk(self, event):
        terpilih = self.tree_produk.selection()

        if not terpilih:
            return

        values = self.tree_produk.item(
            terpilih[0],
            "values",
        )

        self.txt_nama_produk.delete(0, "end")
        self.txt_nama_produk.insert(0, values[1])

        self.txt_harga_produk.delete(0, "end")
        self.txt_harga_produk.insert(
            0,
            bersihkan_angka(values[2]),
        )

        self.txt_stok_produk.delete(0, "end")
        self.txt_stok_produk.insert(0, values[3])

    def aksi_simpan_produk(self):
        nama = self.txt_nama_produk.get().strip()
        harga = bersihkan_angka(self.txt_harga_produk.get())
        stok = bersihkan_angka(self.txt_stok_produk.get())

        try:
            simpan_produk(nama, harga, stok)

            messagebox.showinfo(
                "Berhasil",
                f"Data menu '{nama}' berhasil disimpan.",
                parent=self,
            )

            self.txt_nama_produk.delete(0, "end")
            self.txt_harga_produk.delete(0, "end")
            self.txt_stok_produk.delete(0, "end")

            self.muat_ulang_data()

        except ValueError as err:
            messagebox.showwarning(
                "Validasi Gagal",
                str(err),
                parent=self,
            )

    def aksi_hapus_produk(self):
        terpilih = self.tree_produk.selection()

        if not terpilih:
            messagebox.showinfo(
                "Informasi",
                "Pilih baris menu yang ingin dihapus.",
                parent=self,
            )
            return

        values = self.tree_produk.item(
            terpilih[0],
            "values",
        )

        id_produk = values[0]
        nama_produk = values[1]

        if messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Yakin ingin menghapus menu '{nama_produk}'?",
            parent=self,
        ):
            hapus_produk(id_produk)
            self.muat_ulang_data()

    # ============================================================
    # TAB 3: LAPORAN KEUANGAN (KHUSUS ADMIN)
    # ============================================================

    def bangun_tab_laporan(self):
        container = ctk.CTkFrame(self.tab_laporan)
        container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )

        ctk.CTkLabel(
            container,
            text="Ringkasan Penjualan & Laporan Keuangan",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(25, 20))

        self.lbl_jumlah_transaksi = ctk.CTkLabel(
            container,
            text="Total Transaksi (Nota): 0",
            font=ctk.CTkFont(size=15),
        )
        self.lbl_jumlah_transaksi.pack(pady=8)

        self.lbl_total_pendapatan = ctk.CTkLabel(
            container,
            text="Total Pendapatan: Rp 0",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2E7D32",
        )
        self.lbl_total_pendapatan.pack(pady=8)

        ctk.CTkButton(
            container,
            text="Ekspor Laporan ke Excel (.xlsx)",
            width=240,
            height=40,
            command=self.aksi_ekspor_excel,
        ).pack(pady=25)

    def aksi_ekspor_excel(self):
        nama_default = (
            f"Laporan_Keuangan_"
            f"{datetime.now().strftime('%Y%m%d')}.xlsx"
        )

        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Simpan Laporan Keuangan",
            initialfile=nama_default,
            defaultextension=".xlsx",
            filetypes=[
                ("Excel Workbook", "*.xlsx"),
            ],
        )

        if not file_path:
            return

        try:
            hasil = export_laporan_excel(file_path)

            messagebox.showinfo(
                "Ekspor Berhasil",
                f"Laporan berhasil disimpan "
                f"({hasil['jumlah_data']} baris data):\n"
                f"{hasil['file_path']}",
                parent=self,
            )

        except ValueError as err:
            messagebox.showwarning(
                "Tidak Ada Data",
                str(err),
                parent=self,
            )

        except Exception as err:
            messagebox.showerror(
                "Gagal Ekspor",
                str(err),
                parent=self,
            )

    # ============================================================
    # SINKRONISASI DATA DATABASE KE UI
    # ============================================================

    def muat_ulang_data(self):
        # Perbarui ComboBox menu di tab transaksi
        produk_tersedia = get_produk_tersedia()

        self.produk_map = {}
        daftar_pilihan = []

        for produk in produk_tersedia:
            label = (
                f"{produk['nama_barang']} - "
                f"{format_rupiah(produk['harga'])} "
                f"(Stok: {produk['stok']})"
            )

            self.produk_map[label] = produk
            daftar_pilihan.append(label)

        self.cmb_produk.configure(
            values=daftar_pilihan
        )

        if daftar_pilihan:
            self.cmb_produk.set(daftar_pilihan[0])
        else:
            self.cmb_produk.set("Belum ada menu tersedia")

        # Perbarui tabel dan ringkasan khusus Admin
        if self.role_aktif == "Admin":
            for row in self.tree_produk.get_children():
                self.tree_produk.delete(row)

            for produk in get_all_produk():
                self.tree_produk.insert(
                    "",
                    "end",
                    values=(
                        produk["id"],
                        produk["nama_barang"],
                        format_rupiah(produk["harga"]),
                        produk["stok"],
                    ),
                )

            jumlah = get_jumlah_transaksi()
            total_rp = get_total_pendapatan()

            self.lbl_jumlah_transaksi.configure(
                text=f"Total Transaksi (Nota): {jumlah}"
            )

            self.lbl_total_pendapatan.configure(
                text=f"Total Pendapatan: {format_rupiah(total_rp)}"
            )
