import logging

from repositorios import get_notificacion_repo

logger = logging.getLogger(__name__)


class NotificationRepository:
    """Adaptador que usa el servicio de notificaciones; delega en ``repositorios``."""

    def __init__(self, repo=None):
        self._repo = repo or get_notificacion_repo()

    def guardar(self, data):
        """Guarda la notificación (fecha_hora y leido los fija el repositorio)."""
        try:
            guardada = self._repo.guardar(data)
            logger.info(f"Notificación guardada: {guardada}")
        except Exception as e:
            logger.error(f"Error guardando notificación: {e}")

    def cargar(self, usuario):
        """Devuelve las notificaciones de un usuario."""
        try:
            return self._repo.listar(usuario)
        except Exception as e:
            logger.error(f"Error cargando notificaciones de {usuario}: {e}")
            return []

    def cargar_todas(self):
        try:
            return self._repo.listar_todas()
        except Exception as e:
            logger.error(f"Error cargando todas las notificaciones: {e}")
            return []

    def marcar_como_leidas(self, usuario):
        try:
            n = self._repo.marcar_como_leidas(usuario)
            logger.info(f"Notificaciones de {usuario} marcadas como leídas ({n} actualizadas)")
        except Exception as e:
            logger.error(f"Error marcando notificaciones como leídas: {e}")
