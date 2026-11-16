import logging
from tkinter import messagebox, simpledialog

from auth.permisos import require_permission
from modelo.CRU import cargarCultivos
from modelo.facturaModel import generarFacturaTxt
from modelo.pedidos_utils import registrar_pedido
from repositorios import get_cultivo_repo

logger = logging.getLogger(__name__)


class ControladorCompras:
    def __init__(self, user, root, notificationService):
        self.user = user
        self.root = root
        self.notificationService = notificationService

    @require_permission("realizar_compra")
    def comprar_cultivo(self, campesino, index, *, user):
        try:
            email_campesino = campesino["email"]
            cultivos_usuario = cargarCultivos().get(email_campesino, [])

            if index >= len(cultivos_usuario):
                messagebox.showerror("Error", "El cultivo seleccionado no existe.")
                logger.error(f"Index de cultivo fuera de rango para {email_campesino}")
                return

            cultivo = dict(cultivos_usuario[index])
            cantidad_disponible = cultivo.get("cantidad", 0)
            precio = cultivo.get("precio", 0)

            cantidad = simpledialog.askinteger(
                "Comprar cultivo",
                f"¿Cuántas unidades deseas comprar?\nDisponibles: {cantidad_disponible}",
                minvalue=1
            )
            if cantidad is None:
                return

            # Descuento atómico: falla si otro cliente ya se llevó el stock.
            if not get_cultivo_repo().descontar_stock(email_campesino, cultivo["nombre"], cantidad):
                messagebox.showerror("Stock insuficiente", "No hay suficientes unidades disponibles.")
                logger.warning(f"Intento de compra excediendo stock para {email_campesino}, index {index}")
                return

            total = cantidad * precio
            cultivo["cantidad"] = cantidad_disponible - cantidad
            ruta = generarFacturaTxt(self.user, campesino, cultivo, cantidad, total)

            nuevo = registrar_pedido(restaurante=self.user, campesino=campesino, cultivo=cultivo, cantidad=cantidad)

            # --- Notificaciones ---
            self.notificationService.notificar(
                campesino.get("nombre", email_campesino),
                "Compra confirmada",
                f"El restaurante {self.user.get('nombre', 'Restaurante')} confirmó la compra de {cantidad} unidades.",
                mostrar_inmediatamente=False
            )
            self.notificationService.notificar(
                self.user.get("nombre", "Restaurante"),
                "Compra realizada",
                f"Compra realizada exitosamente al campesino {campesino.get('nombre', email_campesino)}.",
                mostrar_inmediatamente=False
            )

            messagebox.showinfo(
                "Compra realizada",
                f"Has comprado {cantidad} unidades por ${total:,}.\nFactura generada en:\n{ruta}\n"
                f"Pedido registrado con ID: {nuevo['id_pedido']}"
            )

        except Exception as e:
            logger.error(f"Error en el proceso de compra: {e}")
            messagebox.showerror("Error", f"Ocurrió un error: {e}")
