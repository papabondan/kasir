
from datetime import datetime


# ============================================================
# FORMAT RUPIAH
# ============================================================

def format_rupiah(nominal):

    nominal = int(nominal)

    return "Rp {:,}".format(
        nominal
    ).replace(",", ".")


# ============================================================
# FORMAT ANGKA
# ============================================================

def format_angka(nilai):

    return "{:,}".format(
        int(nilai)
    ).replace(",", ".")


# ============================================================
# FORMAT TANGGAL
# ============================================================

def format_tanggal(tanggal):

    if not tanggal:
        return "-"

    try:

        hasil = datetime.strptime(
            str(tanggal),
            "%Y-%m-%d %H:%M:%S"
        )

        return hasil.strftime(
            "%d-%m-%Y %H:%M"
        )

    except (ValueError, TypeError):

        return str(tanggal)


# ============================================================
# FORMAT TANGGAL SAJA
# ============================================================

def format_tanggal_saja(tanggal):

    if not tanggal:
        return "-"

    try:

        hasil = datetime.strptime(
            str(tanggal),
            "%Y-%m-%d"
        )

        return hasil.strftime(
            "%d-%m-%Y"
        )

    except (ValueError, TypeError):

        return str(tanggal)


# ============================================================
# FORMAT WAKTU
# ============================================================

def format_waktu(waktu=None):

    if waktu is None:
        waktu = datetime.now()

    return waktu.strftime(
        "%H:%M:%S"
    )


# ============================================================
# MEMBERSIHKAN INPUT ANGKA
# ============================================================

def bersihkan_angka(nilai):

    return "".join(
        karakter
        for karakter in str(nilai)
        if karakter.isdigit()
    )


# ============================================================
# FORMAT NOMOR NOTA
# ============================================================

def format_nomor_nota(nomor):

    return str(nomor).strip().upper()
