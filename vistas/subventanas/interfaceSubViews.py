import logging
logger = logging.getLogger(__name__)
from abc import ABC
class InterfaceSubViews(ABC):

    def bloquearRoot(self):   
        self.win.transient(self.root)
        self.win.grab_set()
        self.win.focus_set()
        self.win.wait_window() 
    def botonCerrar(self):
        logger.info('boton cerrar pulsado')
        logger.debug('\tdestruyendo ventana '+self.titulo.lower()+'...')
        self.win.destroy()

        