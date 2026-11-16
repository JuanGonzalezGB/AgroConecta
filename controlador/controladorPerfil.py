from modelo.CRU import cargarUsuarios
from servicios import autenticacion
from servicios.errores import ServicioError
import logging

logger = logging.getLogger(__name__)

class ControladorPerfil:
    def __init__(self, user):
        self.user = user
        self.usuarios = cargarUsuarios()
        logger.debug(f"ControladorPerfil inicializado para usuario: {self.user.get('email')}")

    def cambiar_contraseña(self, contraseña_actual, nueva_contrasena):
        email_usuario = self.user.get("email")
        try:
            autenticacion.cambiar_contrasena(email_usuario, contraseña_actual, nueva_contrasena)
        except ServicioError as e:
            logger.warning(f"Cambio de contraseña rechazado para {email_usuario}: {e.mensaje}")
            return False, e.mensaje
        logger.info(f"Contraseña actualizada correctamente para usuario {email_usuario}")
        return True, "Contraseña actualizada correctamente."

    def datos_filtrados_usuario(self):
        return {k: v for k, v in self.user.items() if k not in ("password", "permisos", "cultivos")}

    def refrescar_usuario(self, user_actualizado):
        self.user = user_actualizado
        if "id" in self.user:
            self.usuarios[self.user["id"]] = user_actualizado
