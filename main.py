# main.py
import os
import logging

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from vistas.main_view import MainView
from vistas.selecTema import SelecTema
from estilo.temaActual import TemaActual
from modelo.CRU import asegurarAdminMongo
from notificaciones.iniciar_notis import IniciarNotis
from estilo.baseScreen import BaseScreen  # <- tu BaseScreen con actualizar_fondo

# ---------------- LOGGING ----------------
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%D - %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/app.log", mode="a"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ---------------- SCREENS ----------------

class MainViewScreen(BaseScreen):
    """Pantalla principal que envuelve MainView"""
    NAME = "MainView"

    def __init__(self, notification_service, **kwargs):
        estilo = TemaActual.obtener()
        super().__init__(estilo, name=self.NAME, **kwargs)
        logger.debug("Inicializando MainViewScreen...")

        layout = MainView(estilo, notification_service)
        self.add_widget(layout)


class TemasScreen(BaseScreen):
    """Pantalla de selección de temas"""
    NAME = "Temas"

    def __init__(self, **kwargs):
        estilo = TemaActual.obtener()
        super().__init__(estilo, name=self.NAME, **kwargs)
        logger.debug("Inicializando TemasScreen...")

        layout = SelecTema(self, estilo)
        self.add_widget(layout)

# ---------------- APP ----------------

class AgroConectaApp(App):
    def build(self):
        logger.debug("Cargando tema...")
        TemaActual.cargar()

        logger.debug("Cargando sistema de notificaciones...")
        notification_service = IniciarNotis(None, None)

        logger.debug("Creando ScreenManager...")
        sm = ScreenManager()

        # Instanciar screens
        main_screen = MainViewScreen(notification_service)
        temas_screen = TemasScreen()

        # Agregar screens al manager
        sm.add_widget(main_screen)
        sm.add_widget(temas_screen)

        # Pantalla inicial
        sm.current = MainViewScreen.NAME

        logger.info("MainView cargado correctamente.")
        return sm

    def on_start(self):
        logger.info("Ejecutando AgroConecta...")
        try:
            asegurarAdminMongo()
        except Exception as e:
            logger.critical(f'ERROR AL INICIAR PROGRAMA: {e}')
        finally:
            print('JDB Soft.')

# ---------------- MAIN ----------------

if __name__ == "__main__":
    try:
        AgroConectaApp().run()
    except Exception as e:
        logger.critical(f'ERROR AL CARGAR APP: {e}')