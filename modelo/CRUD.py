"""Alta/consulta de usuarios y cultivos de un campesino. Fachada sobre ``repositorios``."""
import logging

from auth.seguridad import hash_contrasena, necesita_rehash, verificar_contrasena
from diccionarios import LLAVESUSUARIOS
from modelo.rolesModel import inicializar_roles
from repositorios import get_cultivo_repo, get_usuario_repo
from repositorios.errores import DuplicadoError

logger = logging.getLogger(__name__)


def crearUsuario(tipo, userdict):
    """Crea un usuario con su rol base. ``userdict['password']`` ya debe venir hasheada."""
    try:
        key = LLAVESUSUARIOS.get(tipo)
        if not key:
            logger.error(f"Tipo de usuario inválido: {tipo}")
            return False, "Tipo de usuario inválido."

        rol_base = key[:-1]  # 'campesinos' -> 'campesino'
        inicializar_roles()
        datos = dict(userdict, tipo=key, roles=[rol_base])
        creado = get_usuario_repo().crear(datos)
        logger.info(f"Usuario creado con rol '{rol_base}' y permisos {creado['permisos']}")
        return True, "Registro guardado correctamente"
    except DuplicadoError:
        logger.warning("Capa 8: email ya registrado")
        return False, "Ya existe un usuario con ese email."
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        return False, "Error interno al registrar usuario."


def buscarUsuario(email, password):
    """Valida credenciales (password en texto plano). Migra hashes SHA-256 legados a bcrypt."""
    try:
        repo = get_usuario_repo()
        usuario = repo.obtener_por_email(email)
        if not usuario or not verificar_contrasena(password, usuario.get("password", "")):
            return False, None

        if necesita_rehash(usuario["password"]):
            nuevo_hash = hash_contrasena(password)
            repo.actualizar_password(email, nuevo_hash)
            usuario["password"] = nuevo_hash
            logger.info(f"Contraseña de {email} migrada de SHA-256 a bcrypt")

        return True, usuario
    except Exception as e:
        logger.error(f"Error buscando usuario: {e}")
        return False, None


def crearCultivo(user, cultivo):
    """Agrega un cultivo al campesino; si ya existe suma la cantidad y actualiza el precio."""
    email_usuario = user.get("email")
    if not email_usuario:
        logger.error("Usuario sin email recibido en crearCultivo")
        return False, "Error: usuario sin email."
    if cultivo.get("cantidad", 0) < 0:
        logger.warning(f"No se puede asignar cantidad negativa al cultivo '{cultivo.get('nombre')}' para {email_usuario}.")
        return False, "La cantidad no puede ser negativa."
    try:
        c = get_cultivo_repo().agregar_o_sumar(
            email_usuario, cultivo["nombre"], cultivo.get("cantidad", 0), cultivo.get("precio", 0)
        )
        logger.info(f"Cultivo '{c['nombre']}' guardado para {email_usuario}: cantidad={c['cantidad']}, precio={c['precio']}")
        return True, "Cultivo guardado correctamente."
    except Exception as e:
        logger.error(f"No se pudo guardar cultivos para {email_usuario}: {e}")
        return False, "Error guardando cultivo."


def eliminarCultivo(user, nombre_cultivo):
    """Elimina un cultivo del campesino."""
    email_usuario = user.get("email")
    if not email_usuario:
        logger.error("Usuario sin email recibido en eliminarCultivo")
        return False, "Error: usuario sin email."
    try:
        if not get_cultivo_repo().eliminar(email_usuario, nombre_cultivo):
            logger.warning(f"Cultivo '{nombre_cultivo}' no encontrado para {email_usuario}.")
            return False, f"No se encontró el cultivo '{nombre_cultivo}'."
        return True, f"Cultivo '{nombre_cultivo}' eliminado correctamente."
    except Exception as e:
        logger.error(f"No se pudo eliminar '{nombre_cultivo}' para {email_usuario}: {e}")
        return False, f"Error al eliminar el cultivo '{nombre_cultivo}'."
