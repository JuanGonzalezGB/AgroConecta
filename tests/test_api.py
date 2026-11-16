import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def _registrar(client, tipo, email, nombre, **extra):
    datos = {"tipo": tipo, "nombre": nombre, "email": email, "password": "Clave123!", "telefono": "3001112233", **extra}
    r = client.post("/auth/registro", json=datos)
    assert r.status_code == 201, r.text
    return r.json()


def _login(client, email, password="Clave123!"):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def actores(client):
    _registrar(client, "campesino", "c@x.com", "Carlos Campo")
    _registrar(client, "restaurante", "r@x.com", "El Surco", nit="900123456-7")
    _registrar(client, "delivery", "d@x.com", "Diana Domi", tipo_vehiculo="Moto")
    return {"c": _login(client, "c@x.com"), "r": _login(client, "r@x.com"), "d": _login(client, "d@x.com"),
            "admin": _login(client, "ADMIN", "ADMIN")}


# ---------- auth ----------

def test_registro_login_y_me(client):
    u = _registrar(client, "campesino", "c@x.com", "Carlos Campo")
    assert "password" not in u and u["roles"] == ["campesino"]
    me = client.get("/auth/me", headers=_login(client, "c@x.com")).json()
    assert me["email"] == "c@x.com" and "ver_inventario" in me["permisos"]


def test_errores_de_registro_y_login(client):
    base = {"tipo": "campesino", "nombre": "Carlos", "email": "c@x.com", "password": "Clave123!", "telefono": "3001112233"}
    assert client.post("/auth/registro", json=base).status_code == 201
    r = client.post("/auth/registro", json=base)
    assert r.status_code == 409 and r.json()["codigo"] == "conflicto"
    assert client.post("/auth/registro", json=dict(base, email="otro@x.com", password="debil")).status_code == 422
    assert client.post("/auth/registro", json=dict(base, tipo="marciano")).status_code == 422
    assert client.post("/auth/login", json={"email": "c@x.com", "password": "mala"}).status_code == 401
    assert client.post("/auth/login", json={"email": "nadie@x.com", "password": "x"}).status_code == 401


def test_token_requerido_e_invalido(client):
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer basura"}).status_code == 401
    assert client.get("/pedidos").status_code == 401


def test_token_expirado(client, monkeypatch):
    import api.jwt_utils as j
    monkeypatch.setattr(j, "MINUTOS_EXPIRACION", -1)
    _registrar(client, "campesino", "c@x.com", "Carlos Campo")
    h = _login(client, "c@x.com")
    assert client.get("/auth/me", headers=h).status_code == 401


def test_login_por_formulario_para_swagger(client, actores):
    r = client.post("/auth/token", data={"username": "c@x.com", "password": "Clave123!"})
    assert r.status_code == 200 and r.json()["token_type"] == "bearer"


def test_docs_y_openapi_disponibles(client):
    assert client.get("/docs").status_code == 200
    rutas = client.get("/openapi.json").json()["paths"]
    assert "/pedidos/{id_pedido}/qr" in rutas and "/admin/roles" in rutas


# ---------- cultivos ----------

def test_crud_de_cultivos_y_autorizacion_por_rol(client, actores):
    h = actores["c"]
    assert client.post("/cultivos", json={"nombre": "Tomate", "cantidad": 10, "precio": 2000}, headers=h).status_code == 201
    r = client.post("/cultivos", json={"nombre": "tomate", "cantidad": 5, "precio": 2500}, headers=h)
    assert r.json() == {"nombre": "tomate", "cantidad": 15, "precio": 2500}
    assert client.get("/cultivos", headers=h).json() == [r.json()]
    assert client.post("/cultivos", json={"nombre": "x", "cantidad": 0, "precio": 1}, headers=h).status_code == 422
    # el restaurante no puede agregar ni eliminar cultivos
    assert client.post("/cultivos", json={"nombre": "x", "cantidad": 1, "precio": 1}, headers=actores["r"]).status_code == 403
    assert client.delete("/cultivos/tomate", headers=actores["r"]).status_code == 403
    assert client.delete("/cultivos/tomate", headers=h).status_code == 204
    assert client.delete("/cultivos/tomate", headers=h).status_code == 404


def test_restaurante_ve_campesinos_e_inventario(client, actores):
    client.post("/cultivos", json={"nombre": "papa", "cantidad": 8, "precio": 900}, headers=actores["c"])
    lista = client.get("/campesinos", headers=actores["r"]).json()
    assert lista[0]["email"] == "c@x.com" and lista[0]["cultivos"][0]["nombre"] == "papa"
    inv = client.get("/campesinos/c@x.com/inventario", headers=actores["r"]).json()
    assert inv["cultivos"][0]["cantidad"] == 8
    assert client.get("/campesinos/nadie@x.com/inventario", headers=actores["r"]).status_code == 404
    assert client.get("/campesinos").status_code == 401


# ---------- pedidos ----------

def _crear_pedido(client, actores, cantidad=4, agregar_stock=True):
    if agregar_stock:
        client.post("/cultivos", json={"nombre": "tomate", "cantidad": 10, "precio": 1000}, headers=actores["c"])
    r = client.post("/pedidos", json={"email_campesino": "c@x.com", "cultivo": "tomate", "cantidad": cantidad},
                    headers=actores["r"])
    return r


def test_flujo_completo_de_pedido_por_api(client, actores):
    r = _crear_pedido(client, actores)
    assert r.status_code == 201
    p = r.json()
    id_ = p["id_pedido"]
    assert p["estado"] == "CREADO" and p["precio_total"] == 4000

    assert client.post(f"/pedidos/{id_}/aceptar", headers=actores["c"]).json()["estado"] == "ACEPTADO"
    doms = client.get("/domiciliarios", headers=actores["c"]).json()
    assert doms[0]["email"] == "d@x.com"
    r = client.post(f"/pedidos/{id_}/asignar", json={"email_delivery": "d@x.com"}, headers=actores["c"])
    assert r.json()["delivery"] == "Diana Domi"
    h = actores["d"]
    assert client.post(f"/pedidos/{id_}/estado", json={"estado": "EN_CAMINO"}, headers=h).json()["estado"] == "EN_CAMINO"
    assert client.post(f"/pedidos/{id_}/estado", json={"estado": "ENTREGADO"}, headers=h).json()["estado"] == "ENTREGADO"

    historial = client.get(f"/pedidos/{id_}/historial", headers=actores["r"]).json()
    assert [e["evento"] for e in historial] == [
        "PEDIDO_CREADO", "PEDIDO_ACEPTADO", "DOMICILIARIO_ASIGNADO", "PEDIDO_EN_CAMINO", "PEDIDO_ENTREGADO"]
    for k in ("r", "c", "d"):
        assert len(client.get("/pedidos", headers=actores[k]).json()) == 1
    assert client.get("/pedidos?estado=entregado", headers=actores["r"]).json()[0]["id_pedido"] == id_

    notis = client.get("/notificaciones?solo_no_leidas=true", headers=actores["c"]).json()
    assert notis and notis[0]["titulo"] == "Nuevo pedido"
    assert client.post("/notificaciones/leer", headers=actores["c"]).json()["marcadas"] >= 1
    assert client.get("/notificaciones?solo_no_leidas=true", headers=actores["c"]).json() == []


def test_qr_del_pedido(client, actores):
    id_ = _crear_pedido(client, actores).json()["id_pedido"]
    r = client.get(f"/pedidos/{id_}/qr", headers=actores["r"])
    assert r.status_code == 200 and r.headers["content-type"] == "image/png" and r.content.startswith(b"\x89PNG")
    assert client.get(f"/pedidos/{id_}/qr", headers=actores["d"]).status_code == 403  # no participa


def test_autorizacion_por_rol_en_pedidos(client, actores):
    id_ = _crear_pedido(client, actores).json()["id_pedido"]
    # el campesino no compra; el restaurante no acepta; el domiciliario no ve pedidos ajenos
    assert client.post("/pedidos", json={"email_campesino": "c@x.com", "cultivo": "tomate", "cantidad": 1},
                       headers=actores["c"]).status_code == 403
    assert client.post(f"/pedidos/{id_}/aceptar", headers=actores["r"]).status_code == 403
    assert client.get(f"/pedidos/{id_}", headers=actores["d"]).status_code == 403
    assert client.post(f"/pedidos/{id_}/asignar", json={"email_delivery": "d@x.com"},
                       headers=actores["c"]).status_code == 409  # aún no aceptado
    assert client.post(f"/pedidos/{id_}/estado", json={"estado": "ASIGNADO"}, headers=actores["c"]).status_code == 422
    assert client.post(f"/pedidos/{id_}/estado", json={"estado": "VOLANDO"}, headers=actores["c"]).status_code == 422
    assert client.get("/pedidos/PED-NOEXISTE", headers=actores["r"]).status_code == 404
    assert client.get(f"/pedidos/{id_}", headers=actores["admin"]).status_code == 200  # el admin sí ve todo


def test_stock_insuficiente_y_cancelacion_devuelve_stock(client, actores):
    assert _crear_pedido(client, actores, cantidad=11).status_code == 409
    id_ = _crear_pedido(client, actores, cantidad=10, agregar_stock=False).json()["id_pedido"]
    assert client.get("/cultivos", headers=actores["c"]).json()[0]["cantidad"] == 0
    assert client.post(f"/pedidos/{id_}/cancelar", json={"motivo": "ya no"}, headers=actores["r"]).json()["estado"] == "CANCELADO"
    assert client.get("/cultivos", headers=actores["c"]).json()[0]["cantidad"] == 10
    assert client.post(f"/pedidos/{id_}/aceptar", headers=actores["c"]).status_code == 409


# ---------- administración ----------

def test_solo_admin_gestiona_roles(client, actores):
    for k in ("c", "r", "d"):
        assert client.get("/admin/roles", headers=actores[k]).status_code == 403
        assert client.post("/admin/roles", json={"id": "x", "nombre": "X"}, headers=actores[k]).status_code == 403
        assert client.get("/admin/usuarios", headers=actores[k]).status_code == 403
    assert client.get("/admin/roles").status_code == 401
    assert client.get("/admin/roles", headers=actores["admin"]).status_code == 200


def test_admin_crea_edita_y_asigna_rol_con_permisos_dinamicos(client, actores):
    a = actores["admin"]
    assert client.post("/admin/roles", json={"id": "auditor", "nombre": "Auditor"}, headers=a).status_code == 201
    assert client.post("/admin/roles", json={"id": "auditor", "nombre": "Otra vez"}, headers=a).status_code == 409
    r = client.post("/admin/roles/auditor/permisos", json={"categoria": "administrativo", "id": "gestionar_roles"}, headers=a)
    assert r.status_code == 201
    assert client.post("/admin/roles/auditor/permisos", json={"categoria": "inventada", "id": "x"}, headers=a).status_code == 422
    assert client.put("/admin/roles/auditor", json={"nombre": "Auditor general"}, headers=a).json()["nombre"] == "Auditor general"

    # el campesino aún no puede gestionar roles...
    assert client.get("/admin/roles", headers=actores["c"]).status_code == 403
    # ...hasta que el admin le asigna el rol con ese permiso (aplica sin volver a iniciar sesión)
    asignado = client.post("/admin/usuarios/c@x.com/roles", json={"rol_id": "auditor"}, headers=a).json()
    assert "gestionar_roles" in asignado["permisos"]
    assert client.get("/admin/roles", headers=actores["c"]).status_code == 200

    # renombrar y quitar permisos / roles
    assert client.put("/admin/permisos/gestionar_roles", json={"nombre": "Gestionar roles!"}, headers=a).status_code == 200
    assert client.delete("/admin/permisos/gestionar_roles", headers=a).status_code == 403  # del sistema
    assert client.delete("/admin/roles/auditor", headers=a).status_code == 204
    assert client.get("/admin/roles", headers=actores["c"]).status_code == 403  # perdió el rol
    assert client.delete("/admin/roles/admin", headers=a).status_code == 403
    assert client.delete("/admin/usuarios/ADMIN/roles/admin", headers=a).status_code == 403
    assert client.post("/admin/usuarios/c@x.com/roles", json={"rol_id": "no_existe"}, headers=a).status_code == 404
