
import os
import unicodedata


# ============================================================
# PERINTAH ESC/POS
# ============================================================

ESC = b"\x1b"
GS = b"\x1d"

INIT = ESC + b"@"

ALIGN_LEFT = ESC + b"a\x00"
ALIGN_CENTER = ESC + b"a\x01"
ALIGN_RIGHT = ESC + b"a\x02"

BOLD_ON = ESC + b"E\x01"
BOLD_OFF = ESC + b"E\x00"

CUT_PAPER = GS + b"V\x00"


# ============================================================
# KONVERSI TEKS KE BYTE PRINTER
# ============================================================

def konversi_teks(teks):

    # Mengubah karakter khusus menjadi bentuk sederhana
    teks = unicodedata.normalize(
        "NFKD",
        str(teks)
    )

    teks = teks.encode(
        "ascii",
        errors="replace"
    ).decode("ascii")

    return teks.encode("cp437", errors="replace")


# ============================================================
# MEMBUAT DATA CETAK
# ============================================================

def buat_data_cetak(teks):

    data = bytearray()

    data.extend(INIT)
    data.extend(ALIGN_CENTER)

    data.extend(
        BOLD_ON
    )

    data.extend(
        konversi_teks(teks)
    )

    data.extend(
        BOLD_OFF
    )

    data.extend(
        b"\n\n"
    )

    data.extend(
        CUT_PAPER
    )

    return bytes(data)


# ============================================================
# MENGIRIM DATA KE PRINTER LINUX
# ============================================================

def cetak_ke_printer(data, device_path="/dev/usb/lp0"):

    if not isinstance(data, bytes):
        raise TypeError(
            "Data printer harus berupa bytes."
        )

    if not os.path.exists(device_path):
        raise FileNotFoundError(
            f"Perangkat printer tidak ditemukan: {device_path}"
        )

    fd = None

    try:

        fd = os.open(
            device_path,
            os.O_WRONLY
        )

        with os.fdopen(fd, "wb") as printer:

            fd = None

            printer.write(data)
            printer.flush()

        return True

    except OSError as error:

        raise RuntimeError(
            f"Gagal mencetak nota: {error}"
        ) from error

    finally:

        if fd is not None:
            os.close(fd)


# ============================================================
# FUNGSI CETAK NOTA
# ============================================================

def cetak_nota(teks, device_path="/dev/usb/lp0"):

    data = buat_data_cetak(teks)

    return cetak_ke_printer(
        data,
        device_path
    )
