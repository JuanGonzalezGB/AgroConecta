import logging
logger = logging.getLogger(__name__)

class ControladorInternas:
    def __init__(self, frame, root, user, estilo, notiVentana, notificationService):
        self.root = root
        self.estilo = estilo
        self.frame = frame
        self.user = user
        self.notiVentana = notiVentana
        self.notificationService= notificationService

    def open_internas(self):
        from vistas.vistasInternas.notificacioncitas import mostrarNotificaciones
        logger.debug('cargando notificaciones...')  
        try:
            mostrarNotificaciones(self,self.root,self.notiVentana,self.notificationService)
        except:
            logger.error("error cargando notificaciones")
