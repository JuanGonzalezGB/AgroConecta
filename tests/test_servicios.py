import subprocess
import sys

import pytest

from servicios import autenticacion, cultivos, notificaciones, pedidos, roles
from servicios.errores import (
    ConflictoError, NoAutenticadoError, PermisoDenegadoError, ValidacionError,
)

DATOS = {"nombre": "Carlos Campo", "email": "c@x.com", "password": "Clave123!", "telefono": "3001112233"}


def test_los_servicios_no_importan_tkinter():
    codigo = ("import sys, servicios.autenticacion, servicios.cultivos, servicios.pedidos, "
              "servicios.notificaciones, servicios.roles; assert 'tkinter' not in sys.modules")
    assert subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True).returncode == 0


@pytest.fixture
def escenario(crear_usuario):
    camp = crear_usuario("Campesino", "c@x.com", nombre="Carlos")
    rest = crear_usuario("Restaurante", "r@x.com", nombre="El Surco")
    domi = crear_usuario("Delivery", "d@x.com", nombre="Diana")
    cultivos.agregar_cultivo(camp, "Tomate", 10, 1000.0)
    return camp, rest, domi


def test_registro_valida_y_no_expone_hash():
    u = autenticacion.registrar("campesino", dict(DATOS))
    assert "password" not in u and u["roles"] == ["campesino"]
    with pytest.raises(ConflictoError):
        autenticacion.registrar("campesino", dict(DATOS))
    with pytest.raises(ValidacionError):
        autenticacion.registrar("campesino", dict(DATOS, email="DESIGNATOR", password="debil"))
    with pytest.raises(ValidacionError):
        autenticacion.registrar("restaurante", dict(DATOS, email="r@x.com"))  # falta NIT
    with pytest.raises(ValidacionError):
        autenticacion.registrar("marciano", dict(DATOS))


def test_login_y_cambio_de_contrasena():
    autenticacion.registrar("campesino", dict(DATOS))
    assert autenticacion.login("c@x.com", "Clave123!")["email"] == "c@x.com"
    with pytest.raises(NoAutenticadoError):
        autenticacion.login("c@x.com", "mala")
    autenticacion.cambiar_contrasena("c@x.com", "Clave123!", "Nueva123!")
    autenticacion.login("c@x.com", "Nueva123!")
    with pytest.raises(NoAutenticadoError):
        autenticacion.cambiar_contrasena("c@x.com", "Clave123!", "Otra123!")
    with pytest.raises(ValidacionError):
        autenticacion.cambiar_contrasena("c@x.com", "Nueva123!", "debil")


def test_cultivos_validan_permisos_y_datos(escenario):
    camp, rest, _ = escenario
    with pytest.raises(PermisoDenegadoError):
        cultivos.agregar_cultivo(rest, "papa", 1, 1.0)
    with pytest.raises(ValidacionError):
        cultivos.agregar_cultivo(camp, "papa", 0, 1.0)
    assert cultivos.listar_campesinos(rest)[0]["cultivos"][0]["nombre"] == "tomate"


def test_flujo_de_pedido_con_actores_correctos(escenario):
    camp, rest, domi = escenario
    p = pedidos.crear_pedido(rest, "c@x.com", "tomate", 4)
    id_ = p["id_pedido"]
    assert cultivos.listar_mis_cultivos(camp)[0]["cantidad"] == 6
    # el restaurante no puede aceptar su propio pedido; el domiciliario no puede saltarse pasos
    with pytest.raises(PermisoDenegadoError):
        pedidos.aceptar(rest, id_)
    pedidos.aceptar(camp, id_)
    with pytest.raises(PermisoDenegadoError):
        pedidos.marcar_en_camino(domi, id_)  # aún no es suyo
    pedidos.asignar_delivery(camp, id_, "d@x.com")
    with pytest.raises(PermisoDenegadoError):
        pedidos.marcar_en_camino(camp, id_)
    pedidos.marcar_en_camino(domi, id_)
    assert pedidos.cambiar_estado(domi, id_, "entregado")["estado"] == "ENTREGADO"
    assert len(pedidos.historial(rest, id_)) == 5
    with pytest.raises(ConflictoError):
        pedidos.aceptar(camp, id_)
    # notificaciones generadas para cada parte
    assert any("Nuevo pedido" == n["titulo"] for n in notificaciones.listar(camp))
    assert notificaciones.listar(domi)[0]["titulo"] == "Pedido asignado"
    assert notificaciones.marcar_leidas(camp) > 0 and notificaciones.listar(camp, solo_no_leidas=True) == []


def test_stock_insuficiente_y_devolucion_al_rechazar(escenario):
    camp, rest, _ = escenario
    with pytest.raises(ConflictoError):
        pedidos.crear_pedido(rest, "c@x.com", "tomate", 11)
    p = pedidos.crear_pedido(rest, "c@x.com", "tomate", 10)
    assert cultivos.listar_mis_cultivos(camp)[0]["cantidad"] == 0
    pedidos.rechazar(camp, p["id_pedido"], "sin tiempo")
    assert cultivos.listar_mis_cultivos(camp)[0]["cantidad"] == 10


def test_cancelar_devuelve_stock_y_pide_ser_parte(escenario, crear_usuario):
    camp, rest, _ = escenario
    otro = crear_usuario("Restaurante", "o@x.com")
    p = pedidos.crear_pedido(rest, "c@x.com", "tomate", 3)
    with pytest.raises(PermisoDenegadoError):
        pedidos.cancelar(otro, p["id_pedido"])
    pedidos.cancelar(rest, p["id_pedido"])
    assert cultivos.listar_mis_cultivos(camp)[0]["cantidad"] == 10


def test_visibilidad_de_pedidos(escenario, crear_usuario, admin):
    camp, rest, domi = escenario
    otro = crear_usuario("Restaurante", "o@x.com")
    p = pedidos.crear_pedido(rest, "c@x.com", "tomate", 1)
    assert len(pedidos.listar(rest)) == 1 and len(pedidos.listar(camp)) == 1
    assert pedidos.listar(otro) == [] and pedidos.listar(domi) == []
    assert len(pedidos.listar(admin)) == 1
    with pytest.raises(PermisoDenegadoError):
        pedidos.obtener(otro, p["id_pedido"])
    assert pedidos.qr_png(rest, p["id_pedido"]).startswith(b"\x89PNG")


def test_servicio_de_roles_protege_lo_del_sistema(admin, escenario):
    camp, _, _ = escenario
    with pytest.raises(PermisoDenegadoError):
        roles.crear_rol(camp, "x", "X")
    roles.crear_rol(admin, "auditor", "Auditor")
    roles.agregar_permiso(admin, "auditor", "lectura", "ver_auditoria")
    roles.asignar_rol(admin, "c@x.com", "auditor")
    from servicios.autorizacion import tiene_permiso
    from repositorios import get_usuario_repo
    assert tiene_permiso(get_usuario_repo().obtener_por_email("c@x.com"), "ver_auditoria")
    with pytest.raises(PermisoDenegadoError):
        roles.eliminar_rol(admin, "admin")
    with pytest.raises(PermisoDenegadoError):
        roles.quitar_permiso(admin, "gestionar_roles")
    with pytest.raises(PermisoDenegadoError):
        roles.quitar_rol(admin, "ADMIN", "admin")
    with pytest.raises(ConflictoError):
        roles.crear_rol(admin, "auditor", "Otra vez")
    roles.eliminar_rol(admin, "auditor")
    assert not tiene_permiso(get_usuario_repo().obtener_por_email("c@x.com"), "ver_auditoria")
