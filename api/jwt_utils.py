"""Emisión y validación de tokens JWT (HS256)."""
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

logger = logging.getLogger(__name__)

ALGORITMO = "HS256"
MINUTOS_EXPIRACION = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

_secreto = os.getenv("JWT_SECRET")
if not _secreto:
    # Sin secreto configurado se genera uno efímero: los tokens mueren al reiniciar.
    _secreto = secrets.token_urlsafe(48)
    logger.warning("JWT_SECRET no está definido: se usa un secreto temporal (define JWT_SECRET en .env).")


def crear_token(email: str) -> str:
    ahora = datetime.now(timezone.utc)
    claims = {"sub": email, "iat": ahora, "exp": ahora + timedelta(minutes=MINUTOS_EXPIRACION)}
    return jwt.encode(claims, _secreto, algorithm=ALGORITMO)


def leer_token(token: str) -> str:
    """Devuelve el email del token o lanza ``jwt.PyJWTError``."""
    claims = jwt.decode(token, _secreto, algorithms=[ALGORITMO], options={"require": ["exp", "sub"]})
    return claims["sub"]
