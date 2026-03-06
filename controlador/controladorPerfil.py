from modelo.CRU import cargarUsuarios, guardarUsuarios
from auth.validaciones import validar_contrasena
from auth.seguridad import encriptar_contrasena  # <-- nuevo
import logging

logger = logging.getLogger(__name__)

class ControladorPerfil:
    def __init__(self, user):
        self.user = user
        self.usuarios = cargarUsuarios()
        logger.debug(f"ControladorPerfil inicializado para usuario: {self.user.get('email')}")

    def cambiar_contraseña(self, contraseña_actual, nueva_contrasena):
        email_usuario = self.user.get("email")
        logger.debug(f"Iniciando cambio de contraseña para: {email_usuario}")
        encontrado = False

        for categoria, lista_usuarios in self.usuarios.items():
            for u in lista_usuarios:
                if u.get("email") == email_usuario:
                    encontrado = True
                    # Validar contraseña actual encriptada
                    if u.get("password") != encriptar_contrasena(contraseña_actual):
                        logger.warning(f"Contraseña actual incorrecta para usuario {email_usuario}")
                        return False, "La contraseña actual es incorrecta."

                    if not validar_contrasena(nueva_contrasena):
                        logger.warning(f"Nueva contraseña no válida para usuario {email_usuario}")
                        return False, (
                            "La nueva contraseña no cumple los requisitos: "
                            "mínimo 8 caracteres, mayúscula, minúscula, número y carácter especial."
                        )

                    # Guardar contraseña nueva encriptada
                    u["password"] = encriptar_contrasena(nueva_contrasena)
                    guardarUsuarios(self.usuarios)
                    logger.info(f"Contraseña actualizada correctamente para usuario {email_usuario}")
                    return True, "Contraseña actualizada correctamente."

        if not encontrado:
            logger.error(f"Usuario {email_usuario} no encontrado en JSON.")
            return False, "Usuario no encontrado en JSON."

    def datos_filtrados_usuario(self):
        return {k: v for k, v in self.user.items() if k not in ("password", "permisos", "cultivos")}

    def refrescar_usuario(self, user_actualizado):
        self.user = user_actualizado
        if "id" in self.user:
            self.usuarios[self.user["id"]] = user_actualizado
