import tkinter as tk
from tkinter import messagebox
from modelo.rolesModel import cargar_permisos, actualizar_rol
from vistas.subventanas.interfaceSubViews import InterfaceSubViews
import logging

logger = logging.getLogger(__name__)

class VentanaSeleccionPermisosRol(InterfaceSubViews):
    def __init__(self, root, rol, estilo):
        self.root = root
        self.rol = rol  # diccionario del rol a editar
        self.estilo = estilo

        self.win = tk.Toplevel(root)
        self.titulo =f"Editar permisos rol: {rol['nombre']}"
        self.win.title(self.titulo)
        self.win.geometry("420x450")
        self.win.config(bg=self.estilo.colorFondo())
        self.win.grab_set()

        tk.Label(
            self.win, text=f"Permisos de: {rol['nombre']}",
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorLetra(),
            font=("Arial", 13, "bold")
        ).pack(pady=8)

        self.frame_checks = tk.Frame(self.win, bg=self.estilo.colorFondo())
        self.frame_checks.pack(pady=5)

        
        self.permisos = cargar_permisos()

        # Diccionario id_permiso → BooleanVar
        self.checkbox_vars = {}

        for p in self.permisos:
            var = tk.BooleanVar()
            var.set(p["id"] in rol.get("permisos", []))  # marcar existentes

            self.checkbox_vars[p["id"]] = var

            tk.Checkbutton(
                self.frame_checks,
                text=f"{p['id']}  |  {p['nombre']}",
                variable=var,
                bg=self.estilo.colorFondo(),
                fg=self.estilo.colorLetra(),
                selectcolor=self.estilo.colorFondoH(),
                anchor="w"
            ).pack(fill="x")

        tk.Button(
            self.win, text="💾 Guardar cambios",
            bg=self.estilo.colorLetra(),
            fg=self.estilo.colorFondo(),
            command=self.guardar
        ).pack(pady=12)
        tk.Button(self.win, text='Cerrar',fg=self.estilo.colorFondo(),bg=self.estilo.colorLetra(), command=self.botonCerrar).pack(pady=6)



    def guardar(self):
        permisos_seleccionados = [
            pid for pid, v in self.checkbox_vars.items() if v.get()
        ]

        self.rol["permisos"] = permisos_seleccionados
        actualizar_rol(self.rol["id"], self.rol)

        logger.info(f"Permisos actualizados en rol {self.rol['id']}: {permisos_seleccionados}")
        messagebox.showinfo("OK", "Permisos guardados exitosamente")
        self.win.destroy()
