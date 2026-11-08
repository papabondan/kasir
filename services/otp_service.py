
import secrets
import smtplib
import hmac

from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import (
    SMTP_SERVER,
    SMTP_PORT,
    EMAIL_PENGIRIM,
    PASSWORD_APLIKASI,
    NAMA_USAHA
)

from services.auth_service import (
    get_email_by_username,
    update_password
)


# ============================================================
# KONFIGURASI OTP
# ============================================================

OTP_EXPIRED_MINUTES = 5
OTP_MAX_ATTEMPTS = 5

# Penyimpanan OTP sementara selama aplikasi berjalan
_otp_sessions = {}


# ============================================================
# GENERATE OTP
# ============================================================

def generate_otp():

    return str(
        secrets.randbelow(900000) + 100000
    )


# ============================================================
# KIRIM EMAIL OTP
# ============================================================

def kirim_email_otp(email_tujuan, username, otp_code):

    if not EMAIL_PENGIRIM or not PASSWORD_APLIKASI:
        return False

    msg = MIMEMultipart()

    msg["From"] = EMAIL_PENGIRIM
    msg["To"] = email_tujuan

    msg["Subject"] = (
        f"Reset Password Akun {username} - {NAMA_USAHA}"
    )

    body = (
        f"Halo {username},\n\n"
        "Berikut kode OTP untuk mereset password Anda:\n\n"
        f"    >> {otp_code} <<\n\n"
        f"Kode berlaku selama {OTP_EXPIRED_MINUTES} menit.\n"
        "Jangan bagikan kode ini kepada siapa pun.\n\n"
        f"Salam,\nSistem Keamanan {NAMA_USAHA}"
    )

    msg.attach(
        MIMEText(body, "plain")
    )

    try:

        with smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT,
            timeout=20
        ) as server:

            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(
                EMAIL_PENGIRIM,
                PASSWORD_APLIKASI
            )

            server.send_message(msg)

        return True

    except Exception as error:

        print(f"Gagal mengirim OTP: {error}")
        return False


# ============================================================
# MEMINTA OTP RESET PASSWORD
# ============================================================

def request_password_reset(username):

    username = username.strip()

    if not username:
        return {
            "success": False,
            "message": "Username harus diisi."
        }

    email = get_email_by_username(username)

    if not email:
        return {
            "success": False,
            "message": "Username tidak ditemukan."
        }

    if not EMAIL_PENGIRIM or not PASSWORD_APLIKASI:
        return {
            "success": False,
            "message": "Konfigurasi email belum tersedia."
        }

    otp = generate_otp()

    berhasil = kirim_email_otp(
        email,
        username,
        otp
    )

    if not berhasil:
        return {
            "success": False,
            "message": "Gagal mengirim email OTP."
        }

    _otp_sessions[username] = {
        "otp": otp,
        "expires": datetime.now() + timedelta(
            minutes=OTP_EXPIRED_MINUTES
        ),
        "attempts": 0,
        "verified": False
    }

    return {
        "success": True,
        "message": f"OTP dikirim ke {email}.",
        "email": email
    }


# ============================================================
# VERIFIKASI OTP
# ============================================================

def verify_otp(username, otp_input):

    session = _otp_sessions.get(username)

    if not session:
        return False

    if datetime.now() > session["expires"]:
        _otp_sessions.pop(username, None)
        return False

    if session["verified"]:
        return True

    if session["attempts"] >= OTP_MAX_ATTEMPTS:
        _otp_sessions.pop(username, None)
        return False

    session["attempts"] += 1

    if not hmac.compare_digest(
        session["otp"],
        str(otp_input).strip()
    ):
        return False

    session["verified"] = True

    return True


# ============================================================
# RESET PASSWORD SETELAH OTP BENAR
# ============================================================

def reset_password(username, new_password):

    session = _otp_sessions.get(username)

    if not session:
        return False

    if datetime.now() > session["expires"]:
        _otp_sessions.pop(username, None)
        return False

    if not session["verified"]:
        return False

    try:

        berhasil = update_password(
            username,
            new_password
        )

        if berhasil:
            _otp_sessions.pop(username, None)

        return berhasil

    except ValueError:
        raise
