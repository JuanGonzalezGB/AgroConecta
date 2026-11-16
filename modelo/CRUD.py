from diccionarios import LLAVESUSUARIOS
from auth.seguridad import verificar_contrasena, necesita_rehash, hash_contrasena
from modelo.CRU import cargarCultivos, guardarCultivos
import logging

from modelo.rolesModel import cargar_roles
logger = logging.getLogger(__name__)
from conect.mongoConnection import MongoConnection
from pymongo.errors import DuplicateKeyError
import logging

logger = logging.getLogger(__name__)

def crearUsuario(tipo, userdict):
    try:
        db = MongoConnection.get_database()
        collection = db["usuarios"]

        # 🔹 Traducir usando tu diccionario
        key = LLAVESUSUARIOS.get(tipo)

        if not key:
            logger.error(f"Tipo de usuario inválido: {tipo}")
            return False, "Tipo de usuario inválido."

        # 🔹 Validar email único
        if collection.find_one({"email": userdict.get("email")}):
            logger.warning('Capa 8: email ya registrado')
            return False, 'Ya existe un usuario con ese email.'

        # 🔹 Preparar documento

        rol_base = key[:-1]
        userdict["tipo"] = key   
        userdict["roles"] = [rol_base]
        userdict["permisos"] = []

        collection.insert_one(userdict)

        from modelo.CRU import asignar_rol_base_automatico
        asignar_rol_base_automatico(userdict["email"], rol_base)

        usuario_final = collection.find_one({"email": userdict["email"]})
        permisos_finales = usuario_final.get("permisos", [])

        logger.info(f"Usuario creado con rol '{rol_base}' y permisos {permisos_finales}")

        return True, 'Registro guardado correctamente en MongoDB'

    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        return False, 'Error interno al registrar usuario.'

def readUsuario():
    pass    
def updateUsuario():
    pass
def deleteUsuario():
    pass

def buscarUsuario(email, password):
    """Valida credenciales (password en texto plano). Migra hashes SHA-256 legados a bcrypt."""
    try:
        db = MongoConnection.get_database()
        collection = db["usuarios"]

        usuario = collection.find_one({"email": email})
        if not usuario or not verificar_contrasena(password, usuario.get("password", "")):
            return False, None

        if necesita_rehash(usuario.get("password", "")):
            nuevo_hash = hash_contrasena(password)
            collection.update_one({"email": email}, {"$set": {"password": nuevo_hash}})
            usuario["password"] = nuevo_hash
            logger.info(f"Contraseña de {email} migrada de SHA-256 a bcrypt")

        return True, usuario

    except Exception as e:
        print("Error buscando usuario:", e)
        return False, None


def crearCultivo(user, cultivo):
    """
    Agrega o actualiza un cultivo para un usuario en cultivos.json.
    - Si el cultivo ya existe, suma la cantidad y actualiza el precio.
    - Nunca se elimina aunque la cantidad sea 0.
    """
    email_usuario = user.get("email")
    if not email_usuario:
        logger.error("Usuario sin email recibido en crearCultivo")
        return False, "Error: usuario sin email."

    cultivos_data = cargarCultivos()
    cultivos_usuario = cultivos_data.get(email_usuario, [])

    encontrado = False
    for c in cultivos_usuario:
        if c.get("nombre") == cultivo.get("nombre"):
            encontrado = True
            if cultivo.get("cantidad", 0) < 0:
                logger.warning(f"No se puede asignar cantidad negativa al cultivo '{c['nombre']}' para {email_usuario}.")
            else:
                c["cantidad"] += cultivo.get("cantidad", 0)  # sumamos la cantidad
                c["precio"] = cultivo.get("precio", c["precio"])  # actualizamos el precio
                logger.info(f"Cultivo '{c['nombre']}' actualizado para {email_usuario}: cantidad={c['cantidad']}, precio={c['precio']}")
            break

    if not encontrado:
        # agregamos el cultivo si no existe
        cultivos_usuario.append(cultivo)
        logger.info(f"Nuevo cultivo '{cultivo['nombre']}' agregado para {email_usuario}: cantidad={cultivo['cantidad']}, precio={cultivo['precio']}")

    cultivos_data[email_usuario] = cultivos_usuario
    try:
        guardarCultivos(cultivos_data)
        return True, "Cultivo guardado correctamente."
    except Exception as e:
        logger.error(f"No se pudo guardar cultivos para {email_usuario}: {e}")
        return False, "Error guardando cultivo."
def eliminarCultivo(user, nombre_cultivo):
    """
    Elimina un cultivo del JSON de cultivos para el usuario.
    """
    email_usuario = user.get("email")
    if not email_usuario:
        logger.error("Usuario sin email recibido en eliminarCultivo")
        return False, "Error: usuario sin email."

    cultivos_data = cargarCultivos()
    cultivos_usuario = cultivos_data.get(email_usuario, [])

    # Filtrar cultivos distintos al que se quiere eliminar
    nuevos_cultivos = [c for c in cultivos_usuario if c.get("nombre") != nombre_cultivo]

    if len(nuevos_cultivos) == len(cultivos_usuario):
        logger.warning(f"Cultivo '{nombre_cultivo}' no encontrado para {email_usuario}.")
        return False, f"No se encontró el cultivo '{nombre_cultivo}'."

    cultivos_data[email_usuario] = nuevos_cultivos
    try:
        guardarCultivos(cultivos_data)
        return True, f"Cultivo '{nombre_cultivo}' eliminado correctamente."
    except Exception as e:
        logger.error(f"No se pudo guardar cultivos tras eliminar '{nombre_cultivo}' para {email_usuario}: {e}")
        return False, f"Error al eliminar el cultivo '{nombre_cultivo}'."