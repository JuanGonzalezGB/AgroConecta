"""Carga datos de demostración (idempotente: se puede ejecutar varias veces).

Uso (desde la raíz del repositorio):
    python scripts/seed_demo.py

Usa la base indicada por DATABASE_URL (por defecto data/agroconecta.db).

Cuentas de demo (el login pide email y contraseña):
    Rol           Email                      Contraseña
    Admin         ADMIN                      ADMIN
    Campesino     campesino@demo.com         Campesino123!
    Restaurante   restaurante@demo.com       Restaurante123!
    Domiciliario  domiciliario@demo.com      Domiciliario123!

Solo para pruebas locales: no uses estas credenciales en un entorno real.
"""
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.seguridad import hash_contrasena  # noqa: E402
from modelo.CRUD import crearCultivo, crearUsuario  # noqa: E402
from modelo.inicializacion import inicializar_sistema  # noqa: E402
from modelo.pedidos_utils import listar_pedidos, registrar_pedido  # noqa: E402
from repositorios import get_cultivo_repo, get_usuario_repo  # noqa: E402

logger = logging.getLogger("seed_demo")

USUARIOS_DEMO = [
    ("Campesino", {
        "nombre": "Carlos Campesino", "email": "campesino@demo.com", "password": "Campesino123!",
        "telefono": "3001112233", "fecha_nacimiento": "1980-05-12", "direccion": "Vereda La Esperanza",
    }),
    ("Restaurante", {
        "nombre": "Restaurante El Surco", "email": "restaurante@demo.com", "password": "Restaurante123!",
        "nit": "900123456-7", "telefono": "3004445566", "direccion": "Calle 10 # 5-20",
    }),
    ("Delivery", {
        "nombre": "Diana Domiciliaria", "email": "domiciliario@demo.com", "password": "Domiciliario123!",
        "telefono": "3007778899", "tipo_vehiculo": "Moto",
    }),
]

CULTIVOS_DEMO = [
    {"nombre": "tomate", "cantidad": 120, "precio": 2500.0},
    {"nombre": "papa", "cantidad": 300, "precio": 1800.0},
    {"nombre": "cebolla", "cantidad": 80, "precio": 2200.0},
]


def sembrar() -> None:
    inicializar_sistema()  # tablas + roles iniciales + admin
    repo = get_usuario_repo()

    for tipo, datos in USUARIOS_DEMO:
        if repo.obtener_por_email(datos["email"]):
            logger.info("Ya existe %s, se omite", datos["email"])
            continue
        datos = dict(datos, password=hash_contrasena(datos["password"]))
        ok, msg = crearUsuario(tipo, datos)
        logger.info("%s: %s", datos["email"], msg)
        if not ok:
            raise RuntimeError(f"No se pudo crear {datos['email']}: {msg}")

    campesino = repo.obtener_por_email("campesino@demo.com")
    restaurante = repo.obtener_por_email("restaurante@demo.com")

    # crearCultivo suma cantidades, así que solo se siembra si el campesino no tiene cultivos.
    if not get_cultivo_repo().listar(campesino["email"]):
        for cultivo in CULTIVOS_DEMO:
            crearCultivo(campesino, dict(cultivo))
        logger.info("Cultivos de demo creados")

    if not listar_pedidos(restaurante_email=restaurante["email"]):
        tomate = get_cultivo_repo().listar(campesino["email"])[0]
        pedido = registrar_pedido(restaurante, campesino, tomate, 10)
        logger.info("Pedido de demo creado: %s", pedido["id_pedido"])

    logger.info("Datos de demo listos.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sembrar()
