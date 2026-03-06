import os
import json
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONF_DIR = os.path.join(BASE_DIR, "config")
RUTA = os.path.join(CONF_DIR, "config.json")

def ensure_file():
    if not os.path.exists(CONF_DIR):
        logger.warning('No existe carpeta de configuración!')
        logger.debug('Intentando crear carpeta de configuración...')
        try:
            os.makedirs(CONF_DIR)
            logger.info(f'Carpeta de configuración creada: {CONF_DIR}')
        except Exception as e:
            logger.error(f'No se pudo crear la carpeta de configuración: {e}')
            return

    if not os.path.exists(RUTA):
        logger.warning('No existe archivo de configuración!')
        data = {'tema': "dark"}
        logger.debug('Intentando crear archivo config.json...')
        try:
            with open(RUTA, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info('Archivo creado con configuración por defecto')
        except Exception as e:
            logger.error(f'NO SE PUDO CREAR ARCHIVO DE CONFIGURACIÓN: {e}')

def guardar(tipo):
    ensure_file()
    try:
        with open(RUTA, "w", encoding='utf-8') as f:
            json.dump({"tema": tipo}, f, ensure_ascii=False, indent=2)
            logger.info(f'Configuración de tema guardada: {tipo}')
    except Exception as e:
        logger.error(f'ERROR AL GUARDAR CONFIGURACIÓN: {e}')

def cargar():
    ensure_file()
    try:
        with open(RUTA, "r", encoding='utf-8') as f:
            logger.debug('Cargando tema...')
            data = json.load(f)
            logger.info(f'Tema {data.get("tema")} cargado correctamente.')
            return data.get("tema")
    except Exception as e:
        logger.error(f'NO SE PUDO CARGAR EL TEMA: {e}')
        return "dark" 
