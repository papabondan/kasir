
from datetime import datetime

from database.connection import get_connection


# ============================================================
# MENGHITUNG TOTAL BELANJA
# ============================================================

def hitung_total(keranjang):

    return sum(
        int(item["harga"]) * int(item["qty"])
        for item in keranjang
    )


# ============================================================
# MEMERIKSA STOK PRODUK
# ============================================================

def periksa_stok(keranjang):

    with get_connection() as conn:

        cursor = conn.cursor()

        for item in keranjang:

            nama = item["nama"]
            qty = int(item["qty"])

            if qty <= 0:
                return False, f"Jumlah {nama} tidak valid."

            cursor.execute("""
                SELECT stok
                FROM produk
                WHERE nama_barang = ?
            """, (nama,))

            produk = cursor.fetchone()

            if not produk:
                return False, f"Produk {nama} tidak ditemukan."

            if qty > produk["stok"]:
                return False, (
                    f"Stok {nama} tidak mencukupi. "
                    f"Tersedia: {produk['stok']}"
                )

    return True, "Stok tersedia."


# ============================================================
# VALIDASI PEMBAYARAN
# ============================================================

def validasi_pembayaran(keranjang, uang_bayar):

    if not keranjang:
        return False, "Keranjang masih kosong."

    try:
        bayar = int(uang_bayar)

    except (ValueError, TypeError):
        return False, "Nominal pembayaran tidak valid."

    total = hitung_total(keranjang)

    if bayar < total:
        return False, "Uang pembayaran masih kurang."

    return True, "Pembayaran valid."


# ============================================================
# MENYIMPAN TRANSAKSI DAN MENGURANGI STOK
# ============================================================

def simpan_transaksi(keranjang, kasir):

    if not keranjang:
        raise ValueError("Keranjang masih kosong.")

    if not kasir:
        raise ValueError("Nama kasir belum tersedia.")

    waktu_sekarang = datetime.now()

    str_tanggal = waktu_sekarang.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Menambahkan mikrodetik agar ID nota
    # tidak mudah bertabrakan.
    id_nota = waktu_sekarang.strftime(
        "NOTA%Y%m%d%H%M%S%f"
    )

    total = 0

    with get_connection() as conn:

        cursor = conn.cursor()

        for item in keranjang:

            nama = item["nama"]
            harga = int(item["harga"])
            qty = int(item["qty"])

            if harga < 0 or qty <= 0:
                raise ValueError(
                    f"Data transaksi {nama} tidak valid."
                )

            subtotal = harga * qty

            # Kurangi stok hanya jika stok mencukupi
            cursor.execute("""
                UPDATE produk
                SET stok = stok - ?
                WHERE nama_barang = ?
                AND stok >= ?
            """, (qty, nama, qty))

            if cursor.rowcount != 1:
                raise ValueError(
                    f"Stok {nama} tidak mencukupi "
                    "atau produk tidak ditemukan."
                )

            # Simpan riwayat penjualan
            cursor.execute("""
                INSERT INTO transaksi (
                    tanggal,
                    id_nota,
                    nama_barang,
                    harga,
                    qty,
                    subtotal,
                    kasir
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str_tanggal,
                id_nota,
                nama,
                harga,
                qty,
                subtotal,
                kasir
            ))

            total += subtotal

    return {
        "id_nota": id_nota,
        "tanggal": str_tanggal,
        "total": total,
        "kasir": kasir
    }


# ============================================================
# PROSES PEMBAYARAN
# ============================================================

def proses_pembayaran(keranjang, uang_bayar, kasir):

    valid, pesan = validasi_pembayaran(
        keranjang,
        uang_bayar
    )

    if not valid:
        raise ValueError(pesan)

    bayar = int(uang_bayar)
    total = hitung_total(keranjang)

    # Simpan transaksi terlebih dahulu
    data_transaksi = simpan_transaksi(
        keranjang,
        kasir
    )

    return {
        **data_transaksi,
        "bayar": bayar,
        "kembali": bayar - total
    }
