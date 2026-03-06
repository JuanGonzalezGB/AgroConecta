import uuid
import qrcode
from datetime import datetime
from modelo.pedidos_utils import cargar_pedidos

import os

class ControladorPedidosRestaurante:
    def __init__(self, restaurante_actual: dict):
        self.restaurante = restaurante_actual

    def generar_qr(self, texto, id_pedido):
        carpeta = "qr_pedidos"
        os.makedirs(carpeta, exist_ok=True)

        ruta_qr = os.path.join(carpeta, f"qr_{id_pedido}.png")

        img = qrcode.make(texto)
        img.save(ruta_qr)

        return ruta_qr

    def registrar_pedido(self, campesino, producto, cantidad):
        data = cargar_pedidos()

        id_pedido = str(uuid.uuid4())

        info_qr = f"Pedido: {id_pedido}\n" \
                  f"Restaurante: {self.restaurante['nombre']}\n" \
                  f"Campesino: {campesino['nombre']}\n" \
                  f"Producto: {producto['nombre']}\n" \
                  f"Cantidad: {cantidad}"

        ruta_qr = self.generar_qr(info_qr, id_pedido)

        nuevo_pedido = {
            "id_pedido": id_pedido,
            "restaurante": self.restaurante["nombre"],
            "campesino": campesino["nombre"],
            "producto": producto["nombre"],
            "cantidad": cantidad,
            "estado": "Solicitado",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "historial": [
                {
                    "evento": "Pedido creado",
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            ],
            "codigo_qr": ruta_qr
        }

        data["pedidos"].append(nuevo_pedido)
       # guardar_pedidos(data)

        return nuevo_pedido

    def listar_mis_pedidos(self):
        data = cargar_pedidos()

    # 🛠 data puede ser LISTA o DICT → lo convertimos
        if isinstance(data, list):
            pedidos = data
        elif isinstance(data, dict) and "pedidos" in data:
            pedidos = data["pedidos"]
        else:
            pedidos = []  # estructura vacía inesperada

        return [p for p in pedidos if p.get("restaurante") == self.restaurante["nombre"]]
