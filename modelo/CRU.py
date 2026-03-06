import os
import json
from auth.permisos import require_permission
from conect.mongoConnection import MongoConnection
from diccionarios import LLAVESUSUARIOS, USUARIOS_INICIALES,PERMISOS_CATEGORIAS
import logging

logger = logging.getLogger(__name__)


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "../data")
RUTA_USUARIOS = os.path.join(DATA_DIR, "usuarios.json")
RUTA_CULTIVOS = os.path.join(DATA_DIR, "cultivos.json")  

def asegurarAdminMongo():
    try:
        db = MongoConnection.get_database()
        collection = db["usuarios"]

        # Buscar si ya existe algún admin
        admin_existente = collection.find_one({"roles": "admin"})

        if not admin_existente:
            logger.warning("No existe ADMIN en MongoDB, creando desde USUARIOS_INICIALES...")

            # Tomamos el admin desde tu diccionario original
            admin_default = USUARIOS_INICIALES["admin"][0]

            collection.insert_one(admin_default)

            logger.info("ADMIN creado correctamente en MongoDB")

        else:
            logger.debug("ADMIN ya existe en MongoDB")

    except Exception as e:
        logger.critical("Error asegurando ADMIN en MongoDB")
        logger.exception(e)

"""def asegurarFile():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Carpeta creada: {DATA_DIR}")

    if not os.path.exists(RUTA_USUARIOS):
        logger.warning('No existe usuarios.json, creando con usuario ADMIN por defecto...')
        try:
            with open(RUTA_USUARIOS, 'w', encoding='utf-8') as f:
                json.dump(USUARIOS_INICIALES, f, ensure_ascii=False, indent=2)
            logger.info('usuarios.json creado con éxito en /data con usuario ADMIN')
        except Exception as e:
            logger.critical("NO SE PUDO CREAR usuarios.json")
            logger.exception(e)


    if not os.path.exists(RUTA_CULTIVOS):
        logger.warning('No existe cultivos.json, creando...')
        try:
            with open(RUTA_CULTIVOS, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)  # guardamos dict vacío
            logger.info('cultivos.json creado con éxito en /data')
        except Exception as e:
            logger.critical("NO SE PUDO CREAR cultivos.json")
            logger.exception(e)"""


# ------------------ Funciones de usuarios (sin cambios) ------------------

COLLECTION_USUARIOS = "usuarios"


def cargarUsuarios():
    """
    Carga todos los usuarios desde MongoDB.
    Devuelve un diccionario con llaves según LLAVESUSUARIOS.
    """
    try:
        db = MongoConnection.get_database()
        collection = db[COLLECTION_USUARIOS]

        data = {valor: [] for valor in LLAVESUSUARIOS.values()}

        for doc in collection.find({}):
            tipo = doc.get("tipo")  # asumimos que guardas el tipo de usuario en 'tipo'
            if tipo in data:
                data[tipo].append(doc)
            else:
                # si tipo no existe en LLAVESUSUARIOS, lo ignoramos o podemos ponerlo en "otros"
                logger.warning(f"Tipo de usuario desconocido '{tipo}' para {doc.get('email')}")
                data.setdefault("otros", []).append(doc)

        return data

    except Exception as e:
        logger.critical('NO SE PUDO CARGAR USUARIOS desde MongoDB')
        logger.exception(e)
        return {valor: [] for valor in LLAVESUSUARIOS.values()}


def guardarUsuarios(data):
    """
    Guarda todos los usuarios en MongoDB.
    data debe ser un dict con llaves según LLAVESUSUARIOS.
    Cada documento reemplaza al usuario según su email.
    """
    try:
        db = MongoConnection.get_database()
        collection = db[COLLECTION_USUARIOS]

        for tipo, lista_usuarios in data.items():
            for u in lista_usuarios:
                email = u.get("email")
                if not email:
                    logger.warning(f"Usuario sin email ignorado: {u}")
                    continue
                # aseguramos que el tipo esté presente
                u["tipo"] = tipo
                collection.update_one(
                    {"email": email},
                    {"$set": u},
                    upsert=True
                )

        logger.info("Usuarios guardados correctamente en MongoDB")

    except Exception as e:
        logger.critical('NO SE PUDO GUARDAR USUARIOS en MongoDB')
        logger.exception(e)

def listar_usuarios():
    """
    Devuelve una lista plana de todos los usuarios.
    Cada usuario es un diccionario con al menos 'nombre' y 'email'.
    """
    data = cargarUsuarios()
    usuarios = []
    for lista in data.values():
        usuarios.extend(lista)
    return usuarios

def normalizar_permisos(permisos):
    """
    Convierte cualquier lista de permisos (string o dict) en lista de IDs (strings) sin duplicados.
    """
    result = []
    if isinstance(permisos, dict):
        for lista in permisos.values():
            for p in lista:
                if isinstance(p, dict) and "id" in p:
                    result.append(p["id"])
                elif isinstance(p, str):
                    result.append(p)
    elif isinstance(permisos, list):
        for p in permisos:
            if isinstance(p, dict) and "id" in p:
                result.append(p["id"])
            elif isinstance(p, str):
                result.append(p)
    return list(set(result))  # eliminar duplicados

@require_permission("gestionar_usuarios")
def asignar_rol_a_usuario(email_usuario, nuevo_rol_id, *, user):
    from modelo.rolesModel import cargar_roles
    from conect.mongoConnection import MongoConnection  # tu conexión
    roles_def = cargar_roles()

    ids_validos = [r["id"] for r in roles_def]
    if isinstance(nuevo_rol_id, list):
        if any(r not in ids_validos for r in nuevo_rol_id):
            return False, f"Uno o más roles no existen: {nuevo_rol_id}"
    else:
        if nuevo_rol_id not in ids_validos:
            return False, f"Rol '{nuevo_rol_id}' no existe"

    db = MongoConnection.get_database()
    collection = db["usuarios"]

    usuario_objetivo = collection.find_one({"email": email_usuario})
    if not usuario_objetivo:
        return False, "Usuario no encontrado"

    # 🔹 Actualizar roles
    roles_actuales = set(usuario_objetivo.get("roles", []))
    if isinstance(nuevo_rol_id, list):
        roles_actuales.update(nuevo_rol_id)
    else:
        roles_actuales.add(nuevo_rol_id)

    # 🔹 Calcular permisos finales
    permisos_finales = []
    for rol_id in roles_actuales:
        rol_obj = next((r for r in roles_def if r["id"] == rol_id), None)
        if rol_obj:
            permisos_finales.extend(normalizar_permisos(rol_obj.get("permisos", {})))

    # 🔹 Guardar cambios en Mongo
    collection.update_one(
        {"email": email_usuario},
        {"$set": {
            "roles": list(roles_actuales),
            "permisos": sorted(list(set(permisos_finales)))
        }}
    )

    logger.info(f"{user.get('email')} asignó rol '{nuevo_rol_id}' a '{email_usuario}' correctamente")
    return True, f"Rol '{nuevo_rol_id}' asignado correctamente"

@require_permission("gestionar_usuarios")
def quitar_rol_a_usuario(email_usuario, roles_a_quitar, *, user):
    from modelo.rolesModel import cargar_roles
    data = cargarUsuarios()
    roles_def = cargar_roles()

    # Validar roles a quitar
    ids_validos = [r["id"] for r in roles_def]
    if isinstance(roles_a_quitar, list):
        invalidos = [r for r in roles_a_quitar if r not in ids_validos]
        if invalidos:
            return False, f"Uno o más roles no existen: {invalidos}"
    else:
        if roles_a_quitar not in ids_validos:
            return False, f"Rol '{roles_a_quitar}' no existe"
        roles_a_quitar = [roles_a_quitar]

    usuario_objetivo = None
    tipo_usuario = None
    index_usuario = None

    for tipo, lista in data.items():
        for i, u in enumerate(lista):
            if u.get("email") == email_usuario:
                usuario_objetivo = u
                tipo_usuario = tipo
                index_usuario = i
                break
        if usuario_objetivo:
            break

    if not usuario_objetivo:
        return False, "Usuario no encontrado"

    usuario_objetivo.setdefault("roles", [])

    # Separar roles quitables y prohibidos
    roles_prohibidos = [r for r in roles_a_quitar if r == "admin"]
    roles_a_quitar_reales = [r for r in roles_a_quitar if r != "admin"]

    # Eliminar solo los roles permitidos
    if roles_a_quitar_reales:
        usuario_objetivo["roles"] = [r for r in usuario_objetivo["roles"] if r not in roles_a_quitar_reales]

    # Recalcular permisos
    permisos_finales = []
    for rol_id in usuario_objetivo["roles"]:
        rol_obj = next((r for r in roles_def if r["id"] == rol_id), None)
        if rol_obj:
            permisos_finales.extend(normalizar_permisos(rol_obj.get("permisos", {})))
    usuario_objetivo["permisos"] = sorted(list(set(permisos_finales)))

    # Guardar cambios
    data[tipo_usuario][index_usuario] = usuario_objetivo
    guardarUsuarios(data)

    # Construir mensaje
    msg_quitar = f"Roles eliminados: {roles_a_quitar_reales}" if roles_a_quitar_reales else ""
    msg_admin = "El rol 'admin' no se puede quitar." if roles_prohibidos else ""
    msg = "\n".join(filter(None, [msg_quitar, msg_admin]))

    logger.info(f"{user.get('email')} intentó quitar roles '{roles_a_quitar}' a '{email_usuario}'. Resultado: {msg}")
    return True, msg or "No se eliminaron roles."



def asignar_rol_base_automatico(email_usuario, rol_base):
    """
    Asigna automáticamente un rol al usuario recién creado sin validar permisos.
    """
    usuario_actor = {"email": "DESIGNATOR", "permisos": ["gestionar_usuarios"]}
    return asignar_rol_a_usuario(email_usuario, rol_base, user=usuario_actor)


def obtener_usuario_por_email(email):
    data = cargarUsuarios()
    for lista in data.values():
        for u in lista:
            if u.get("email") == email:
                return u
    return None


# ------------------ Funciones de cultivos ------------------

COLLECTION_CULTIVOS = "cultivos"


def cargarCultivos():
    """Carga todos los cultivos desde MongoDB en formato {email: [cultivos]}"""
    try:
        db = MongoConnection.get_database()
        collection = db[COLLECTION_CULTIVOS]

        cultivos_data = {}
        for doc in collection.find({}):
            email = doc.get("email")
            cultivos = doc.get("cultivos", [])
            if email:
                cultivos_data[email] = cultivos

        return cultivos_data

    except Exception as e:
        logger.critical("NO SE PUDO CARGAR cultivos desde MongoDB")
        logger.exception(e)
        return {}


def guardarCultivos(data):
    """
    Guarda todos los cultivos en MongoDB.
    data debe ser un dict {email: [cultivos]}.
    Reemplaza los cultivos de cada usuario.
    """
    try:
        db = MongoConnection.get_database()
        collection = db[COLLECTION_CULTIVOS]

        for email, cultivos in data.items():
            collection.update_one(
                {"email": email},
                {"$set": {"cultivos": cultivos}},
                upsert=True  # crea el documento si no existe
            )

        logger.info("Cultivos guardados correctamente en MongoDB")

    except Exception as e:
        logger.critical("NO SE PUDO GUARDAR cultivos en MongoDB")
        logger.exception(e)


def obtenerCultivosUsuario(user):
    """Devuelve todos los cultivos de un usuario desde cultivos.json"""
    email = user.get("email")
    if not email:
        logger.error("Usuario sin email recibido en obtenerCultivosUsuario")
        return []

    cultivos_data = cargarCultivos()
    return cultivos_data.get(email, [])





def actualizarStockCampesino(email_campesino, index_cultivo, nueva_cantidad):
    """Actualiza la cantidad de un cultivo de un usuario"""
    cultivos_data = cargarCultivos()
    cultivos_usuario = cultivos_data.get(email_campesino, [])

    if index_cultivo < len(cultivos_usuario):
        cultivos_usuario[index_cultivo]["cantidad"] = nueva_cantidad
        cultivos_data[email_campesino] = cultivos_usuario
        guardarCultivos(cultivos_data)
        logger.info(f"Stock actualizado para {email_campesino} ({nueva_cantidad} unidades)")
        return True
    else:
        logger.error(f"Index de cultivo {index_cultivo} fuera de rango para {email_campesino}")
        return False


def obtenerCampesinosConCultivos():
    """Devuelve lista de campesinos que tengan cultivos con cantidad > 0"""
    cultivos_data = cargarCultivos()
    disponibles = []
    for email, cultivos in cultivos_data.items():
        cultivos_disponibles = [c for c in cultivos if c.get("cantidad", 0) > 0]
        if cultivos_disponibles:
            disponibles.append({
                "email": email,
                "cultivos": cultivos_disponibles
            })
    return disponibles
