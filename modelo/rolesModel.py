"""Roles y permisos dinámicos. Fachada sobre ``repositorios`` (sin acceso directo a la BD)."""
import logging

from diccionarios import PERMISOS_CATEGORIAS, ROLES_INICIALES
from repositorios import get_rol_repo, get_usuario_repo
from repositorios.errores import DuplicadoError, NoEncontradoError

logger = logging.getLogger(__name__)


def _permisos_vacios() -> dict:
    return {cat: [] for cat in PERMISOS_CATEGORIAS}


# -------------------- Funciones de roles --------------------

def inicializar_roles():
    """Crea los roles iniciales que falten."""
    repo = get_rol_repo()
    for rol in ROLES_INICIALES:
        if repo.obtener(rol["id"]) is None:
            nuevo = dict(rol)
            nuevo.setdefault("permisos", _permisos_vacios())
            nuevo.setdefault("vista", "")
            repo.crear(nuevo)
            logger.info(f"Rol inicial '{rol['id']}' creado")


def cargar_roles():
    """Devuelve todos los roles (asegurando antes que existan los iniciales)."""
    inicializar_roles()
    return get_rol_repo().listar()


def guardar_roles(data):
    """Guarda (crea o reemplaza) todos los roles recibidos."""
    repo = get_rol_repo()
    for rol in data:
        rol.setdefault("permisos", _permisos_vacios())
        rol.setdefault("vista", "")
        repo.guardar(rol)
    logger.info("Roles guardados/actualizados correctamente")


def agregar_rol(nuevo_rol):
    """Agrega un rol nuevo si no existe (según id)."""
    nuevo_rol.setdefault("permisos", _permisos_vacios())
    nuevo_rol.setdefault("vista", "")
    try:
        get_rol_repo().crear(nuevo_rol)
    except DuplicadoError:
        return False, f"Ya existe un rol con ID {nuevo_rol['id']}"
    return True, "Rol agregado correctamente"


def actualizar_rol(id_rol, datos_actualizados):
    """Actualiza un rol existente según su id."""
    if not get_rol_repo().actualizar(id_rol, datos_actualizados):
        logger.warning(f"Rol {id_rol} no encontrado para actualizar.")
        return False
    logger.info(f"Rol {id_rol} actualizado correctamente.")
    return True


def eliminar_rol(rol_id, user):
    """Elimina un rol; los usuarios pierden el rol (y los permisos que solo venían de él)."""
    repo = get_rol_repo()
    afectados = len(get_usuario_repo().listar_por_roles([rol_id]))
    if not repo.eliminar(rol_id):
        return False, "Rol no encontrado"
    logger.info(f"Rol {rol_id} eliminado. Usuarios afectados: {afectados}")
    return True, "Rol eliminado, permisos y usuarios actualizados"


# -------------------- Funciones de permisos --------------------

def agregar_permiso_a_rol(rol_id, permiso, categoria="otros"):
    if categoria not in PERMISOS_CATEGORIAS:
        return False, "Categoría inválida"
    try:
        agregado = get_rol_repo().agregar_permiso(rol_id, categoria, permiso)
    except NoEncontradoError:
        return False, "Rol no encontrado"
    if not agregado:
        return False, "Permiso ya existe en esta categoría"
    return True, "Permiso agregado correctamente"


def eliminar_permiso_de_rol(permiso_id):
    """Elimina el permiso de todos los roles. Los permisos de usuario se derivan de los roles."""
    roles_afectados = get_rol_repo().quitar_permiso(permiso_id)
    if not roles_afectados:
        return False, "Permiso no encontrado en roles"
    usuarios = len(get_usuario_repo().listar_por_roles(roles_afectados))
    return True, f"Permiso eliminado correctamente. Usuarios afectados: {usuarios}"


def actualizar_permiso(permiso_id, nuevo_nombre):
    get_rol_repo().renombrar_permiso(permiso_id, nuevo_nombre)
    return True, "Permiso actualizado"


# -------------------- Funciones para aplicar roles y permisos a usuarios --------------------

def aplicar_roles_y_permisos(usuario):
    """Recalcula ``usuario['permisos']`` a partir de sus roles actuales."""
    usuario["permisos"] = get_rol_repo().permisos_de_roles(usuario.get("roles", []))
    return usuario


def obtener_rol_por_id(rol_id):
    return get_rol_repo().obtener(rol_id)


def obtener_permisos_desde_ids_roles(roles_ids):
    """Dado un listado de ids de roles devuelve los ids de permiso (sin duplicados, ordenados)."""
    return get_rol_repo().permisos_de_roles(list(roles_ids))
