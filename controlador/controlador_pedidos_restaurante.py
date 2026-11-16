import logging

from modelo.pedidos_utils import listar_pedidos

logger = logging.getLogger(__name__)


class ControladorPedidosRestaurante:
    """Consulta de pedidos del restaurante. La creación vive en ``ControladorCompras``."""

    def __init__(self, restaurante_actual: dict):
        self.restaurante = restaurante_actual

    def listar_mis_pedidos(self):
        return listar_pedidos(restaurante_email=self.restaurante["email"])
