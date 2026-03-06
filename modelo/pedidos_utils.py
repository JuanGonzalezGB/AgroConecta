import os
import json
import qrcode
from io import BytesIO
import base64
from datetime import datetime
import logging
from conect.mongoConnection import MongoConnection  # <-- tu import correcto

logger = logging.getLogger(__name__)

# Ruta local de respaldo
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RUTA_PEDIDOS = os.path.join(DATA_DIR, "pedidos.json")
QRPEDIDOS_DIR = os.path.join(DATA_DIR, "qr_pedidos")


# -------------------------
# ASEGURAR ARCHIVOS
# -------------------------
def asegurar_archivo_pedidos():
    """Crea pedidos.json si no existe."""
    if not os.path.exists(RUTA_PEDIDOS):
        with open(RUTA_PEDIDOS, "w", encoding="utf-8") as f:
            json.dump({"pedidos": []}, f, indent=4, ensure_ascii=False)


def asegurar_carpeta_qr():
    if not os.path.exists(QRPEDIDOS_DIR):
        logger.warning('No existe carpeta de QR!')
        try:
            os.makedirs(QRPEDIDOS_DIR)
            logger.info(f'Carpeta de QR creada: {QRPEDIDOS_DIR}')
        except Exception as e:
            logger.error(f'No se pudo crear carpeta de QR: {e}')

def cargar_pedidos():
    """
    Devuelve todos los pedidos almacenados en la colección 'pedidos' de MongoDB.
    """
    try:
        mongo = MongoConnection()
        db = mongo.get_database()
        pedidos_col = db["pedidos"]
        pedidos = list(pedidos_col.find({}, {'_id': 0}))  # excluye _id si no lo necesitas
        return {"pedidos": pedidos}
    except Exception as e:
        logger.error(f"No se pudieron cargar los pedidos desde MongoDB: {e}")
        logger.exception(e)
        return {"pedidos": []}
# -------------------------
# CARGAR Y GUARDAR JSON
# -------------------------
"""def cargar_pedidos():
    asegurar_archivo_pedidos()
    with open(RUTA_PEDIDOS, "r", encoding="utf-8") as f:
        return json.load(f)"""


def guardar_pedidos(data):
    with open(RUTA_PEDIDOS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# -------------------------
# GENERAR QR
# -------------------------
def generar_qr_pedido(pedido: dict):
    """
    Genera QR, lo guarda localmente y devuelve base64 para Mongo.
    """
    contenido = json.dumps(pedido, ensure_ascii=False, indent=2)
    asegurar_carpeta_qr()
    #ruta = os.path.join(QRPEDIDOS_DIR, f"pedido_{pedido['id_pedido']}.png")

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(contenido)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    #img.save(ruta)

    # Convertir a base64 para MongoDB
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return qr_b64


# -------------------------
# REGISTRAR PEDIDO
# -------------------------
def registrar_pedido(restaurante: dict, campesino: dict, cultivo: dict, cantidad: int):
    """
    Registra pedido en JSON local y MongoDB, genera historial y QR.
    """
    # Crear ID único
    id_pedido = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Estructura del pedido
    pedido = {
        "id_pedido": id_pedido,
        "restaurante": restaurante.get("nombre"),
        "campesino": campesino.get("nombre"),
        "producto": cultivo.get('nombre'),
        "cantidad": cantidad,
        "precio_total": cantidad * cultivo.get("precio", 0),
        "estado": "Pedido creado",
        "fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "historial": [
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Pedido creado automáticamente."
        ]
    }

    # Generar QR
    qr_b64 = generar_qr_pedido(pedido)
    #pedido["codigo_qr"] = ruta_qr
    pedido["qr_base64"] = qr_b64  # para MongoDB

    # Guardar en JSON local
    """data = cargar_pedidos()
    data["pedidos"].append(pedido)
    guardar_pedidos(data)
"""
    # Guardar en MongoDB
    try:
        mongo = MongoConnection()
        db = mongo.get_database()
        pedidos_col = db["pedidos"]
        pedidos_col.insert_one(pedido)
        logger.info(f"Pedido {id_pedido} guardado en MongoDB")
    except Exception as e:
        logger.error(f"No se pudo guardar pedido en MongoDB: {e}")
        logger.exception(e)

    return pedido