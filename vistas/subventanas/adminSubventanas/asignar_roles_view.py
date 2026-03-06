import tkinter as tk
from tkinter import messagebox

from modelo.CRU import cargarUsuarios
from vistas.subventanas.interfaceSubViews import InterfaceSubViews
import logging
logger = logging.getLogger(__name__)

class AsignarRolesView(InterfaceSubViews):
    def __init__(self, root,user,usuario_objetivo, notificationService, estilo):
        self.root=root
        self.user = user
        self.usuario_objetivo=usuario_objetivo
        self.notificationService = notificationService
        self.estilo = estilo
        self.win = tk.Toplevel(self.root)
        self.titulo = "Asignar Roles a Usuarios"
        self.win.title(self.titulo)
        self.win.geometry("420x350")
        self.win.config(bg=self.estilo.colorFondo())
        self.win.grab_set()

        tk.Label(self.win, text="👤 Seleccionar usuario",
                 bg=self.estilo.colorFondo(),
                 fg=self.estilo.colorLetra(),
                 font=("Arial", 13, "bold")).pack(pady=6)

        self.lista_usuarios = cargarUsuarios()
        self.usuarios = [u for lista in self.lista_usuarios.values() for u in lista]

        self.listbox = tk.Listbox(self.win, width=50,
                                  fg=self.estilo.colorFondo(),
                                  bg=self.estilo.colorLetra())
        self.listbox.pack(pady=6)
        for u in self.usuarios:
            self.listbox.insert(tk.END, f"{u['nombre']} | {u['email']}")

        tk.Button(self.win, text="Asignar roles",
                  bg=self.estilo.colorLetra(),
                  fg=self.estilo.colorFondo(),
                  command=self.abrirSeleccionRoles).pack(pady=8)
        tk.Button(self.win, text='Cerrar',fg=self.estilo.colorFondo(),bg=self.estilo.colorLetra(), command=self.botonCerrar).pack(pady=6)
        

    def abrirSeleccionRoles(self):
        from controlador.controladorSubVistas import ControladorSubVistas
        seleccion = self.listbox.curselection()

        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un usuario")
            return

        # usuario seleccionado
        self.usuario_objetivo = self.usuarios[seleccion[0]]

        # Pasar usuario_objetivo al controlador
        controlador = ControladorSubVistas(
            None,                 # ?? depende de diseño
            self.win,             # root actual
            self.user,            # usuario que está logueado, el admin
            self.usuario_objetivo,# usuario seleccionado al que asignaremos roles
            None,
            None,
            self.estilo,
            self.notificationService
        )
        self.win.withdraw()
        controlador.open_ventana_seleccion_roles_view()

        

