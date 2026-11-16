"""Administración de roles y permisos dinámicos (solo quien tenga los permisos de gestión)."""
from diccionarios import PERMISOS_CATEGORIAS, ROLES_INICIALES
from repositorios import get_rol_repo, get_usuario_repo
from repositorios.errores import DuplicadoError
from servicios.autorizacion import exigir_permiso
from servicios.errores import ConflictoError, NoEncontradoError, PermisoDenegadoError, ValidacionError

ROLES_PROTEGIDOS = {r["id"] for r in ROLES_INICIALES}
PERMISOS_PROTEGIDOS = {p["id"] for r in ROLES_INICIALES for lista in r["permisos"].values() for p in lista}


def listar_roles(actor: dict) -> list[dict]:
    exigir_permiso(actor, "gestionar_roles")
    return get_rol_repo().listar()


def crear_rol(actor: dict, rol_id: str, nombre: str, vista: str = "open_generica") -> dict:
    exigir_permiso(actor, "gestionar_roles")
    rol_id = (rol_id or "").strip()
    if not rol_id or not (nombre or "").strip():
        raise ValidacionError("El id y el nombre del rol son obligatorios.")
    try:
        return get_rol_repo().crear({"id": rol_id, "nombre": nombre.strip(), "vista": vista,
                                     "permisos": {c: [] for c in PERMISOS_CATEGORIAS}})
    except DuplicadoError as e:
        raise ConflictoError(str(e)) from e


def actualizar_rol(actor: dict, rol_id: str, nombre: str | None = None, vista: str | None = None) -> dict:
    exigir_permiso(actor, "gestionar_roles")
    datos = {k: v for k, v in (("nombre", nombre), ("vista", vista)) if v is not None}
    if not get_rol_repo().actualizar(rol_id, datos):
        raise NoEncontradoError("Rol no encontrado.")
    return get_rol_repo().obtener(rol_id)


def eliminar_rol(actor: dict, rol_id: str) -> None:
    exigir_permiso(actor, "gestionar_roles")
    if rol_id in ROLES_PROTEGIDOS:
        raise PermisoDenegadoError(f"El rol '{rol_id}' es del sistema y no se puede eliminar.")
    if not get_rol_repo().eliminar(rol_id):
        raise NoEncontradoError("Rol no encontrado.")


def agregar_permiso(actor: dict, rol_id: str, categoria: str, permiso_id: str, nombre: str | None = None) -> dict:
    exigir_permiso(actor, "gestionar_permisos")
    if categoria not in PERMISOS_CATEGORIAS:
        raise ValidacionError(f"Categoría inválida. Usa una de: {', '.join(PERMISOS_CATEGORIAS)}")
    if get_rol_repo().obtener(rol_id) is None:
        raise NoEncontradoError("Rol no encontrado.")
    if not get_rol_repo().agregar_permiso(rol_id, categoria, {"id": permiso_id, "nombre": nombre or permiso_id}):
        raise ConflictoError("El permiso ya existe en esa categoría.")
    return get_rol_repo().obtener(rol_id)


def quitar_permiso(actor: dict, permiso_id: str) -> list[str]:
    """Quita el permiso de todos los roles. Devuelve los roles afectados."""
    exigir_permiso(actor, "gestionar_permisos")
    if permiso_id in PERMISOS_PROTEGIDOS:
        raise PermisoDenegadoError(f"El permiso '{permiso_id}' es del sistema y no se puede eliminar.")
    afectados = get_rol_repo().quitar_permiso(permiso_id)
    if not afectados:
        raise NoEncontradoError("Permiso no encontrado en ningún rol.")
    return afectados


def renombrar_permiso(actor: dict, permiso_id: str, nuevo_nombre: str) -> int:
    exigir_permiso(actor, "gestionar_permisos")
    n = get_rol_repo().renombrar_permiso(permiso_id, nuevo_nombre)
    if n == 0:
        raise NoEncontradoError("Permiso no encontrado en ningún rol.")
    return n


def listar_usuarios(actor: dict) -> list[dict]:
    exigir_permiso(actor, "gestionar_usuarios")
    return [{k: v for k, v in u.items() if k != "password"} for u in get_usuario_repo().listar()]


def asignar_rol(actor: dict, email: str, rol_id: str) -> dict:
    exigir_permiso(actor, "gestionar_usuarios")
    if get_rol_repo().obtener(rol_id) is None:
        raise NoEncontradoError(f"Rol '{rol_id}' no existe.")
    usuarios = get_usuario_repo()
    u = usuarios.obtener_por_email(email)
    if u is None:
        raise NoEncontradoError("Usuario no encontrado.")
    if rol_id not in u["roles"]:
        usuarios.establecer_roles(email, [*u["roles"], rol_id])
    return {k: v for k, v in usuarios.obtener_por_email(email).items() if k != "password"}


def quitar_rol(actor: dict, email: str, rol_id: str) -> dict:
    exigir_permiso(actor, "gestionar_usuarios")
    if rol_id == "admin":
        raise PermisoDenegadoError("El rol 'admin' no se puede quitar.")
    usuarios = get_usuario_repo()
    u = usuarios.obtener_por_email(email)
    if u is None:
        raise NoEncontradoError("Usuario no encontrado.")
    usuarios.establecer_roles(email, [r for r in u["roles"] if r != rol_id])
    return {k: v for k, v in usuarios.obtener_por_email(email).items() if k != "password"}
