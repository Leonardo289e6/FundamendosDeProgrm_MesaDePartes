"""Seguridad de contraseñas: PBKDF2 con sal aleatoria (la contraseña nunca se guarda)."""
import hashlib
import hmac
import os

from config import settings


def generar_sal():
    """Sal aleatoria de 16 bytes en hexadecimal (32 caracteres)."""
    return os.urandom(16).hex()


def generar_hash(clave, sal):
    """PBKDF2-HMAC-SHA256 en hexadecimal (64 caracteres)."""
    return hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), bytes.fromhex(sal),
                               settings.ITERACIONES_HASH).hex()


def verificar_clave(clave, sal, hash_guardado):
    """Compara en tiempo constante para no filtrar información."""
    return hmac.compare_digest(generar_hash(clave, sal), hash_guardado)
