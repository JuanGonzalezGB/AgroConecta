import pytest
from sqlalchemy import text

from repositorios import (
    get_cultivo_repo, get_notificacion_repo, get_pedido_repo, get_rol_repo, get_usuario_repo,
)
from repositorios import database
from repositorios.errores import DuplicadoError, NoEncontradoError


def test_sqlite_con_claves_foraneas_activas():
    with database.get_engine().connect() as c:
        assert c.execute(text("PRAGMA foreign_keys")).scalar() == 1


def test_wal_en_archivo(tmp_path):
    eng = database.make_engine(f"sqlite:///{tmp_path / 'x.db'}")
    with eng.connect() as c:
        assert c.execute(text("PRAGMA journal_mode")).scalar() == "wal"
    eng.dispose()


# ---------- usuarios ----------

def test_usuario_crear_obtener_y_email_unico(crear_usuario):
    crear_usuario("Campesino", "c@x.com", nombre="Camp", telefono="3001112233", direccion="Vereda")
    u = get_usuario_repo().obtener_por_email("c@x.com")
    assert u["nombre"] == "Camp" and u["tipo"] == "campesinos" and u["roles"] == ["campesino"]
    assert u["telefono"] == "3001112233" and "nit" not in u
    assert "ver_inventario" in u["permisos"]
    with pytest.raises(DuplicadoError):
        get_usuario_repo().crear({"email": "c@x.com", "nombre": "otro", "password": "h", "tipo": "campesinos"})


def test_usuario_guardar_es_upsert_y_reemplaza_roles(crear_usuario):
    crear_usuario("Campesino", "c@x.com")
    repo = get_usuario_repo()
    repo.guardar({"email": "c@x.com", "nombre": "Nuevo", "roles": ["campesino", "restaurante", "rol_borrado"]})
    u = repo.obtener_por_email("c@x.com")
    assert u["nombre"] == "Nuevo" and sorted(u["roles"]) == ["campesino", "restaurante"]
    repo.guardar({"email": "nuevo@x.com", "nombre": "N", "password": "h", "tipo": "deliverys"})
    assert repo.obtener_por_email("nuevo@x.com")["tipo"] == "deliverys"


def test_usuario_roles_inexistentes_fallan(crear_usuario):
    crear_usuario("Campesino", "c@x.com")
    with pytest.raises(NoEncontradoError):
        get_usuario_repo().establecer_roles("c@x.com", ["no_existe"])


def test_usuario_eliminar_borra_en_cascada(crear_usuario):
    crear_usuario("Campesino", "c@x.com")
    get_cultivo_repo().agregar_o_sumar("c@x.com", "papa", 5, 1.0)
    assert get_usuario_repo().eliminar("c@x.com")
    assert get_cultivo_repo().listar("c@x.com") == []
    assert not get_usuario_repo().eliminar("c@x.com")


# ---------- cultivos ----------

def test_cultivos_suma_y_actualiza_precio(crear_usuario):
    crear_usuario("Campesino", "c@x.com")
    repo = get_cultivo_repo()
    repo.agregar_o_sumar("c@x.com", "papa", 10, 100)
    repo.agregar_o_sumar("c@x.com", "papa", 5, 120)
    assert repo.listar("c@x.com") == [{"nombre": "papa", "cantidad": 15, "precio": 120}]
    assert repo.eliminar("c@x.com", "papa") and not repo.eliminar("c@x.com", "papa")


def test_descuento_de_stock_atomico(crear_usuario):
    crear_usuario("Campesino", "c@x.com")
    repo = get_cultivo_repo()
    repo.agregar_o_sumar("c@x.com", "papa", 10, 100)
    assert repo.descontar_stock("c@x.com", "papa", 4)
    assert not repo.descontar_stock("c@x.com", "papa", 7)  # solo quedan 6
    assert repo.listar("c@x.com")[0]["cantidad"] == 6


def test_cultivos_reemplazar_y_listar_todos(crear_usuario):
    crear_usuario("Campesino", "c@x.com")
    repo = get_cultivo_repo()
    repo.agregar_o_sumar("c@x.com", "papa", 1, 1)
    repo.reemplazar("c@x.com", [{"nombre": "papa", "cantidad": 9, "precio": 2}, {"nombre": "yuca", "cantidad": 3, "precio": 5}])
    assert [c["nombre"] for c in repo.listar_todos()["c@x.com"]] == ["papa", "yuca"]
    repo.reemplazar("c@x.com", [{"nombre": "yuca", "cantidad": 3, "precio": 5}])
    assert [c["nombre"] for c in repo.listar("c@x.com")] == ["yuca"]


# ---------- pedidos ----------

def _pedido_base(rest, camp):
    from modelo import pedidoModel as pm
    return pm.crear_pedido(camp, rest, {"nombre": "papa", "siembra": "2026-01-01"}, cantidad=2, precio_total=20)


def test_pedido_ida_y_vuelta_con_historial(crear_usuario):
    camp = crear_usuario("Campesino", "c@x.com", nombre="Camp")
    rest = crear_usuario("Restaurante", "r@x.com", nombre="Rest")
    repo = get_pedido_repo()
    creado = repo.crear(_pedido_base(rest, camp))
    p = repo.obtener(creado["id_pedido"])
    assert p["restaurante"] == "Rest" and p["campesino"] == "Camp" and p["delivery"] is None
    assert p["info_producto"]["siembra"] == "2026-01-01"
    assert [e["evento"] for e in p["historial"]] == ["PEDIDO_CREADO"]
    assert p["historial"][0]["fecha"] == p["historial"][0]["timestamp"]  # la vista usa 'fecha'


def test_pedido_actualizar_agrega_solo_eventos_nuevos(crear_usuario):
    from modelo import pedidoModel as pm
    camp = crear_usuario("Campesino", "c@x.com")
    rest = crear_usuario("Restaurante", "r@x.com")
    dom = crear_usuario("Delivery", "d@x.com", nombre="Dom")
    repo = get_pedido_repo()
    p = repo.crear(_pedido_base(rest, camp))
    pm.aceptar(p)
    pm.asignar_delivery(p, dom)
    repo.actualizar(p)
    repo.actualizar(p)  # idempotente: no duplica eventos
    p2 = repo.obtener(p["id_pedido"])
    assert p2["estado"] == "ASIGNADO" and p2["delivery"] == "Dom"
    assert len(p2["historial"]) == 3


def test_pedido_listar_con_filtros(crear_usuario):
    camp = crear_usuario("Campesino", "c@x.com")
    rest1 = crear_usuario("Restaurante", "r1@x.com")
    rest2 = crear_usuario("Restaurante", "r2@x.com")
    repo = get_pedido_repo()
    repo.crear(_pedido_base(rest1, camp))
    repo.crear(_pedido_base(rest2, camp))
    assert len(repo.listar()) == 2
    assert len(repo.listar(restaurante_email="r1@x.com")) == 1
    assert len(repo.listar(campesino_email="c@x.com", estado="CREADO")) == 2
    assert repo.listar(estado="ENTREGADO") == []
    assert repo.listar(restaurante_email="nadie@x.com") == []


def test_pedido_con_usuario_inexistente_falla(crear_usuario):
    camp = crear_usuario("Campesino", "c@x.com")
    p = _pedido_base({"nombre": "X", "email": "fantasma@x.com"}, camp)
    with pytest.raises(NoEncontradoError):
        get_pedido_repo().crear(p)


# ---------- roles ----------

def test_roles_iniciales_y_duplicado():
    ids = [r["id"] for r in get_rol_repo().listar()]
    assert {"admin", "campesino", "restaurante", "delivery"} <= set(ids)
    with pytest.raises(DuplicadoError):
        get_rol_repo().crear({"id": "admin", "nombre": "otra vez"})


# ---------- notificaciones ----------

def test_notificaciones_guardar_listar_y_marcar_leidas():
    repo = get_notificacion_repo()
    repo.guardar({"destinatario": "Ana", "titulo": "t1", "mensaje": "m1"})
    repo.guardar({"destinatario": "Ana", "titulo": "t2", "mensaje": "m2", "mostrar_inmediatamente": False})
    repo.guardar({"destinatario": "Beto", "titulo": "t3", "mensaje": "m3"})
    assert len(repo.listar("Ana")) == 2 and len(repo.listar_todas()) == 3
    assert repo.marcar_como_leidas("Ana") == 2
    assert repo.listar("Ana", solo_no_leidas=True) == []
    assert len(repo.listar("Beto", solo_no_leidas=True)) == 1
