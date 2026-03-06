import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

CARPETA = os.path.join(os.path.dirname(__file__), "..", "facturas")

def asegurarCarpeta():    
    if not os.path.exists(CARPETA):
        logger.warning('no existe carpeta facturas!')
        logger.debug('intentando crear carpeta facturas...')
        try:
            os.makedirs(CARPETA, exist_ok=True)
            logger.info('carpeta facturas creada satisfactoriamente.')
        except Exception as e:
            logger.critical('NO SE PUDO CREAR CARPETA facturas: {e}')
def generarFacturaTxt(comprador, campesino, cultivo, cantidad, total):
    asegurarCarpeta()
    logger.debug('formateando factura...')
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"factura_{comprador['email'].split('@')[0]}_{fecha}.txt"
    ruta_factura = os.path.join(CARPETA, nombre_archivo)    
    with open(ruta_factura, "w", encoding="utf-8") as f:
        f.write("==============================================\n")
        f.write("              FACTURA DE COMPRA              \n")
        f.write("==============================================\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        logger.debug('recopilando información...')
        f.write(f"Comprador: {comprador['nombre']} ({comprador['email']})\n")
        f.write(f"Vendedor: {campesino['nombre']} ({campesino['email']})\n\n")
        f.write("----------------------------------------------\n")
        f.write(f"Producto: {cultivo['nombre'].capitalize()}\n")
        f.write(f"Cantidad comprada: {cantidad}\n")
        f.write(f"Precio unitario: ${cultivo['precio']:,}\n")
        f.write(f"Total a pagar: ${total:,}\n")
        logger.debug('finalizando factura...')
        f.write("----------------------------------------------\n\n")
        f.write("La información de pago será enviada por correo \nelectrónico, al igual que una copia de este \ndocumento.\n\n")
        f.write("¡Gracias por usar AgroConecta! 🌾\n")
    logger.info('factura lista para escritura de archivo txt.')
    return ruta_factura
