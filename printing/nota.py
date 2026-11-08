
from datetime import datetime

from config import (
    NAMA_USAHA,
    ALAMAT_USAHA,
    FOLDER_NOTA,
    LEBAR_NOTA_THERMAL
)

from utils.formatter import format_rupiah


# ============================================================
# PENGATURAN NOTA
# ============================================================

LEBAR_KARAKTER = 32


def garis(char="-"):
    return char * LEBAR_KARAKTER


def potong_teks(teks, panjang):
    teks = str(teks)

    if len(teks) > panjang:
        return teks[:panjang - 1] + "…"

    return teks


# ============================================================
# MEMBUAT HEADER NOTA
# ============================================================

def buat_header():

    return [
        NAMA_USAHA.center(LEBAR_KARAKTER),
        ALAMAT_USAHA.center(LEBAR_KARAKTER),
        garis("=")
    ]


# ============================================================
# MEMBUAT DETAIL BARANG
# ============================================================

def buat_detail_barang(keranjang):

    hasil = []

    for item in keranjang:

        nama = item.get(
            "nama",
            item.get("nama_barang", "Produk")
        )

        harga = int(item["harga"])
        qty = int(item["qty"])
        subtotal = harga * qty

        hasil.append(
            potong_teks(nama, LEBAR_KARAKTER)
        )

        hasil.append(
            f"{qty} x {format_rupiah(harga)}"
        )

        hasil.append(
            f"  Subtotal: {format_rupiah(subtotal)}"
        )

    return hasil


# ============================================================
# MEMBUAT NOTA LENGKAP
# ============================================================

def buat_teks_nota(data_transaksi, keranjang):

    id_nota = data_transaksi.get(
        "id_nota", "-"
    )

    tanggal = data_transaksi.get(
        "tanggal",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    kasir = data_transaksi.get(
        "kasir", "-"
    )

    total = int(
        data_transaksi.get("total", 0)
    )

    bayar = int(
        data_transaksi.get("bayar", total)
    )

    kembali = int(
        data_transaksi.get(
            "kembali",
            bayar - total
        )
    )

    baris = []

    baris.extend(buat_header())

    baris.extend([
        f"No. Nota : {id_nota}",
        f"Tanggal  : {tanggal}",
        f"Kasir    : {kasir}",
        garis("-")
    ])

    baris.extend(
        buat_detail_barang(keranjang)
    )

    baris.extend([
        garis("="),
        f"TOTAL    : {format_rupiah(total)}",
        f"BAYAR    : {format_rupiah(bayar)}",
        f"KEMBALI  : {format_rupiah(kembali)}",
        garis("="),
        "Terima kasih telah berbelanja!",
        NAMA_USAHA.center(LEBAR_KARAKTER),
        "\n\n\n"
    ])

    return "\n".join(baris)


# ============================================================
# MENYIMPAN NOTA
# ============================================================

def simpan_nota(data_transaksi, keranjang):

    FOLDER_NOTA.mkdir(
        parents=True,
        exist_ok=True
    )

    id_nota = str(
        data_transaksi.get("id_nota", "nota")
    )

    nama_file = (
        "".join(
            c for c in id_nota
            if c.isalnum() or c in "-_"
        ) or "nota"
    )

    file_path = FOLDER_NOTA / f"{nama_file}.txt"

    isi_nota = buat_teks_nota(
        data_transaksi,
        keranjang
    )

    file_path.write_text(
        isi_nota,
        encoding="utf-8"
    )

    return file_path
