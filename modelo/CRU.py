"""Usuarios, asignación de roles y cultivos. Fachada sobre ``repositorios``."""
import logging

from auth.permisos import require_permission
from diccionarios import LLAVESUSUARIOS
from repositorios import get_cultivo_repo, get_usuario_repo

logger = logging.getLogger(__name__)


# ------------------ Usuarios ------------------

def cargarUsuarios():
    """Devuelve {tipo: [usuarios]} con llaves según LLAVESUSUARIOS (más 'admin' si existe)."""
    data = {valor: [] for valor in LLAVESUSUARIOS.values()}
    for u in get_usuario_repo().listar():
        data.setdefault(u.get("tipo") or "otros", []).append(u)
    return data


def guardarUsuarios(data):
    """Guarda (upsert por email) todos los usuarios de un dict {tipo: [usuarios]}."""
    repo = get_usuario_repo()
    for tipo, lista_usuarios in data.items():
        for u in lista_usuarios:
            if not u.get("email"):
                logger.warning(f"Usuario sin email ignorado: {u}")
                continue
            u["tipo"] = tipo
            repo.guardar(u)
    logger.info("Usuarios guardados correctamente")


def listar_usuarios():
    """Lista plana de todos los usuarios."""
    return get_usuario_repo().listar()


def normalizar_permisos(permisos):
    """Convierte cualquier lista/dict de permisos (str o dict) en lista de IDs sin duplicados."""
    result = []
    if isinstance(permisos, dict):
        permisos = [p for lista in permisos.values() for p in lista]
    if isinstance(permisos, list):
        for p in permisos:
            if isinstance(p, dict) and "id" in p:
                result.append(p["id"])
            elif isinstance(p, str):
                result.append(p)
    return list(set(result))


@require_permission("gestionar_usuarios")
def asignar_rol_a_usuario(email_usuario, nuevo_rol_id, *, user):
    from modelo.rolesModel import cargar_roles

    ids_validos = [r["id"] for r in cargar_roles()]
    nuevos = nuevo_rol_id if isinstance(nuevo_rol_id, list) else [nuevo_rol_id]
    if isinstance(nuevo_rol_id, list):
        if any(r not in ids_validos for r in nuevos):
            return False, f"Uno o más roles no existen: {nuevo_rol_id}"
    elif nuevo_rol_id not in ids_validos:
        return False, f"Rol '{nuevo_rol_id}' no existe"

    repo = get_usuario_repo()
    objetivo = repo.obtener_por_email(email_usuario)
    if not objetivo:
        return False, "Usuario no encontrado"

    roles = list(objetivo.get("roles", []))
    roles.extend(r for r in nuevos if r not in roles)
    repo.establecer_roles(email_usuario, roles)  # los permisos se derivan de los roles

    logger.info(f"{user.get('email')} asignó rol '{nuevo_rol_id}' a '{email_usuario}' correctamente")
    return True, f"Rol '{nuevo_rol_id}' asignado correctamente"


@require_permission("gestionar_usuarios")
def quitar_rol_a_usuario(email_usuario, roles_a_quitar, *, user):
    from modelo.rolesModel import cargar_roles

    ids_validos = [r["id"] for r in cargar_roles()]
    if isinstance(roles_a_quitar, list):
        invalidos = [r for r in roles_a_quitar if r not in ids_validos]
        if invalidos:
            return False, f"Uno o más roles no existen: {invalidos}"
    else:
        if roles_a_quitar not in ids_validos:
            return False, f"Rol '{roles_a_quitar}' no existe"
        roles_a_quitar = [roles_a_quitar]

    repo = get_usuario_repo()
    objetivo = repo.obtener_por_email(email_usuario)
    if not objetivo:
        return False, "Usuario no encontrado"

    roles_prohibidos = [r for r in roles_a_quitar if r == "admin"]
    roles_a_quitar_reales = [r for r in roles_a_quitar if r != "admin"]

    if roles_a_quitar_reales:
        restantes = [r for r in objetivo.get("roles", []) if r not in roles_a_quitar_reales]
        repo.establecer_roles(email_usuario, restantes)

    msg_quitar = f"Roles eliminados: {roles_a_quitar_reales}" if roles_a_quitar_reales else ""
    msg_admin = "El rol 'admin' no se puede quitar." if roles_prohibidos else ""
    msg = "\n".join(filter(None, [msg_quitar, msg_admin]))

    logger.info(f"{user.get('email')} intentó quitar roles '{roles_a_quitar}' a '{email_usuario}'. Resultado: {msg}")
    return True, msg or "No se eliminaron roles."


def asignar_rol_base_automatico(email_usuario, rol_base):
    """Asigna un rol al usuario recién creado sin validar permisos (actor interno)."""
    usuario_actor = {"email": "DESIGNATOR", "permisos": ["gestionar_usuarios"]}
    return asignar_rol_a_usuario(email_usuario, rol_base, user=usuario_actor)


def obtener_usuario_por_email(email):
    return get_usuario_repo().obtener_por_email(email)


# ------------------ Cultivos ------------------

def cargarCultivos():
    """Devuelve {email_campesino: [cultivos]}."""
    return get_cultivo_repo().listar_todos()


def guardarCultivos(data):
    """Reemplaza los cultivos de cada campesino del dict {email: [cultivos]}."""
    repo = get_cultivo_repo()
    for email, cultivos in data.items():
        repo.reemplazar(email, cultivos)
    logger.info("Cultivos guardados correctamente")


def obtenerCultivosUsuario(user):
    email = user.get("email")
    if not email:
        logger.error("Usuario sin email recibido en obtenerCultivosUsuario")
        return []
    return get_cultivo_repo().listar(email)


def actualizarStockCampesino(email_campesino, index_cultivo, nueva_cantidad):
    """Actualiza la cantidad del cultivo en la posición ``index_cultivo`` del campesino."""
    repo = get_cultivo_repo()
    cultivos = repo.listar(email_campesino)
    if 0 <= index_cultivo < len(cultivos):
        repo.actualizar_cantidad(email_campesino, cultivos[index_cultivo]["nombre"], nueva_cantidad)
        logger.info(f"Stock actualizado para {email_campesino} ({nueva_cantidad} unidades)")
        return True
    logger.error(f"Index de cultivo {index_cultivo} fuera de rango para {email_campesino}")
    return False


def obtenerCampesinosConCultivos():
    """Campesinos con al menos un cultivo con cantidad > 0 (solo esos cultivos)."""
    disponibles = []
    for email, cultivos in get_cultivo_repo().listar_todos().items():
        con_stock = [c for c in cultivos if c.get("cantidad", 0) > 0]
        if con_stock:
            disponibles.append({"email": email, "cultivos": con_stock})
    return disponibles
