import tkinter as tk
from tkinter import messagebox
from vistas.subventanas.interfaceSubViews import InterfaceSubViews
from controlador.controladorAdmin import ControladorAdmin

class VentanaEditarPermiso(InterfaceSubViews):
    def __init__(self, root, user, permiso, estilo, notificationService, callback_recargar):
        self.root = root
        self.permiso = permiso
        self.user = user
        self.estilo = estilo
        self.callback_recargar = callback_recargar
        self.notificationService = notificationService

        self.win = tk.Toplevel(root)
        self.titulo = f"Editar permiso {permiso['id']}"
        self.win.title(self.titulo)
        self.win.geometry("")
        self.win.config(bg=self.estilo.colorFondo())
        self.win.grab_set()

        self.controlador = ControladorAdmin(self.user, self.root, self.notificationService)

        # Título
        tk.Label(
            self.win, text=f"Editar permiso '{permiso['id']}'",
            font=("Arial", 12, "bold"),
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorLetra()
        ).pack(pady=8)

        # Entrada para nombre
        tk.Label(self.win, text="Nombre visible:", 
                 bg=self.estilo.colorFondo(),
                 fg=self.estilo.colorLetra()).pack(pady=4)
        self.entry_nombre = tk.Entry(self.win,readonlybackground=self.estilo.colorLetra(), bg=self.estilo.colorLetra(),fg=self.estilo.colorFondo(),width=30)
        self.entry_nombre.pack(pady=4)
        self.entry_nombre.insert(0, permiso.get("nombre", permiso["id"]))

        # Bloquear edición si es un permiso protegido
        if self.controlador.es_permiso_protegido(permiso["id"]):
            self.entry_nombre.config(state="readonly")
            tk.Label(self.win, text="⚠ Permiso protegido, no puede cambiar el nombre",
                     bg=self.estilo.colorFondo(),
                     fg=self.estilo.colorLetraH()).pack(pady=2)

        # Listbox para roles
        tk.Label(self.win, text="Asignar a roles:",
                 bg=self.estilo.colorFondo(),
                 fg=self.estilo.colorLetra()).pack(pady=8)
        self.listbox_roles = tk.Listbox(self.win, selectmode=tk.MULTIPLE, width=30,
                                        bg=self.estilo.colorLetra(), fg=self.estilo.colorFondo())
        self.listbox_roles.pack(pady=4, padx=10, fill=tk.BOTH, expand=True)

        roles = self.controlador.obtener_roles(user=self.user)
        # Filtrar admin
        roles = [r for r in roles if r["id"] != "admin"]
        self.roles_ids = [r["id"] for r in roles]

        # Preseleccionar roles actuales del permiso
        roles_actuales = [r["id"] for r in self.controlador.roles_del_permiso(permiso["id"], user=self.user)
                          if r["id"] != "admin"]

        for r_id in self.roles_ids:
            # Determinar si el permiso está protegido en este rol
            protegido = self.controlador.permiso_original_del_rol(r_id, permiso["id"])

            display = r_id
            if protegido and self.controlador.es_rol_protegido(r_id):
                display += "  [PROTEGIDO]"

            self.listbox_roles.insert(tk.END, display)

            idx = self.listbox_roles.size() - 1

            # Preseleccionar si ya lo tiene asignado
            if r_id in roles_actuales:
                self.listbox_roles.selection_set(idx)

            # Colorear si es protegido
            if protegido and self.controlador.es_rol_protegido(r_id):
                self.listbox_roles.itemconfig(idx,
                                              bg=self.estilo.colorFondoH(),
                                              fg=self.estilo.colorLetraH())


        # Botón guardar
        tk.Button(self.win, text="Guardar",
                  bg=self.estilo.colorLetra(),
                  fg=self.estilo.colorFondo(),
                  command=self.guardar).pack(pady=10)

        # Botón cerrar
        tk.Button(self.win, text='Cerrar',
                  fg=self.estilo.colorFondo(),
                  bg=self.estilo.colorLetra(),
                  command=self.botonCerrar).pack(pady=6)

    def guardar(self):
        nuevo_nombre = self.entry_nombre.get().strip()

        # Validaciones
        if not nuevo_nombre:
            messagebox.showwarning("Atención", "El permiso debe tener un nombre.")
            return

        seleccion = [self.roles_ids[i] for i in self.listbox_roles.curselection()]
        if not seleccion:
            messagebox.showwarning("Atención", "Debes seleccionar al menos un rol.")
            return

        # Llamada al controlador
        exito, msg = self.controlador.editar_permiso(
            self.permiso["id"],
            nuevo_nombre,
            seleccion,
            user=self.user
        )

        messagebox.showinfo("Resultado", msg)
        self.win.destroy()
        if self.callback_recargar:
            self.callback_recargar()

