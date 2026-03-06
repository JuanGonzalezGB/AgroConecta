import logging
from diccionarios import PERMISOS_CATEGORIAS, ROLES_INICIALES
from conect.mongoConnection import MongoConnection

logger = logging.getLogger(__name__)

def get_roles_collection():
    db = MongoConnection.get_database()
    return db["roles"]

# -------------------- Funciones de roles --------------------

def inicializar_roles():
    """Crea roles iniciales si no existen en MongoDB"""
    col = get_roles_collection()
    for rol in ROLES_INICIALES:
        if not col.find_one({"id": rol["id"]}):
            rol.setdefault("permisos", {cat: [] for cat in PERMISOS_CATEGORIAS})
            rol.setdefault("vista", "")
            col.insert_one(rol)
            logger.info(f"Rol inicial '{rol['id']}' creado en MongoDB")

def cargar_roles():
    """Carga todos los roles desde MongoDB"""
    inicializar_roles()
    return list(get_roles_collection().find({}))

def guardar_roles(data):
    """Guarda todos los roles en MongoDB"""
    col = get_roles_collection()
    for rol in data:
        rol.setdefault("permisos", {cat: [] for cat in PERMISOS_CATEGORIAS})
        rol.setdefault("vista", "")
        col.update_one({"id": rol["id"]}, {"$set": rol}, upsert=True)
    logger.info("Todos los roles guardados/actualizados correctamente en MongoDB")

def agregar_rol(nuevo_rol):
    """Agrega un rol nuevo si no existe (según id)"""
    col = get_roles_collection()
    if col.find_one({"id": nuevo_rol["id"]}):
        return False, f"Ya existe un rol con ID {nuevo_rol['id']}"
    nuevo_rol.setdefault("permisos", {cat: [] for cat in PERMISOS_CATEGORIAS})
    nuevo_rol.setdefault("vista", "")
    col.insert_one(nuevo_rol)
    return True, "Rol agregado correctamente"

def actualizar_rol(id_rol, datos_actualizados):
    """Actualiza un rol existente según su id"""
    col = get_roles_collection()
    result = col.update_one({"id": id_rol}, {"$set": datos_actualizados})
    if result.matched_count == 0:
        logger.warning(f"Rol {id_rol} no encontrado para actualizar.")
        return False
    logger.info(f"Rol {id_rol} actualizado correctamente.")
    return True

def eliminar_rol(rol_id, user):
    """Elimina un rol y actualiza usuarios en MongoDB"""
    from modelo.CRU import cargarUsuarios, guardarUsuarios
    from modelo.rolesUtils import _recalcular_permisos_usuario_obj

    col = get_roles_collection()
    rol = col.find_one({"id": rol_id})
    if not rol:
        return False, "Rol no encontrado"

    permisos_a_eliminar = []
    for cat, permisos in rol.get("permisos", {}).items():
        for p in permisos:
            permisos_a_eliminar.append(p["id"] if isinstance(p, dict) else p)

    # Eliminar rol
    col.delete_one({"id": rol_id})
    logger.info(f"Rol {rol_id} eliminado de MongoDB")

    # Actualizar usuarios
    usuarios_data = cargarUsuarios()
    afectados = 0
    for tipo, lista in usuarios_data.items():
        for i, u in enumerate(lista):
            # Eliminar rol
            if "roles" in u and rol_id in u["roles"]:
                u["roles"] = [r for r in u["roles"] if r != rol_id]
                _recalcular_permisos_usuario_obj(u)
                usuarios_data[tipo][i] = u
                afectados += 1
            # Eliminar permisos asociados
            if "permisos" in u:
                u["permisos"] = [p for p in u["permisos"] if p not in permisos_a_eliminar]
                usuarios_data[tipo][i] = u

    guardarUsuarios(usuarios_data)
    logger.info(f"Usuarios actualizados tras eliminar rol {rol_id}: {afectados}")
    return True, "Rol eliminado, permisos y usuarios actualizados"

# -------------------- Funciones de permisos --------------------

def agregar_permiso_a_rol(rol_id, permiso, categoria="otros"):
    if categoria not in PERMISOS_CATEGORIAS:
        return False, "Categoría inválida"
    col = get_roles_collection()
    rol = col.find_one({"id": rol_id})
    if not rol:
        return False, "Rol no encontrado"
    rol.setdefault("permisos", {cat: [] for cat in PERMISOS_CATEGORIAS})
    if any(p["id"] == permiso["id"] for p in rol["permisos"][categoria]):
        return False, "Permiso ya existe en esta categoría"
    rol["permisos"][categoria].append(permiso)
    col.update_one({"id": rol_id}, {"$set": {"permisos": rol["permisos"]}})
    return True, "Permiso agregado correctamente"

def eliminar_permiso_de_rol(permiso_id):
    from modelo.CRU import cargarUsuarios, guardarUsuarios
    col = get_roles_collection()
    roles = list(col.find({}))
    encontrado = False
    for r in roles:
        for cat in r.get("permisos", {}):
            nueva = []
            for p in r["permisos"][cat]:
                if (isinstance(p, dict) and p.get("id") == permiso_id) or (isinstance(p, str) and p == permiso_id):
                    encontrado = True
                    continue
                nueva.append(p)
            r["permisos"][cat] = nueva
        col.update_one({"id": r["id"]}, {"$set": {"permisos": r["permisos"]}})
    if not encontrado:
        return False, "Permiso no encontrado en roles"

    usuarios_data = cargarUsuarios()
    afectados = 0
    for tipo, lista in usuarios_data.items():
        for i, u in enumerate(lista):
            if "permisos" in u and permiso_id in u["permisos"]:
                u["permisos"] = [p for p in u["permisos"] if p != permiso_id]
                usuarios_data[tipo][i] = u
                afectados += 1
    guardarUsuarios(usuarios_data)
    return True, f"Permiso eliminado correctamente. Usuarios afectados: {afectados}"

def actualizar_permiso(permiso_id, nuevo_nombre):
    col = get_roles_collection()
    roles = list(col.find({}))
    for r in roles:
        for cat in PERMISOS_CATEGORIAS:
            for p in r["permisos"].get(cat, []):
                if isinstance(p, dict) and p.get("id") == permiso_id:
                    p["nombre"] = nuevo_nombre
        col.update_one({"id": r["id"]}, {"$set": {"permisos": r["permisos"]}})
    return True, "Permiso actualizado"

# -------------------- Funciones para aplicar roles y permisos a usuarios --------------------

def aplicar_roles_y_permisos(usuario):
    from modelo.CRU import cargarUsuarios, guardarUsuarios, normalizar_permisos
    col = get_roles_collection()
    roles_def = list(col.find({}))
    permisos_finales = set()
    for rol_def in roles_def:
        if rol_def["id"] in usuario.get("roles", []):
            permisos = rol_def.get("permisos", {})
            if isinstance(permisos, dict):
                for lista_perms in permisos.values():
                    for p in lista_perms:
                        if isinstance(p, dict) and "id" in p:
                            permisos_finales.add(p["id"])
                        elif isinstance(p, str):
                            permisos_finales.add(p)
    usuario["permisos"] = list(permisos_finales)
    return usuario

def obtener_rol_por_id(rol_id):
    col = get_roles_collection()
    return col.find_one({"id": rol_id})

def obtener_permisos_desde_ids_roles(roles_ids):
    from modelo.CRU import normalizar_permisos
    """
    Dado un listado de ids de roles -> devuelve lista de permisos 'planos' (strings) sin duplicados.
    Usa normalizar_permisos() para soportar ambos formatos (dict/list).
    """
    roles = cargar_roles()
    permisos = []
    for rid in roles_ids:
        rol = next((r for r in roles if r.get("id") == rid), None)
        if rol:
            permisos.extend(normalizar_permisos(rol.get("permisos", {})))
    return sorted(list(set(permisos)))