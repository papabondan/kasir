
from database.connection import get_connection


# ============================================================
# MENGAMBIL SEMUA PRODUK
# ============================================================

def get_all_produk():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nama_barang, harga, stok
            FROM produk
            ORDER BY nama_barang ASC
        """)

        return [
            dict(row)
            for row in cursor.fetchall()
        ]


# ============================================================
# PRODUK YANG MEMILIKI STOK
# ============================================================

def get_produk_tersedia():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nama_barang, harga, stok
            FROM produk
            WHERE stok > 0
            ORDER BY nama_barang ASC
        """)

        return [
            dict(row)
            for row in cursor.fetchall()
        ]


# ============================================================
# MENCARI PRODUK BERDASARKAN NAMA
# ============================================================

def get_produk_by_nama(nama_barang):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nama_barang, harga, stok
            FROM produk
            WHERE nama_barang = ?
        """, (nama_barang,))

        produk = cursor.fetchone()

        return dict(produk) if produk else None


# ============================================================
# MENYIMPAN PRODUK
# INSERT ATAU UPDATE
# ============================================================

def simpan_produk(nama_barang, harga, stok):

    nama_barang = nama_barang.strip()

    if not nama_barang:
        raise ValueError("Nama produk harus diisi.")

    try:
        harga = int(harga)
        stok = int(stok)

    except (ValueError, TypeError):
        raise ValueError("Harga dan stok harus berupa angka.")

    if harga <= 0:
        raise ValueError("Harga harus lebih dari nol.")

    if stok < 0:
        raise ValueError("Stok tidak boleh negatif.")

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO produk
            (nama_barang, harga, stok)

            VALUES (?, ?, ?)

            ON CONFLICT(nama_barang)
            DO UPDATE SET
                harga = excluded.harga,
                stok = excluded.stok

        """, (nama_barang, harga, stok))

        return True


# ============================================================
# MENGHAPUS PRODUK
# ============================================================

def hapus_produk(id_produk):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM produk
            WHERE id = ?
        """, (id_produk,))

        return cursor.rowcount > 0
