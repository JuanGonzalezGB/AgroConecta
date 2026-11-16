"""Hash y verificación de contraseñas.

Esquema actual: bcrypt (con sal incluida en el propio hash).
Esquema legado: SHA-256 hexadecimal sin sal (64 caracteres). Se sigue aceptando
solo para poder verificar y *migrar* contraseñas antiguas: cuando un usuario inicia
sesión con un hash legado correcto, quien llama debe guardar el hash nuevo
(ver ``necesita_rehash``).
"""
import base64
import hashlib
import hmac
import re

import bcrypt

_SHA256_HEX = re.compile(r"^[a-fA-F0-9]{64}$")
_BCRYPT_PREFIXES = ("$2a$", "$2b$", "$2y$")
BCRYPT_ROUNDS = 12


def _prehash(contrasena: str) -> bytes:
    """bcrypt solo admite 72 bytes; se pre-hashea para aceptar contraseñas largas."""
    digest = hashlib.sha256(contrasena.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_contrasena(contrasena: str) -> str:
    """Devuelve el hash bcrypt (con sal) de la contraseña."""
    return bcrypt.hashpw(_prehash(contrasena), bcrypt.gensalt(BCRYPT_ROUNDS)).decode("utf-8")


# Nombre histórico, conservado para no romper a los controladores existentes.
encriptar_contrasena = hash_contrasena


def es_hash_legado(hash_guardado: str) -> bool:
    """True si el hash guardado es un SHA-256 hexadecimal sin sal."""
    return bool(hash_guardado) and bool(_SHA256_HEX.fullmatch(hash_guardado))


def es_hash_bcrypt(hash_guardado: str) -> bool:
    return bool(hash_guardado) and hash_guardado.startswith(_BCRYPT_PREFIXES)


def verificar_contrasena(contrasena: str, hash_guardado: str) -> bool:
    """Verifica la contraseña contra un hash bcrypt o un hash SHA-256 legado."""
    if not contrasena or not hash_guardado:
        return False
    if es_hash_bcrypt(hash_guardado):
        try:
            return bcrypt.checkpw(_prehash(contrasena), hash_guardado.encode("utf-8"))
        except ValueError:
            return False
    if es_hash_legado(hash_guardado):
        candidato = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()
        return hmac.compare_digest(candidato.lower(), hash_guardado.lower())
    return False


def necesita_rehash(hash_guardado: str) -> bool:
    """True si el hash guardado no es bcrypt y debe regenerarse tras un login correcto."""
    return not es_hash_bcrypt(hash_guardado)
