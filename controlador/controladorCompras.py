from tkinter import messagebox, simpledialog
from modelo.CRU import guardarCultivos, cargarCultivos
from modelo.facturaModel import generarFacturaTxt
from auth.permisos import require_permission
from modelo.pedidos_utils import registrar_pedido

import logging

logger = logging.getLogger(__name__)

class ControladorCompras:
    def __init__(self, user, root, notificationService):
        self.user = user
        self.root= root
        self.notificationService=notificationService

    @require_permission("realizar_compra")
    def comprar_cultivo(self, campesino, index,*,user):
        try:
            cultivos_data = cargarCultivos()
            email_campesino = campesino["email"]
            cultivos_usuario = cultivos_data.get(email_campesino, [])

            if index >= len(cultivos_usuario):
                messagebox.showerror("Error", "El cultivo seleccionado no existe.")
                logger.error(f"Index de cultivo fuera de rango para {email_campesino}")
                return

            cultivo = cultivos_usuario[index]

            cantidad_disponible = cultivo.get("cantidad", 0)
            precio = cultivo.get("precio", 0)

            cantidad = simpledialog.askinteger(
                "Comprar cultivo",
                f"¿Cuántas unidades deseas comprar?\nDisponibles: {cantidad_disponible}",
                minvalue=1
            )
            if cantidad is None:
                return

            if cantidad > cantidad_disponible:
                messagebox.showerror("Stock insuficiente", "No hay suficientes unidades disponibles.")
                logger.warning(f"Intento de compra excediendo stock para {email_campesino}, index {index}")
                return

            cultivo["cantidad"] -= cantidad
            total = cantidad * precio

            # Guardar de nuevo en cultivos.json
            cultivos_usuario[index] = cultivo
            cultivos_data[email_campesino] = cultivos_usuario
            guardarCultivos(cultivos_data)

            ruta = generarFacturaTxt(self.user, campesino, cultivo, cantidad, total)

            # --- Notificaciones ---
            self.notificationService.notificar(
                campesino.get("nombre", email_campesino),
                "Compra confirmada",
                f"El restaurante {self.user.get('nombre','Restaurante')} confirmó la compra de {cantidad} unidades.",
                mostrar_inmediatamente=False
            )

            self.notificationService.notificar(
                self.user.get('nombre','Restaurante'),
                "Compra realizada",
                f"Compra realizada exitosamente al campesino {campesino.get('nombre', email_campesino)}.",
                mostrar_inmediatamente=False
            )

            messagebox.showinfo(
                "Compra realizada",
                f"Has comprado {cantidad} unidades por ${total:,}.\nFactura generada en:\n{ruta}"
            )

        except Exception as e:
            logger.error(f"Error en el proceso de compra: {e}")
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

        nuevo = registrar_pedido(
        restaurante=self.user,
        campesino=campesino,
        cultivo=cultivo,      # ← aquí estaba el error, estabas mandando solo el nombre
        cantidad=cantidad
        )
        messagebox.showinfo(
    "Pedido realizado",
    f"Pedido registrado con ID: {nuevo['id_pedido']}"
)
        
