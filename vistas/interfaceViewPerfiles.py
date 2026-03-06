from abc import ABC
import logging

logger = logging.getLogger(__name__)

class InterfaceViewsPerfiles(ABC):

    def __init__(self, frame, root, user, estilo, notificationService):
 
        self.frame = frame
        self.root = root
        self.user = user
        self.estilo = estilo
        self.notificationService = notificationService


    def openNotificaciones(self):
        from controlador.controladorSubVistas import ControladorSubVistas
        self.controlaSub = ControladorSubVistas(self.frame,self.root,self.user,None,None,None,self.estilo,self.notificationService)
        self.controlaSub.open_ventana_notificaciones_view()
        from controlador.controladorVistas import ControladorVistas
        self.controlaVistas = ControladorVistas(self.frame,self.root,self.user,None,self.estilo,self.notificationService)
        self.controlaVistas.abrir_vista_por_roles()

    def openPerfil(self):
        from controlador.controladorVistas import ControladorVistas
        controlador = ControladorVistas(self.frame, self.root,self.user,None, self.estilo,self.notificationService)
        controlador.openPerfil()

    def cerrarSesion(self):
        
        from controlador.controladorLogin import ControladorLogin
        controlador = ControladorLogin(self.frame, self.root, self.user, self.estilo, self.notificationService)
        controlador.logout()

    def openGanancias(self):
        from controlador.controladorSubVistas import ControladorSubVistas
        self.controlaVistas = ControladorSubVistas(
            self.frame, self.root, self.user, None, None,None,self.estilo, self.notificationService
        )       
        self.controlaVistas.open_ganancias_view()

    def openTemas(self):
        from controlador.controladorVistas import ControladorVistas
        self.controlaVistas = ControladorVistas(
            self.frame, self.root, self.user, None, self.estilo, self.notificationService
        )       
        self.controlaVistas.open_temas()

    def openRegistro(self):
        from controlador.controladorVistas import ControladorVistas
        self.controlaVistas = ControladorVistas(
            self.frame, self.root, self.user, None, self.estilo, self.notificationService
        )       
        self.controlaVistas.open_register()
