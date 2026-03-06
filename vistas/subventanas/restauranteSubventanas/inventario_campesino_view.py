import tkinter as tk
from tkinter import messagebox
import logging
from controlador.controladorCompras import ControladorCompras
from vistas.subventanas.interfaceSubViews import InterfaceSubViews
from modelo.CRU import obtener_usuario_por_email, obtenerCultivosUsuario

logger = logging.getLogger(__name__)

class InventarioCampesinoView(InterfaceSubViews):
    def __init__(self, root, user, campesino, estilo, notificationService):
        self.notificationService = notificationService
        self.user = user
        self.root = root
        self.estilo = estilo
        self.win = tk.Toplevel(root)

        # Obtener datos completos del campesino
        usuario_completo = obtener_usuario_por_email(campesino.get('email', ''))
        if usuario_completo:
            self.campesino = {
                "email": campesino["email"],
                "nombre": usuario_completo.get("nombre", campesino["email"]),
                "cultivos": obtenerCultivosUsuario(campesino)
            }
        else:
            # En caso de no encontrar usuario, usamos email como nombre y cultivamos vacíos
            self.campesino = {
                "email": campesino.get("email", ""),
                "nombre": campesino.get("email", ""),
                "cultivos": []
            }
        self.titulo = f"Inventario de {self.campesino['nombre']}"
        self.win.title(self.titulo)
        self.win.geometry('400x350')
        self.win.config(bg=self.estilo.colorFondo())

        tk.Label(
            self.win,
            text=f"🌾 Cultivos de {self.campesino['nombre']}",
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorLetra(),
            font=('Arial', 14, 'bold')
        ).pack(pady=8)

        self.listbox = tk.Listbox(
            self.win,
            width=50,
            fg=self.estilo.colorFondo(),
            bg=self.estilo.colorLetra(),
        )
        self.listbox.pack(pady=6, expand=True)

        cultivos = self.campesino.get("cultivos", [])
        if not cultivos:
            self.listbox.insert(tk.END, "No hay cultivos disponibles.")
        else:
            for c in cultivos:
                texto = f"{c['nombre'].capitalize()} | Cantidad: {c['cantidad']} | Precio: {c['precio']}"
                self.listbox.insert(tk.END, texto)

        tk.Button(
            self.win,
            text="Comprar cultivo seleccionado 🛒",
            fg=self.estilo.colorFondo(),
            bg=self.estilo.colorLetra(),
            command=self.comprarCultivo
        ).pack(pady=6)

        tk.Button(
            self.win,
            text="Cerrar",
            fg=self.estilo.colorFondo(),
            bg=self.estilo.colorLetra(),
            command=self.win.destroy
        ).pack(pady=6)

        self.bloquearRoot()

    def comprarCultivo(self):
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un cultivo para comprar.")
            return
        index = seleccion[0]
        controlador = ControladorCompras(self.user, self.root, self.notificationService)
        controlador.comprar_cultivo(self.campesino, index, user=self.user)
        self.win.destroy()
