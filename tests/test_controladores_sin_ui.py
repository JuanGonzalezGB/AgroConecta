"""Controladores de escritorio ejercitados sin ventanas (messagebox y diálogos simulados)."""
import pytest

pytest.importorskip("tkinter")

from modelo.CRU import obtenerCultivosUsuario  # noqa: E402
from repositorios import get_notificacion_repo, get_usuario_repo  # noqa: E402


class _Avisos:
    def __init__(self):
        self.infos, self.errores = [], []


@pytest.fixture
def avisos(monkeypatch):
    a = _Avisos()
    monkeypatch.setattr("tkinter.messagebox.showinfo", lambda t, m, **k: a.infos.append(m))
    monkeypatch.setattr("tkinter.messagebox.showerror", lambda t, m, **k: a.errores.append(m))
    monkeypatch.setattr("tkinter.messagebox.showwarning", lambda t, m, **k: a.errores.append(m))
    return a


def test_compra_desde_el_controlador_descuenta_stock_crea_pedido_y_notifica(
        monkeypatch, avisos, crear_usuario, tmp_path):
    from controlador.controladorCompras import ControladorCompras
    from modelo.CRUD import crearCultivo
    from notificaciones.notification_repository import NotificationRepository
    from notificaciones.notification_sender import NotificationSender
    from notificaciones.notification_service import NotificationService

    monkeypatch.setattr("modelo.facturaModel.CARPETA", str(tmp_path))
    monkeypatch.setattr("tkinter.simpledialog.askinteger", lambda *a, **k: 4)

    camp = crear_usuario("Campesino", "c@x.com", nombre="Carlos")
    rest = crear_usuario("Restaurante", "r@x.com", nombre="El Surco")
    crearCultivo(camp, {"nombre": "papa", "cantidad": 10, "precio": 1000.0})

    servicio = NotificationService(NotificationRepository(), NotificationSender(None))
    ctrl = ControladorCompras(rest, None, servicio)
    ctrl.comprar_cultivo(camp, 0, user=rest)

    assert avisos.errores == []
    assert "Pedido registrado con ID: PED-" in avisos.infos[0]
    assert obtenerCultivosUsuario(camp)[0]["cantidad"] == 6
    assert list(tmp_path.glob("factura_*.txt"))
    assert get_notificacion_repo().listar("Carlos")[0]["titulo"] == "Nuevo pedido"

    from controlador.controlador_pedidos_restaurante import ControladorPedidosRestaurante
    mis = ControladorPedidosRestaurante(rest).listar_mis_pedidos()
    assert len(mis) == 1 and mis[0]["campesino"] == "Carlos" and mis[0]["historial"][0]["fecha"]


def test_compra_con_stock_insuficiente_no_crea_pedido(monkeypatch, avisos, crear_usuario):
    from controlador.controladorCompras import ControladorCompras
    from modelo.CRUD import crearCultivo
    from modelo.pedidos_utils import listar_pedidos

    monkeypatch.setattr("tkinter.simpledialog.askinteger", lambda *a, **k: 99)
    camp = crear_usuario("Campesino", "c@x.com")
    rest = crear_usuario("Restaurante", "r@x.com")
    crearCultivo(camp, {"nombre": "papa", "cantidad": 10, "precio": 1000.0})

    ControladorCompras(rest, None, None).comprar_cultivo(camp, 0, user=rest)
    assert avisos.errores and listar_pedidos() == []
    assert obtenerCultivosUsuario(camp)[0]["cantidad"] == 10


def test_compra_sin_permiso_de_realizar_compra(monkeypatch, avisos, crear_usuario):
    from controlador.controladorCompras import ControladorCompras
    camp = crear_usuario("Campesino", "c@x.com")
    resultado = ControladorCompras(camp, None, None).comprar_cultivo(camp, 0, user=camp)
    assert resultado[0] is False


def test_cambio_de_contrasena_en_perfil(crear_usuario):
    from auth.seguridad import es_hash_bcrypt, verificar_contrasena
    from controlador.controladorPerfil import ControladorPerfil

    u = crear_usuario("Campesino", "c@x.com", password="Clave123!")
    ctrl = ControladorPerfil(u)
    assert ctrl.cambiar_contraseña("mala", "Nueva123!")[0] is False
    assert ctrl.cambiar_contraseña("Clave123!", "debil")[0] is False
    assert ctrl.cambiar_contraseña("Clave123!", "Nueva123!")[0] is True
    guardado = get_usuario_repo().obtener_por_email("c@x.com")["password"]
    assert es_hash_bcrypt(guardado) and verificar_contrasena("Nueva123!", guardado)


def test_controlador_de_registro_de_cultivos(avisos, crear_usuario):
    from controlador.controladorRegis import ControladorRegis
    camp = crear_usuario("Campesino", "c@x.com")
    ctrl = ControladorRegis({"nombre": "yuca", "cantidad": 7, "precio": 500.0}, None, None, camp, None, None)
    ctrl.submitCultivo(user=camp)
    assert obtenerCultivosUsuario(camp) == [{"nombre": "yuca", "cantidad": 7, "precio": 500.0}]
    ctrl.eliminarCultivo("yuca", user=camp)
    assert obtenerCultivosUsuario(camp) == []
