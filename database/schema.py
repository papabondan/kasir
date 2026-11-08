from database.connection import get_connection
from services.auth_service import hash_password


def init_db():
  """
    Membuat tabel database jika belum tersedia.
    Tidak menghapus data yang sudah ada.
    """

  with get_connection() as conn:
    cursor = conn.cursor()

    # =========================================
    # TABEL PRODUK
    # =========================================

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS produk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_barang TEXT UNIQUE NOT NULL,
                harga INTEGER NOT NULL,
                stok INTEGER NOT NULL
            )
        """)

    # =========================================
    # TABEL USER
    # =========================================

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL
            )
        """)

    # =========================================
    # TABEL TRANSAKSI
    # =========================================

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

    # =========================================
    # USER DEFAULT
    # =========================================

    cursor.execute("SELECT COUNT(*) FROM user")

    if cursor.fetchone()[0] == 0:

      cursor.executemany(
          """
                INSERT INTO user
                (username, password, email, role)
                VALUES (?, ?, ?, ?)
            """,
          [
              (
                  "owner",
                  hash_password("owner123"),
                  "sdijatim@gmail.com",
                  "Admin",
              ),
              (
                  "kasir1",
                  hash_password("kasir123"),
                  "sdijatim@gmail.com",
                  "Kasir",
              ),
          ],
      )

  print("Database berhasil diperiksa.")


if __name__ == "__main__":
  init_db()
