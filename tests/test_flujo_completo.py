"""Recorrido de extremo a extremo contra SQLite (sin UI): lo que hace la app de escritorio."""
import pytest

from auth.seguridad import hash_contrasena
from modelo import pedidoModel as pm
from modelo.CRU import (
    asignar_rol_a_usuario, obtenerCampesinosConCultivos, obtenerCultivosUsuario,
)
from modelo.CRUD import buscarUsuario, crearCultivo, crearUsuario, eliminarCultivo
from modelo.pedidos_utils import (
    aceptar_pedido, asignar_delivery, cargar_pedidos, listar_pedidos, marcar_en_camino, marcar_entregado,
    obtener_pedido, registrar_pedido,
)
from modelo.rolesModel import agregar_permiso_a_rol, agregar_rol, aplicar_roles_y_permisos, obtener_rol_por_id
from repositorios import get_cultivo_repo, get_notificacion_repo


def _registrar(tipo, email, nombre, password="Clave123!", **extra):
    ok, msg = crearUsuario(tipo, {"nombre": nombre, "email": email, "password": hash_contrasena(password), **extra})
    assert ok, msg


def test_registro_login_y_duplicado():
    _registrar("Campesino", "c@x.com", "Carlos")
    assert crearUsuario("Campesino", {"nombre": "Otro", "email": "c@x.com", "password": "h"}) == (
        False, "Ya existe un usuario con ese email.")
    assert crearUsuario("Marciano", {"email": "m@x.com"}) == (False, "Tipo de usuario inválido.")
    ok, user = buscarUsuario("c@x.com", "Clave123!")
    assert ok and user["roles"] == ["campesino"]
    assert aplicar_roles_y_permisos(user)["permisos"]
    assert buscarUsuario("c@x.com", "mala")[0] is False


def test_pedido_de_principio_a_fin(admin):
    _registrar("Campesino", "c@x.com", "Carlos")
    _registrar("Restaurante", "r@x.com", "El Surco")
    _registrar("Delivery", "d@x.com", "Diana", tipo_vehiculo="Moto")
    _, campesino = buscarUsuario("c@x.com", "Clave123!")
    _, restaurante = buscarUsuario("r@x.com", "Clave123!")
    _, domi = buscarUsuario("d@x.com", "Clave123!")

    # campesino agrega (y suma) cultivos
    assert crearCultivo(campesino, {"nombre": "tomate", "cantidad": 50, "precio": 2000.0})[0]
    assert crearCultivo(campesino, {"nombre": "tomate", "cantidad": 10, "precio": 2500.0})[0]
    assert crearCultivo(campesino, {"nombre": "papa", "cantidad": 5, "precio": 900.0})[0]
    assert obtenerCultivosUsuario(campesino)[0] == {"nombre": "tomate", "cantidad": 60, "precio": 2500.0}

    # el restaurante ve al campesino con stock y compra
    assert obtenerCampesinosConCultivos()[0]["email"] == "c@x.com"
    tomate = obtenerCultivosUsuario(campesino)[0]
    assert get_cultivo_repo().descontar_stock("c@x.com", "tomate", 20)
    pedido = registrar_pedido(restaurante, campesino, tomate, 20)
    assert pedido["estado"] == "CREADO" and pedido["precio_total"] == 50000.0 and pedido["qr_base64"]
    assert obtenerCultivosUsuario(campesino)[0]["cantidad"] == 40

    # aceptar -> asignar -> en camino -> entregar
    id_ = pedido["id_pedido"]
    aceptar_pedido(id_)
    asignar_delivery(id_, domi)
    marcar_en_camino(id_)
    final = marcar_entregado(id_)

    assert final["estado"] == "ENTREGADO" and final["delivery"] == "Diana"
    assert [e["evento"] for e in obtener_pedido(id_)["historial"]] == [
        "PEDIDO_CREADO", "PEDIDO_ACEPTADO", "DOMICILIARIO_ASIGNADO", "PEDIDO_EN_CAMINO", "PEDIDO_ENTREGADO"]
    assert len(cargar_pedidos()["pedidos"]) == 1
    assert listar_pedidos(delivery_email="d@x.com")[0]["id_pedido"] == id_
    with pytest.raises(pm.EstadoInvalidoError):
        aceptar_pedido(id_)  # ya entregado

    # eliminar cultivo
    assert eliminarCultivo(campesino, "papa")[0]
    assert eliminarCultivo(campesino, "papa")[0] is False


def test_admin_crea_y_edita_rol_con_permisos(admin):
    _registrar("Restaurante", "r@x.com", "El Surco")
    assert agregar_rol({"id": "auditor", "nombre": "Auditor", "vista": "open_generica"})[0]
    assert agregar_permiso_a_rol("auditor", {"id": "ver_auditoria", "nombre": "ver_auditoria"}, "lectura")[0]
    assert asignar_rol_a_usuario("r@x.com", "auditor", user=admin)[0]
    _, user = buscarUsuario("r@x.com", "Clave123!")
    assert "ver_auditoria" in aplicar_roles_y_permisos(user)["permisos"]
    assert obtener_rol_por_id("auditor")["permisos"]["lectura"][0]["id"] == "ver_auditoria"


def test_las_notificaciones_de_compra_quedan_guardadas():
    get_notificacion_repo().guardar({"destinatario": "Carlos", "titulo": "Compra confirmada", "mensaje": "x"})
    assert get_notificacion_repo().listar("Carlos", solo_no_leidas=True)
