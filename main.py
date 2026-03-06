import os
import logging
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from estilo import estiloFactory
from vistas.main_view import MainView  # Debe ser la versión Kivy de MainView
from modelo.CRU import asegurarAdminMongo
import modelo.saveConfig
from notificaciones.iniciar_notis import IniciarNotis

# Crear carpeta de logs si no existe
os.makedirs("logs", exist_ok=True)

# Configuración de logging
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


# Wrapper de MainView como Screen
class MainViewScreen(Screen):
    def __init__(self, estilo, notification_service, **kwargs):
        super().__init__(name="MainView", **kwargs)
        # MainView debe ser la versión Kivy
        self.main_layout = MainView(estilo, notification_service)
        self.add_widget(self.main_layout)


class AgroConectaApp(App):
    def build(self):
        # Cargar estilo
        estilo = estiloFactory.EstiloFactory.definirEstilo(modelo.saveConfig.cargar())
        logger.debug('Cargando sistema de notificaciones...')
        notification_service = IniciarNotis(None, None)

        logger.debug('Cargando MainView...')
        try:
            # Creamos ScreenManager
            sm = ScreenManager()

            # Agregamos MainView como pantalla inicial
            main_screen = MainViewScreen(estilo, notification_service)
            sm.add_widget(main_screen)
            sm.current = "MainView"

            logger.info('MainView cargado correctamente.')

            return sm

        except Exception as e:
            logger.exception(f'ERROR CARGANDO MAINVIEW: {e}')
            return None

    def on_start(self):
        logger.info('Ejecutando AgroConecta...')
        try:
            asegurarAdminMongo()
        except Exception as e:
            logger.critical(f'ERROR AL INICIAR PROGRAMA: {e}')
        finally:
            print('JDB Soft.')


if __name__ == '__main__':
    try:
        AgroConectaApp().run()
    except Exception as e:
        logger.critical(f'ERROR AL CARGAR APP: {e}')