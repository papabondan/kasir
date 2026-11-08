
import hashlib
import secrets
import hmac

from database.connection import get_connection


# ============================================================
# PASSWORD HASHING
# ============================================================

ITERATIONS = 310000


def hash_password(password):

    salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS
    ).hex()

    return f"pbkdf2_sha256${ITERATIONS}${salt}${hashed}"


def verify_password(password, stored_password):

    if stored_password.startswith("pbkdf2_sha256$"):

        try:
            _, iterations, salt, original_hash = (
                stored_password.split("$")
            )

            hashed = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                int(iterations)
            ).hex()

            return hmac.compare_digest(
                hashed,
                original_hash
            )

        except (ValueError, TypeError):
            return False

    # Kompatibilitas password plaintext database lama
    return hmac.compare_digest(
        password,
        stored_password
    )


# ============================================================
# AUTENTIKASI
# ============================================================

def authenticate_user(username, password):

    username = username.strip()

    if not username or not password:
        return None

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, password, email, role
            FROM user
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

        if not user:
            return None

        if not verify_password(password, user["password"]):
            return None

        # Migrasi otomatis password plaintext lama
        if not user["password"].startswith("pbkdf2_sha256$"):

            password_baru = hash_password(password)

            cursor.execute("""
                UPDATE user
                SET password = ?
                WHERE id = ?
            """, (password_baru, user["id"]))

        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }


# ============================================================
# INFORMASI PENGGUNA
# ============================================================

def get_user_by_username(username):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, email, role
            FROM user
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

        return dict(user) if user else None


def get_email_by_username(username):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT email
            FROM user
            WHERE username = ?
        """, (username,))

        result = cursor.fetchone()

        return result["email"] if result else None


# ============================================================
# GANTI PASSWORD
# ============================================================

def update_password(username, new_password):

    if not new_password or len(new_password) < 8:
        raise ValueError(
            "Password minimal 8 karakter."
        )

    password_hash = hash_password(new_password)

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user
            SET password = ?
            WHERE username = ?
        """, (password_hash, username))

        return cursor.rowcount > 0
