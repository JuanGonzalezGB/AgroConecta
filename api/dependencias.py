"""Dependencias de FastAPI: usuario autenticado y permisos dinámicos."""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from api.jwt_utils import leer_token
from repositorios import get_usuario_repo
from servicios.autorizacion import exigir_permiso

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/token")


def usuario_actual(token: str = Depends(oauth2)) -> dict:
    """Carga el usuario desde la base en cada petición: los cambios de rol aplican de inmediato."""
    credenciales_invalidas = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Token inválido o expirado", headers={"WWW-Authenticate": "Bearer"})
    try:
        email = leer_token(token)
    except jwt.PyJWTError:
        raise credenciales_invalidas
    usuario = get_usuario_repo().obtener_por_email(email)
    if usuario is None:
        raise credenciales_invalidas
    return usuario


def requiere_permiso(permiso: str):
    """Fábrica de dependencias: ``Depends(requiere_permiso('gestionar_roles'))``.

    Aplica los mismos permisos dinámicos (y alias) que usa la app de escritorio.
    """
    def dependencia(usuario: dict = Depends(usuario_actual)) -> dict:
        exigir_permiso(usuario, permiso)  # PermisoDenegadoError -> 403 (ver api.main)
        return usuario

    dependencia.__name__ = f"requiere_{permiso}"
    return dependencia
