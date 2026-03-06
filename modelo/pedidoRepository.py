# modelo/pedido_repository.py
import os
import json


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RUTA_PEDIDOS = os.path.join(DATA_DIR, "pedidos.json")

def _asegurar_archivo():
    if not os.path.exists(RUTA_PEDIDOS):
        with open(RUTA_PEDIDOS, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def cargar_pedidos() -> list:
    _asegurar_archivo()
    with open(RUTA_PEDIDOS, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_pedidos(data: list) -> None:
    _asegurar_archivo()
    with open(RUTA_PEDIDOS, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def guardar_pedido(pedido: dict) -> None:
    pedidos = cargar_pedidos()
    pedidos.append(pedido)
    guardar_pedidos(pedidos)


def actualizar_pedido(pedido_actualizado: dict) -> None:
    pedidos = cargar_pedidos()
    for i, p in enumerate(pedidos):
        if p.get("id_pedido") == pedido_actualizado.get("id_pedido"):
            pedidos[i] = pedido_actualizado
            break
    guardar_pedidos(pedidos)


def obtener_pedidos_por_restaurante(nombre_restaurante: str) -> list:
    pedidos = cargar_pedidos()
    return [p for p in pedidos if p.get("restaurante") == nombre_restaurante]
