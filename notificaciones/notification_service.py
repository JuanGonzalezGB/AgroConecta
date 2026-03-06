import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, repository, sender):
        logger.debug("inicializando NotificationService...")
        self.repository = repository
        self.sender = sender
    def notificar(self, destinatario, titulo, mensaje, mostrar_inmediatamente=True):
        """
        Guarda la notificación y la envía si mostrar_inmediatamente=True
        """
        try:
            data = {
                "destinatario": destinatario,
                "titulo": titulo,
                "mensaje": mensaje,
                "leido": False,
                "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "mostrar_inmediatamente": mostrar_inmediatamente
            }
            self.repository.guardar(data)
            logger.info(f"Notificación guardada para {destinatario}.")

            if mostrar_inmediatamente:
                self.sender.enviar(destinatario, titulo, mensaje)

        except Exception as e:
            logger.error(f"Error al enviar notificación: {e}")

    def obtener_notificaciones(self, destinatario):
        data = self.repository.cargar(destinatario)  # cargar JSON
        return [
            n for n in data
            if n["destinatario"] == destinatario and n["leido"] == False
        ]
    def marcar_como_leidas(self, usuario):
        try:
            self.repository.marcar_como_leidas(usuario)
            logger.info(f"Notificaciones de {usuario} marcadas como leídas.")
        except Exception as e:
            logger.error(f"Error al marcar notificaciones como leídas: {e}")
