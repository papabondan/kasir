
import pandas as pd

from database.connection import get_connection


# ============================================================
# MENGAMBIL RIWAYAT TRANSAKSI
# ============================================================

def get_riwayat_transaksi():

    with get_connection() as conn:

        df = pd.read_sql_query("""
            SELECT *
            FROM transaksi
            ORDER BY id DESC
        """, conn)

    return df


# ============================================================
# MENGHITUNG TOTAL PENDAPATAN
# ============================================================

def get_total_pendapatan():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(subtotal), 0)
            FROM transaksi
        """)

        return cursor.fetchone()[0]


# ============================================================
# MENGHITUNG JUMLAH TRANSAKSI
# ============================================================

def get_jumlah_transaksi():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(DISTINCT id_nota)
            FROM transaksi
        """)

        return cursor.fetchone()[0]


# ============================================================
# EKSPOR LAPORAN EXCEL
# ============================================================

def export_laporan_excel(file_path):

    if not file_path:
        raise ValueError("Lokasi penyimpanan belum dipilih.")

    df = get_riwayat_transaksi()

    if df.empty:
        raise ValueError(
            "Belum ada riwayat transaksi keuangan."
        )

    # Nama kolom Excel mengikuti aplikasi lama
    df.columns = [
        "ID",
        "Waktu Transaksi",
        "ID Nota",
        "Nama Menu",
        "Harga Satuan",
        "Jumlah (Qty)",
        "Subtotal Pendapatan",
        "Kasir Operator"
    ]

    df.to_excel(
        file_path,
        index=False
    )

    return {
        "success": True,
        "file_path": file_path,
        "jumlah_data": len(df)
    }
