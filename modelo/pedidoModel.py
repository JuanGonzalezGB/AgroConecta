"""Modelo de pedido y su máquina de estados (lógica pura, sin base de datos ni Tkinter).

Flujo normal:  CREADO -> ACEPTADO -> ASIGNADO -> EN_CAMINO -> ENTREGADO
Salidas:       CREADO -> RECHAZADO | CANCELADO,  ACEPTADO/ASIGNADO -> CANCELADO
Cada cambio queda registrado como evento en el historial del pedido.
"""
import uuid
from datetime import datetime

CREADO = "CREADO"
ACEPTADO = "ACEPTADO"
ASIGNADO = "ASIGNADO"
EN_CAMINO = "EN_CAMINO"
ENTREGADO = "ENTREGADO"
RECHAZADO = "RECHAZADO"
CANCELADO = "CANCELADO"

ESTADOS = (CREADO, ACEPTADO, ASIGNADO, EN_CAMINO, ENTREGADO, RECHAZADO, CANCELADO)

TRANSICIONES = {
    CREADO: {ACEPTADO, RECHAZADO, CANCELADO},
    ACEPTADO: {ASIGNADO, CANCELADO},
    ASIGNADO: {EN_CAMINO, CANCELADO},
    EN_CAMINO: {ENTREGADO},
    ENTREGADO: set(),
    RECHAZADO: set(),
    CANCELADO: set(),
}

# Nombre del evento que se guarda en el historial al entrar a cada estado.
EVENTO_POR_ESTADO = {
    ACEPTADO: "PEDIDO_ACEPTADO",
    ASIGNADO: "DOMICILIARIO_ASIGNADO",
    EN_CAMINO: "PEDIDO_EN_CAMINO",
    ENTREGADO: "PEDIDO_ENTREGADO",
    RECHAZADO: "PEDIDO_RECHAZADO",
    CANCELADO: "PEDIDO_CANCELADO",
}


class EstadoInvalidoError(ValueError):
    """Transición de estado no permitida."""


def _ahora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def nuevo_id_pedido() -> str:
    return f"PED-{uuid.uuid4().hex[:12].upper()}"


def crear_pedido(campesino: dict, restaurante: dict, producto_info: dict,
                 cantidad: int = 0, precio_total: float = 0) -> dict:
    """Crea un pedido (en memoria) con su historial inicial.

    campesino / restaurante: dicts con al menos ``nombre`` y ``email``.
    producto_info: datos del producto (nombre, siembra, cosecha, tipo de cultivo...).
    """
    pedido = {
        "id_pedido": nuevo_id_pedido(),
        "campesino": campesino.get("nombre", ""),
        "campesino_email": campesino.get("email"),
        "restaurante": restaurante.get("nombre", ""),
        "restaurante_email": restaurante.get("email"),
        "delivery": None,
        "delivery_email": None,
        "producto": producto_info.get("nombre", ""),
        "cantidad": cantidad,
        "precio_total": precio_total,
        "estado": CREADO,
        "fecha": _ahora(),
        "info_producto": producto_info,
        "historial": [],
    }
    registrar_evento(pedido, "PEDIDO_CREADO", f"Pedido creado por restaurante {restaurante.get('nombre', '')}")
    return pedido


def registrar_evento(pedido: dict, tipo_evento: str, detalle: str = "") -> None:
    """Agrega un evento al historial del pedido."""
    pedido.setdefault("historial", []).append(
        {"timestamp": _ahora(), "evento": tipo_evento, "detalle": detalle}
    )


def transicion_permitida(estado_actual: str, nuevo_estado: str) -> bool:
    return nuevo_estado in TRANSICIONES.get(estado_actual, set())


def cambiar_estado(pedido: dict, nuevo_estado: str, detalle: str = "") -> dict:
    """Aplica una transición validada y registra el evento. Modifica y devuelve ``pedido``."""
    if nuevo_estado not in ESTADOS:
        raise EstadoInvalidoError(f"Estado desconocido: {nuevo_estado}")
    actual = pedido.get("estado")
    if not transicion_permitida(actual, nuevo_estado):
        raise EstadoInvalidoError(f"No se puede pasar de {actual} a {nuevo_estado}")
    pedido["estado"] = nuevo_estado
    registrar_evento(pedido, EVENTO_POR_ESTADO[nuevo_estado], detalle)
    return pedido


def aceptar(pedido: dict) -> dict:
    return cambiar_estado(pedido, ACEPTADO, f"Pedido aceptado por el campesino {pedido.get('campesino', '')}")


def rechazar(pedido: dict, motivo: str = "") -> dict:
    return cambiar_estado(pedido, RECHAZADO, motivo or "Pedido rechazado por el campesino")


def cancelar(pedido: dict, motivo: str = "") -> dict:
    return cambiar_estado(pedido, CANCELADO, motivo or "Pedido cancelado")


def asignar_delivery(pedido: dict, delivery: dict) -> dict:
    """Asigna un domiciliario (dict con ``nombre`` y ``email``). Requiere estado ACEPTADO."""
    if not transicion_permitida(pedido.get("estado"), ASIGNADO):
        raise EstadoInvalidoError(f"No se puede asignar domiciliario en estado {pedido.get('estado')}")
    pedido["delivery"] = delivery.get("nombre", "")
    pedido["delivery_email"] = delivery.get("email")
    return cambiar_estado(pedido, ASIGNADO, f"Asignado a {delivery.get('nombre', '')}")


def marcar_en_camino(pedido: dict) -> dict:
    return cambiar_estado(pedido, EN_CAMINO, "El domiciliario recogió el pedido")


def marcar_entregado(pedido: dict) -> dict:
    return cambiar_estado(pedido, ENTREGADO, "Pedido entregado al restaurante")
