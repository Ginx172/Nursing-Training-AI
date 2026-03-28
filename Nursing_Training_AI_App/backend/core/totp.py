"""
TOTP Two-Factor Authentication module.
Uses pyotp for TOTP generation and verification.
Generates QR codes for authenticator app setup.
"""

import pyotp
import qrcode
import io
import base64
from typing import Optional, Tuple


APP_NAME = "NursingTrainingAI"


def generate_totp_secret() -> str:
    """Genereaza un secret TOTP random (base32)."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, user_email: str) -> str:
    """Genereaza URI-ul otpauth:// pentru authenticator apps."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=user_email, issuer_name=APP_NAME)


def generate_qr_code_base64(uri: str) -> str:
    """Genereaza QR code ca base64 PNG string (pentru afisare in frontend)."""
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def verify_totp_code(secret: str, code: str) -> bool:
    """
    Verifica un cod TOTP.
    Accepta codul curent si cel anterior/urmator (window=1) pentru a acoperi
    diferente mici de ceas intre server si telefonul utilizatorului.
    """
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_backup_codes(count: int = 8) -> list:
    """Genereaza coduri de backup (recovery codes) pentru cazul in care
    utilizatorul pierde accesul la authenticator app."""
    import secrets
    return [secrets.token_hex(4).upper() for _ in range(count)]
