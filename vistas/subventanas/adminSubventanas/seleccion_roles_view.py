import tkinter as tk
from tkinter import messagebox
from modelo.rolesModel import cargar_roles
from modelo.CRU import asignar_rol_a_usuario, quitar_rol_a_usuario
from vistas.subventanas.interfaceSubViews import InterfaceSubViews

class VentanaSeleccionRoles(InterfaceSubViews):
    def __init__(self, root, usuario, estilo, actor):
        self.root = root
        self.objetivo = usuario
        self.user = actor
        self.estilo = estilo
        self.win = tk.Toplevel(root)
        nombre_usuario = self.objetivo.get("nombre", self.objetivo.get("email", "Usuario"))
        self.titulo = f"Asignar roles a {nombre_usuario}"
        self.win.title(self.titulo)
        self.win.geometry("350x350")
        self.win.config(bg=self.estilo.colorFondo())
        self.win.grab_set()

        tk.Label(self.win, text="Seleccionar roles",
                 bg=self.estilo.colorFondo(),
                 fg=self.estilo.colorLetra(),
                 font=("Arial", 12, "bold")).pack(pady=8)

        # Cargar roles y roles actuales del usuario
        self.roles = cargar_roles()
        self.roles_actuales = set(self.objetivo.get('roles', []))

        self.listbox = tk.Listbox(self.win, selectmode=tk.MULTIPLE,
                                  bg=self.estilo.colorLetra(),
                                  fg=self.estilo.colorFondo(), width=40)
        self.listbox.pack(pady=6)

        for idx, r in enumerate(self.roles):
            self.listbox.insert(tk.END, f"{r['id']} | {r['nombre']}")
            if r['id'] in self.roles_actuales:
                self.listbox.selection_set(idx)  # Preseleccionar roles existentes

        tk.Button(self.win, text="Guardar",
                  bg=self.estilo.colorLetra(),
                  fg=self.estilo.colorFondo(),
                  command=self.guardar).pack(pady=10)
        tk.Button(self.win, text='Cerrar',
                  fg=self.estilo.colorFondo(),
                  bg=self.estilo.colorLetra(),
                  command=self.botonCerrar).pack(pady=6)

    def guardar(self):
        seleccion = {self.roles[i]["id"] for i in self.listbox.curselection()}

        # Roles a agregar y quitar
        roles_a_agregar = seleccion - self.roles_actuales
        roles_a_quitar = self.roles_actuales - seleccion


        resultados = []

        # Asignar roles nuevos
        if roles_a_agregar:
            ok, msg = asignar_rol_a_usuario(
                self.objetivo["email"],
                list(roles_a_agregar),
                user=self.user
            )
            resultados.append(msg)

        # Quitar roles existentes (excepto admin)
        if roles_a_quitar:
            ok, msg = quitar_rol_a_usuario(
                self.objetivo["email"],
                list(roles_a_quitar),
                user=self.user
            )
            resultados.append(msg)

        if resultados:
            messagebox.showinfo("Resultado", "\n".join(resultados))
        else:
            messagebox.showinfo("Resultado", "No se realizaron cambios.")
        self.win.destroy()
