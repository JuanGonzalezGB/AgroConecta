"""Copia los datos de una base MongoDB antigua a la base actual (SQLite por defecto).

Es opcional y solo la necesitas si ya tenías datos en Mongo. Requiere pymongo:

    pip install -r requirements-migracion.txt
    MONGO_URI="mongodb://usuario:clave@host:27017/?authSource=admin" python scripts/migrar_desde_mongo.py

Variables de entorno:
    MONGO_URI  (obligatoria)  URI de conexión a Mongo.
    MONGO_DB   (opcional)     nombre de la base, por defecto "miapp".
    DATABASE_URL              destino; por defecto data/agroconecta.db.

Es idempotente: lo que ya existe en el destino (email de usuario, id de rol, id de pedido,
cultivo por campesino y nombre) se omite. Las contraseñas se copian tal cual (SHA-256 legado)
y se migran a bcrypt la primera vez que cada usuario inicia sesión.
Además de usuarios, roles, pedidos y notificaciones, copia los cultivos (colección "cultivos").
"""
import logging
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modelo import pedidoModel  # noqa: E402
from modelo.inicializacion import inicializar_sistema  # noqa: E402
from repositorios import (  # noqa: E402
    get_cultivo_repo, get_notificacion_repo, get_pedido_repo, get_rol_repo, get_usuario_repo,
)

logger = logging.getLogger("migrar_desde_mongo")

ESTADOS_LEGADOS = {"pedido creado": "CREADO", "solicitado": "CREADO"}
_LINEA_HISTORIAL = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (.*)$")


def _quitar_id(doc: dict) -> dict:
    return {k: v for k, v in doc.items() if k != "_id"}


def migrar_roles(db) -> int:
    repo, n = get_rol_repo(), 0
    for doc in db["roles"].find({}):
        rol = _quitar_id(doc)
        if repo.obtener(rol["id"]) is None:
            repo.crear(rol)
            n += 1
    return n


def migrar_usuarios(db) -> int:
    repo, n = get_usuario_repo(), 0
    for doc in db["usuarios"].find({}):
        u = _quitar_id(doc)
        if not u.get("email") or repo.obtener_por_email(u["email"]):
            continue
        u.setdefault("tipo", "admin" if "admin" in u.get("roles", []) else "otros")
        roles_validos = {r["id"] for r in get_rol_repo().listar()}
        u["roles"] = [r for r in u.get("roles", []) if r in roles_validos]
        repo.crear(u)
        n += 1
    return n


def migrar_cultivos(db) -> int:
    repo, n = get_cultivo_repo(), 0
    usuarios = get_usuario_repo()
    for doc in db["cultivos"].find({}):
        email = doc.get("email")
        if not email or usuarios.obtener_por_email(email) is None:
            logger.warning("Cultivos de %s omitidos: usuario inexistente", email)
            continue
        existentes = {c["nombre"] for c in repo.listar(email)}
        for c in doc.get("cultivos", []):
            if c["nombre"] not in existentes:
                repo.agregar_o_sumar(email, c["nombre"], c.get("cantidad", 0), c.get("precio", 0))
                n += 1
    return n


def _por_nombre(nombre: str, tipo: str):
    for u in get_usuario_repo().listar():
        if u["tipo"] == tipo and u["nombre"] == nombre:
            return u
    return None


def _historial(items) -> list[dict]:
    eventos = []
    for it in items or []:
        if isinstance(it, str):
            m = _LINEA_HISTORIAL.match(it)
            ts, texto = (m.group(1), m.group(2)) if m else ("", it)
            eventos.append({"timestamp": ts or None, "evento": "EVENTO_LEGADO", "detalle": texto})
        elif isinstance(it, dict):
            eventos.append({
                "timestamp": it.get("timestamp") or it.get("fecha"),
                "evento": it.get("evento", "EVENTO_LEGADO"),
                "detalle": it.get("detalle", ""),
            })
    return eventos


def migrar_pedidos(db) -> int:
    repo, n = get_pedido_repo(), 0
    for doc in db["pedidos"].find({}):
        p = _quitar_id(doc)
        if repo.obtener(p["id_pedido"]):
            continue
        rest = _por_nombre(p.get("restaurante"), "restaurantes")
        camp = _por_nombre(p.get("campesino"), "campesinos")
        if not rest or not camp:
            logger.warning("Pedido %s omitido: no se encontró restaurante o campesino por nombre", p["id_pedido"])
            continue
        dom = _por_nombre(p["delivery"], "deliverys") if p.get("delivery") else None
        estado = p.get("estado", "CREADO")
        estado = ESTADOS_LEGADOS.get(estado.lower(), estado)
        if estado not in pedidoModel.ESTADOS:
            estado = "CREADO"
        repo.crear({
            "id_pedido": p["id_pedido"],
            "restaurante_email": rest["email"], "campesino_email": camp["email"],
            "delivery_email": dom["email"] if dom else None,
            "producto": p.get("producto") or (p.get("info_producto") or {}).get("nombre", ""),
            "cantidad": p.get("cantidad", 0), "precio_total": p.get("precio_total", 0),
            "estado": estado, "fecha": p.get("fecha"),
            "info_producto": p.get("info_producto") or {},
            "qr_base64": p.get("qr_base64"),
            "historial": _historial(p.get("historial")),
        })
        n += 1
    return n


def migrar_notificaciones(db) -> int:
    repo = get_notificacion_repo()
    existentes = {(x["destinatario"], x["titulo"], x["mensaje"], x["fecha_hora"]) for x in repo.listar_todas()}
    n = 0
    for doc in db["notificaciones"].find({}):
        d = _quitar_id(doc)
        clave = (d.get("destinatario"), d.get("titulo", ""), d.get("mensaje", ""), d.get("fecha_hora"))
        if not d.get("destinatario") or clave in existentes:
            continue
        repo.guardar(d)
        n += 1
    return n


def main() -> None:
    uri = os.getenv("MONGO_URI")
    if not uri:
        sys.exit("Define la variable de entorno MONGO_URI para migrar desde Mongo.")
    try:
        from pymongo import MongoClient
    except ImportError:
        sys.exit("Falta pymongo: pip install -r requirements-migracion.txt")

    inicializar_sistema()
    db = MongoClient(uri)[os.getenv("MONGO_DB", "miapp")]
    # El orden importa: roles -> usuarios -> cultivos/pedidos/notificaciones.
    for nombre, funcion in (("roles", migrar_roles), ("usuarios", migrar_usuarios),
                            ("cultivos", migrar_cultivos), ("pedidos", migrar_pedidos),
                            ("notificaciones", migrar_notificaciones)):
        logger.info("%s nuevos migrados: %d", nombre, funcion(db))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
