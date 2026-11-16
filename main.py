import os
import tkinter as tk
from modelo.CRU import asegurarAdminMongo
from estilo import estiloFactory
from vistas.main_view import MainView
import modelo.saveConfig
import logging
from notificaciones.iniciar_notis import IniciarNotis

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


def main():   
    estilo = estiloFactory.EstiloFactory.definirEstilo(modelo.saveConfig.cargar())
    logger.debug('cargando root...')
    try:
        root = tk.Tk()    
        root.title("AgroConecta") 
        logger.info('cargado.')
    except Exception:
        logger.exception('ERROR CARGANDO ROOT')
        return
        
    logger.debug('intentando cargar sistema de notificaciones...')
    notification_service=IniciarNotis(root,None)        
    logger.debug('cargando MainView...') 
    try:      
        MainView(root, estilo, notification_service)
        logger.info('MainView cargado.')
    except Exception:
        logger.exception('ERROR CARGANDO MAINVIEW')
        return
    logger.info('Ejecutando AgroConecta...')
    try:
        asegurarAdminMongo()
        root.mainloop()
    except Exception:
        logger.exception('ERROR AL CARGAR PROGRAMA')
        return
    finally:
        print('JDB Soft.')

if __name__ == '__main__':
    main()