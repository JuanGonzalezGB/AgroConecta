import logging
from tkinter import messagebox, simpledialog

from auth.permisos import require_permission
from modelo.facturaModel import generarFacturaTxt
from servicios import cultivos, pedidos
from servicios.errores import ServicioError

logger = logging.getLogger(__name__)


class ControladorCompras:
    """Capa fina de UI: pide datos al usuario y delega la lógica en ``servicios``."""

    def __init__(self, user, root, notificationService=None):
        self.user = user
        self.root = root
        self.notificationService = notificationService  # se conserva por compatibilidad con las vistas

    @require_permission("realizar_compra")
    def comprar_cultivo(self, campesino, index, *, user):
        try:
            email_campesino = campesino["email"]
            inventario = cultivos.inventario_de_campesino(self.user, email_campesino)["cultivos"]

            if index >= len(inventario):
                messagebox.showerror("Error", "El cultivo seleccionado no existe.")
                logger.error(f"Index de cultivo fuera de rango para {email_campesino}")
                return

            cultivo = inventario[index]
            cantidad = simpledialog.askinteger(
                "Comprar cultivo",
                f"¿Cuántas unidades deseas comprar?\nDisponibles: {cultivo['cantidad']}",
                minvalue=1
            )
            if cantidad is None:
                return

            pedido = pedidos.crear_pedido(self.user, email_campesino, cultivo["nombre"], cantidad)
            total = pedido["precio_total"]
            ruta = generarFacturaTxt(self.user, campesino, cultivo, cantidad, total)

            messagebox.showinfo(
                "Compra realizada",
                f"Has comprado {cantidad} unidades por ${total:,}.\nFactura generada en:\n{ruta}\n"
                f"Pedido registrado con ID: {pedido['id_pedido']}"
            )
        except ServicioError as e:
            logger.warning(f"Compra rechazada: {e.mensaje}")
            messagebox.showerror("No se pudo comprar", e.mensaje)
        except Exception as e:
            logger.error(f"Error en el proceso de compra: {e}")
            messagebox.showerror("Error", f"Ocurrió un error: {e}")
