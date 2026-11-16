"""Notificaciones persistidas. El destinatario es el nombre del usuario (como en la app original)."""
from notificaciones.notification_stratgies import (
    NewOrderNotificationStrategy, NotificationStrategy, OrderStatusChangedStrategy,
)
from repositorios import get_notificacion_repo


def notificar(destinatario: str, titulo: str, mensaje: str, mostrar_inmediatamente: bool = False) -> None:
    get_notificacion_repo().guardar({
        "destinatario": destinatario, "titulo": titulo, "mensaje": mensaje,
        "mostrar_inmediatamente": mostrar_inmediatamente,
    })


def notificar_con_estrategia(destinatario: str, titulo: str, estrategia: NotificationStrategy, datos: dict) -> None:
    """Patrón Strategy: la estrategia decide el texto, el servicio solo lo entrega."""
    notificar(destinatario, titulo, estrategia.format_message(datos))


def nuevo_pedido(campesino: str, pedido: dict) -> None:
    notificar_con_estrategia(campesino, "Nuevo pedido", NewOrderNotificationStrategy(),
                             {"order_id": pedido["id_pedido"], "restaurant_name": pedido["restaurante"]})


def cambio_estado(destinatario: str, pedido: dict) -> None:
    notificar_con_estrategia(destinatario, "Actualización de pedido", OrderStatusChangedStrategy(),
                             {"order_id": pedido["id_pedido"], "new_status": pedido["estado"]})


def listar(usuario: dict, solo_no_leidas: bool = False) -> list[dict]:
    return get_notificacion_repo().listar(usuario["nombre"], solo_no_leidas=solo_no_leidas)


def marcar_leidas(usuario: dict) -> int:
    return get_notificacion_repo().marcar_como_leidas(usuario["nombre"])
