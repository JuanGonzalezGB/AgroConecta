"""Operaciones de pedidos: orquestan ``pedidoModel`` (reglas) y el repositorio (persistencia)."""
import base64
import json
import logging
from io import BytesIO

import qrcode

from modelo import pedidoModel
from repositorios import get_pedido_repo
from repositorios.errores import NoEncontradoError

logger = logging.getLogger(__name__)


def generar_qr_pedido(pedido: dict) -> str:
    """Genera el QR del pedido y lo devuelve como PNG en base64."""
    contenido = json.dumps(
        {k: pedido.get(k) for k in ("id_pedido", "restaurante", "campesino", "producto", "cantidad")},
        ensure_ascii=False,
    )
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
    qr.add_data(contenido)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def registrar_pedido(restaurante: dict, campesino: dict, cultivo: dict, cantidad: int) -> dict:
    """Crea y guarda un pedido (con historial y QR). Lanza excepción si no se pudo guardar."""
    pedido = pedidoModel.crear_pedido(
        campesino, restaurante, cultivo,
        cantidad=cantidad, precio_total=cantidad * cultivo.get("precio", 0),
    )
    pedido["qr_base64"] = generar_qr_pedido(pedido)
    guardado = get_pedido_repo().crear(pedido)
    logger.info(f"Pedido {guardado['id_pedido']} guardado")
    return guardado


def obtener_pedido(id_pedido: str) -> dict | None:
    return get_pedido_repo().obtener(id_pedido)


def listar_pedidos(**filtros) -> list:
    """Filtros: restaurante_email, campesino_email, delivery_email, estado."""
    return get_pedido_repo().listar(**filtros)


def cargar_pedidos() -> dict:
    """Todos los pedidos, con el formato histórico ``{"pedidos": [...]}``."""
    return {"pedidos": get_pedido_repo().listar()}


def _transicionar(id_pedido: str, accion, *args) -> dict:
    repo = get_pedido_repo()
    pedido = repo.obtener(id_pedido)
    if pedido is None:
        raise NoEncontradoError(f"Pedido {id_pedido} no encontrado")
    accion(pedido, *args)  # lanza EstadoInvalidoError si la transición no es válida
    return repo.actualizar(pedido)


def aceptar_pedido(id_pedido: str) -> dict:
    return _transicionar(id_pedido, pedidoModel.aceptar)


def rechazar_pedido(id_pedido: str, motivo: str = "") -> dict:
    return _transicionar(id_pedido, pedidoModel.rechazar, motivo)


def cancelar_pedido(id_pedido: str, motivo: str = "") -> dict:
    return _transicionar(id_pedido, pedidoModel.cancelar, motivo)


def asignar_delivery(id_pedido: str, delivery: dict) -> dict:
    return _transicionar(id_pedido, pedidoModel.asignar_delivery, delivery)


def marcar_en_camino(id_pedido: str) -> dict:
    return _transicionar(id_pedido, pedidoModel.marcar_en_camino)


def marcar_entregado(id_pedido: str) -> dict:
    return _transicionar(id_pedido, pedidoModel.marcar_entregado)
