import pytest

from modelo import pedidoModel as pm


@pytest.fixture
def pedido():
    return pm.crear_pedido(
        {"nombre": "Camp", "email": "c@x.com"}, {"nombre": "Rest", "email": "r@x.com"},
        {"nombre": "tomate", "precio": 10}, cantidad=3, precio_total=30,
    )


def test_pedido_nuevo(pedido):
    assert pedido["estado"] == pm.CREADO
    assert pedido["delivery"] is None
    assert [e["evento"] for e in pedido["historial"]] == ["PEDIDO_CREADO"]
    assert pedido["id_pedido"].startswith("PED-")


def test_flujo_feliz_registra_cada_evento(pedido):
    pm.aceptar(pedido)
    pm.asignar_delivery(pedido, {"nombre": "Dom", "email": "d@x.com"})
    pm.marcar_en_camino(pedido)
    pm.marcar_entregado(pedido)
    assert pedido["estado"] == pm.ENTREGADO
    assert pedido["delivery_email"] == "d@x.com"
    assert [e["evento"] for e in pedido["historial"]] == [
        "PEDIDO_CREADO", "PEDIDO_ACEPTADO", "DOMICILIARIO_ASIGNADO", "PEDIDO_EN_CAMINO", "PEDIDO_ENTREGADO",
    ]


def test_no_se_puede_saltar_estados(pedido):
    with pytest.raises(pm.EstadoInvalidoError):
        pm.marcar_entregado(pedido)
    with pytest.raises(pm.EstadoInvalidoError):
        pm.asignar_delivery(pedido, {"nombre": "Dom", "email": "d@x.com"})  # aún no aceptado
    assert pedido["estado"] == pm.CREADO and pedido["delivery"] is None
    assert len(pedido["historial"]) == 1  # los intentos fallidos no dejan rastro


def test_estados_finales_no_avanzan(pedido):
    pm.rechazar(pedido, "sin stock")
    for accion in (pm.aceptar, pm.marcar_en_camino, pm.cancelar):
        with pytest.raises(pm.EstadoInvalidoError):
            accion(pedido)


def test_cancelar_desde_aceptado_y_estado_desconocido(pedido):
    pm.aceptar(pedido)
    pm.cancelar(pedido, "cliente desistió")
    assert pedido["estado"] == pm.CANCELADO
    with pytest.raises(pm.EstadoInvalidoError):
        pm.cambiar_estado(pedido, "VOLANDO")


def test_matriz_de_transiciones():
    assert pm.transicion_permitida(pm.CREADO, pm.ACEPTADO)
    assert not pm.transicion_permitida(pm.ENTREGADO, pm.CREADO)
    assert all(pm.TRANSICIONES[e] == set() for e in (pm.ENTREGADO, pm.RECHAZADO, pm.CANCELADO))
