import functools
from tkinter import messagebox
from modelo.rolesUtils import _permisos_de_usuario
from modelo.auditoria import log_auditoria
from diccionarios import PERMISOS_ALIAS
import logging

logger = logging.getLogger(__name__)

def require_permission(permiso_requerido):
    """
    Decorador que verifica si el usuario pasado en kwargs['user'] tiene el permiso requerido
    o alguno de sus alias definidos en PERMISOS_ALIAS.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user_actor = kwargs.get("user", None)

            if not isinstance(user_actor, dict):
                raise ValueError(
                    f"La función '{func.__name__}' requiere un parámetro 'user' como diccionario "
                    f"y pasado por keyword argument."
                )

            # Bypass seguro para usuario interno DESIGNATOR
            if user_actor.get("email") == "DESIGNATOR":
                log_auditoria(
                    usuario="DESIGNATOR",
                    accion=func.__name__,
                    recurso=permiso_requerido,
                    resultado="GRANTED",
                    extra="force override"
                )
                return func(*args, **kwargs)

            permisos_actor = _permisos_de_usuario(user_actor)

            # Construir lista de permisos válidos considerando alias
            permisos_validos = [permiso_requerido]
            permisos_validos.extend(PERMISOS_ALIAS.get(permiso_requerido, []))

            # Verificar si el usuario tiene alguno de los permisos válidos
            if not any(p in permisos_actor for p in permisos_validos):
                messagebox.showerror(
                    "Permiso denegado",
                    f"No tienes permiso para realizar esta acción.\nPermiso requerido: {permiso_requerido}"
                )
                logger.warning(
                    f"Usuario {user_actor.get('email')} DENEGADO para '{permiso_requerido}' "
                    f"(permisos disponibles: {permisos_actor})"
                )
                log_auditoria(
                    usuario=user_actor.get("email"),
                    accion=func.__name__,
                    recurso=permiso_requerido,
                    resultado="DENIED"
                )
                # Retornar tupla vacía para que funciones como eliminarCultivo no fallen
                return False, f"Permiso '{permiso_requerido}' denegado"

            # Permiso concedido
            log_auditoria(
                usuario=user_actor.get("email"),
                accion=func.__name__,
                recurso=permiso_requerido,
                resultado="GRANTED"
            )
            logger.info(
                f"Usuario {user_actor.get('email')} GRANTED para '{permiso_requerido}'"
            )

            # Ejecutar la función original
            resultado = func(*args, **kwargs)

            # Asegurarse de que la función devuelva tupla (exito, mensaje) si es None
            if resultado is None:
                return True, "Acción realizada"
            return resultado

        return wrapper
    return decorator
