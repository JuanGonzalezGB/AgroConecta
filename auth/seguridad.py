import hashlib

def encriptar_contrasena(contrasena: str) -> str:
    """
    Devuelve el hash SHA-256 de la contraseña.
    """
    return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()
