"""Prueba el script de migración con una 'base Mongo' falsa (sin pymongo ni servidor)."""
import hashlib

from auth.seguridad import verificar_contrasena
from repositorios import get_cultivo_repo, get_notificacion_repo, get_pedido_repo, get_rol_repo, get_usuario_repo
from scripts import migrar_desde_mongo as mig


class _Coleccion:
    def __init__(self, docs):
        self.docs = docs

    def find(self, _filtro):
        return [dict(d, _id="oid") for d in self.docs]


class _FakeDb(dict):
    def __getitem__(self, k):
        return _Coleccion(self.get(k, []))


def _db():
    legado = hashlib.sha256(b"Vieja123!").hexdigest()
    return _FakeDb({
        "roles": [{"id": "campesino", "nombre": "Campesino", "vista": "open_campesino",
                   "permisos": {"lectura": [{"id": "ver_inventario", "nombre": "ver_inventario"}]}},
                  {"id": "especial", "nombre": "Especial", "permisos": {"otros": [{"id": "x", "nombre": "x"}]}}],
        "usuarios": [
            {"nombre": "Carlos", "email": "c@x.com", "password": legado, "tipo": "campesinos",
             "roles": ["campesino", "rol_que_ya_no_existe"], "permisos": ["ver_inventario"]},
            {"nombre": "El Surco", "email": "r@x.com", "password": legado, "tipo": "restaurantes", "roles": ["restaurante"]},
        ],
        "cultivos": [{"email": "c@x.com", "cultivos": [{"nombre": "papa", "cantidad": 5, "precio": 10}]}],
        "pedidos": [
            {"id_pedido": "PED-VIEJO", "restaurante": "El Surco", "campesino": "Carlos", "producto": "papa",
             "cantidad": 2, "precio_total": 20, "estado": "Pedido creado", "fecha": "2026-02-01 10:00:00",
             "historial": ["2026-02-01 10:00:00 - Pedido creado automáticamente."], "qr_base64": "AAA"},
            {"id_pedido": "PED-HUERFANO", "restaurante": "Nadie", "campesino": "Carlos"},
        ],
        "notificaciones": [{"destinatario": "Carlos", "titulo": "t", "mensaje": "m", "fecha_hora": "2026-02-01 10:00:00"}],
    })


def test_migracion_completa_e_idempotente():
    db = _db()
    assert mig.migrar_roles(db) == 1          # 'campesino' ya existía (rol inicial)
    assert mig.migrar_usuarios(db) == 2
    assert mig.migrar_cultivos(db) == 1
    assert mig.migrar_pedidos(db) == 1        # el huérfano se omite
    assert mig.migrar_notificaciones(db) == 1

    u = get_usuario_repo().obtener_por_email("c@x.com")
    assert u["roles"] == ["campesino"]        # rol inexistente descartado
    assert verificar_contrasena("Vieja123!", u["password"])  # hash legado intacto
    p = get_pedido_repo().listar()[0]
    assert p["estado"] == "CREADO" and p["historial"][0]["detalle"].startswith("Pedido creado")
    assert get_cultivo_repo().listar("c@x.com")[0]["cantidad"] == 5
    assert get_rol_repo().obtener("especial") and len(get_notificacion_repo().listar_todas()) == 1

    # segunda ejecución: no duplica nada
    assert (mig.migrar_roles(db), mig.migrar_usuarios(db), mig.migrar_cultivos(db),
            mig.migrar_pedidos(db), mig.migrar_notificaciones(db)) == (0, 0, 0, 0, 0)
