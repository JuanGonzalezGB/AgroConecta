# modelo/pedido_model.py
import uuid
from datetime import datetime

def crear_pedido(campesino: dict, restaurante: dict, producto_info: dict) -> dict:
    """
    Crea un pedido con historial inicial.
    campesino: dict con al menos ["nombre"]
    restaurante: dict con al menos ["nombre"]
    producto_info: dict con info del producto (campesino la registró)
    """
    id_pedido = str(uuid.uuid4())

    pedido = {
        "id_pedido": id_pedido,
        "campesino": campesino.get("nombre", ""),
        "restaurante": restaurante.get("nombre", ""),
        "delivery": None,
        "estado": "CREADO",
        "info_producto": producto_info,  # siembra, cosecha, tipo cultivo, etc.
        "historial": [],
        "codigo_qr": f"qrs/{id_pedido}.png"
    }

    registrar_evento(
        pedido,
        "PEDIDO_CREADO",
        f"Pedido creado por restaurante {restaurante.get('nombre', '')}"
    )
    return pedido


def registrar_evento(pedido: dict, tipo_evento: str, detalle: str = "") -> None:
    """
    Agrega un evento al historial del pedido.
    """
    evento = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evento": tipo_evento,
        "detalle": detalle
    }
    pedido.setdefault("historial", [])
    pedido["historial"].append(evento)