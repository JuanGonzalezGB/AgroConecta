from notificaciones.notification_repository import NotificationRepository
from notificaciones.notification_sender import NotificationSender
from notificaciones.notification_service import NotificationService
import logging
logger = logging.getLogger(__name__)

def IniciarNotis(root,notification_service):
        # 🧩 --- Inicialización del sistema de notificaciones ---    
    try:
        repo_notificaciones = NotificationRepository()
        sender_notificaciones = NotificationSender(root)
        notification_service = NotificationService(repo_notificaciones, sender_notificaciones)
        logger.info("Sistema de notificaciones inicializado correctamente.")
    except Exception as e:
        logger.error(f"Error inicializando notificaciones: {e}")
        notification_service = None  # Evita errores posteriores
    return notification_service

        