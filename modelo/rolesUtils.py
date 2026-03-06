import logging
from modelo.rolesModel import obtener_permisos_desde_ids_roles, obtener_rol_por_id

logger = logging.getLogger(__name__)

# ----- Obtiene todos los permisos reales de un usuario desde sus roles -----
def _permisos_de_usuario(user):
    permisos = set()
    if not user:
        return permisos

    roles_ids = user.get("roles", [])
    for rid in roles_ids:
        rol = obtener_rol_por_id(rid)
        if rol:
            permisos_rol = rol.get("permisos", {})
            if isinstance(permisos_rol, dict):
                for lista_perms in permisos_rol.values():
                    for p in lista_perms:
                        if isinstance(p, dict) and "id" in p:
                            permisos.add(p["id"])
                        elif isinstance(p, str):
                            permisos.add(p)
            elif isinstance(permisos_rol, list):
                for p in permisos_rol:
                    if isinstance(p, dict) and "id" in p:
                        permisos.add(p["id"])
                    elif isinstance(p, str):
                        permisos.add(p)
    return permisos

def _recalcular_permisos_usuario_obj(usuario):
    """
    Recalcula permisos de un usuario (mutates usuario dict) a partir de su lista usuario['roles'].
    Devuelve la lista resultante.
    """
    if not usuario:
        return []
    roles_ids = usuario.get("roles", []) or []
    permisos = obtener_permisos_desde_ids_roles(roles_ids)
    usuario["permisos"] = permisos
    return permisos

def _recalcular_permisos_usuario(user):
    permisos = set()
    for rid in user.get("roles", []):
        rol = obtener_rol_por_id(rid)
        if rol:
            permisos_rol = rol.get("permisos", {})
            if isinstance(permisos_rol, dict):
                for lista in permisos_rol.values():
                    for p in lista:
                        if isinstance(p, dict) and "id" in p:
                            permisos.add(p["id"])
                        elif isinstance(p, str):
                            permisos.add(p)
            elif isinstance(permisos_rol, list):
                for p in permisos_rol:
                    if isinstance(p, dict) and "id" in p:
                        permisos.add(p["id"])
                    elif isinstance(p, str):
                        permisos.add(p)
    return permisos