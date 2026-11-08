
import re


# ============================================================
# VALIDASI USERNAME
# ============================================================

def validasi_username(username):

    if not username:
        return False

    username = username.strip()

    if len(username) < 3:
        return False

    if len(username) > 30:
        return False

    return bool(
        re.fullmatch(
            r"[a-zA-Z0-9_.-]+",
            username
        )
    )


# ============================================================
# VALIDASI PASSWORD
# ============================================================

def validasi_password(password):

    if not password:
        return False

    return len(password) >= 8


# ============================================================
# VALIDASI EMAIL
# ============================================================

def validasi_email(email):

    if not email:
        return False

    pola = (
        r"^[a-zA-Z0-9._%+-]+"
        r"@[a-zA-Z0-9.-]+"
        r"\.[a-zA-Z]{2,}$"
    )

    return bool(
        re.fullmatch(
            pola,
            email.strip()
        )
    )


# ============================================================
# VALIDASI ANGKA
# ============================================================

def validasi_angka(nilai):

    try:

        int(nilai)
        return True

    except (ValueError, TypeError):
        return False


# ============================================================
# VALIDASI HARGA
# ============================================================

def validasi_harga(harga):

    try:

        harga = int(harga)

        return harga > 0

    except (ValueError, TypeError):
        return False


# ============================================================
# VALIDASI STOK
# ============================================================

def validasi_stok(stok):

    try:

        stok = int(stok)

        return stok >= 0

    except (ValueError, TypeError):
        return False


# ============================================================
# VALIDASI JUMLAH PEMBELIAN
# ============================================================

def validasi_qty(qty):

    try:

        qty = int(qty)

        return qty > 0

    except (ValueError, TypeError):
        return False


# ============================================================
# VALIDASI PEMBAYARAN
# ============================================================

def validasi_pembayaran(total, bayar):

    try:

        total = int(total)
        bayar = int(bayar)

        if total < 0 or bayar < 0:
            return False

        return bayar >= total

    except (ValueError, TypeError):
        return False


# ============================================================
# VALIDASI NAMA PRODUK
# ============================================================

def validasi_nama_produk(nama):

    if not nama:
        return False

    nama = nama.strip()

    return (
        len(nama) >= 2
        and len(nama) <= 100
    )
