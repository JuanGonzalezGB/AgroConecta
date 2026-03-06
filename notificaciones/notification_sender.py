import logging
logger = logging.getLogger(__name__)

class NotificationSender:
    def __init__(self, root=None):
        logger.debug("inicializando NotificationSender...")
        self.root = root
    def enviar(self, destinatario, titulo, mensaje, mostrar=True):
        """
        Envía la notificación solo si mostrar=True.
        Para notificaciones diferidas, mostrar=False -> solo se guarda.
        """
        try:
            if mostrar:
                logger.info(f"✅ Notificación para {destinatario}: {titulo} - {mensaje}")
        except Exception as e:
            logger.error(f"Error al enviar la notificación: {e}")
