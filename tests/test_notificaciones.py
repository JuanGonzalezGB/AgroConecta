import pytest

from notificaciones.event_triggers import notificar_asignado_delivery, notificar_nuevo_pedido
from notificaciones.notification_repository import NotificationRepository
from notificaciones.notification_sender import NotificationSender
from notificaciones.notification_service import NotificationService
from notificaciones.notification_stratgies import (
    NewOrderNotificationStrategy, NotificationStrategy, OrderStatusChangedStrategy,
)


def test_estrategia_nuevo_pedido():
    msg = NewOrderNotificationStrategy().format_message({"order_id": "PED-1", "restaurant_name": "El Surco"})
    assert msg == "Nuevo pedido #PED-1 recibido de El Surco"


def test_estrategia_cambio_de_estado():
    msg = OrderStatusChangedStrategy().format_message({"order_id": "PED-1", "new_status": "ENTREGADO"})
    assert msg == "El pedido #PED-1 cambió a estado: ENTREGADO"


def test_las_estrategias_son_intercambiables():
    estrategias = [NewOrderNotificationStrategy(), OrderStatusChangedStrategy()]
    assert all(isinstance(e, NotificationStrategy) for e in estrategias)
    datos = {"order_id": "1", "restaurant_name": "R", "new_status": "S"}
    assert len({e.format_message(datos) for e in estrategias}) == 2


def test_estrategia_abstracta_no_se_instancia():
    with pytest.raises(TypeError):
        NotificationStrategy()


@pytest.fixture
def servicio():
    return NotificationService(NotificationRepository(), NotificationSender(None))


def test_servicio_guarda_y_lista_no_leidas(servicio):
    servicio.notificar("Ana", "Hola", "mensaje")
    servicio.notificar("Ana", "Diferida", "otra", mostrar_inmediatamente=False)
    servicio.notificar("Beto", "Otro", "x")
    assert [n["titulo"] for n in servicio.obtener_notificaciones("Ana")] == ["Hola", "Diferida"]


def test_servicio_marca_como_leidas(servicio):
    servicio.notificar("Ana", "Hola", "mensaje")
    servicio.marcar_como_leidas("Ana")
    assert servicio.obtener_notificaciones("Ana") == []


def test_triggers_generan_notificaciones(servicio):
    notificar_nuevo_pedido(servicio, "Carlos", "PED-9", "El Surco")
    notificar_asignado_delivery(servicio, "Diana", "PED-9")
    assert "PED-9" in servicio.obtener_notificaciones("Carlos")[0]["mensaje"]
    assert servicio.obtener_notificaciones("Diana")[0]["titulo"] == "Pedido Asignado"
