"""Permisos dinámicos (los de los roles en la base). Sin Tkinter ni FastAPI."""
from diccionarios import PERMISOS_ALIAS
from repositorios import get_rol_repo
from servicios.errores import PermisoDenegadoError


def permisos_de(usuario: dict) -> set[str]:
    """Permisos reales según los roles guardados (no se confía en el dict recibido)."""
    return set(get_rol_repo().permisos_de_roles(usuario.get("roles", [])))


def tiene_permiso(usuario: dict, permiso: str) -> bool:
    validos = {permiso, *PERMISOS_ALIAS.get(permiso, [])}
    return bool(validos & permisos_de(usuario))


def exigir_permiso(usuario: dict, permiso: str) -> None:
    if not tiene_permiso(usuario, permiso):
        raise PermisoDenegadoError(f"Permiso requerido: {permiso}")


def es_admin(usuario: dict) -> bool:
    return "admin" in usuario.get("roles", [])
