import tkinter as tk
from tkinter import messagebox
from vistas.subventanas.interfaceSubViews import InterfaceSubViews
from controlador.controladorAdmin import ControladorAdmin

class VentanaEditarRol(InterfaceSubViews):
    def __init__(self, root, user, rol, estilo, notificationService, callback_recargar):
        self.root = root
        self.user = user
        self.rol = rol
        self.estilo = estilo
        self.notificationService = notificationService
        self.callback_recargar = callback_recargar
        self.controlador = ControladorAdmin(self.user,self.root,self.notificationService)
        
        self.win = tk.Toplevel(root)
        self.titulo=(f"Editar rol '{rol['id']}'")
        self.win.title(self.titulo)
        self.win.config(bg=self.estilo.colorFondo())
        self.win.grab_set()

        tk.Label(self.win, text=f"Editar rol '{rol['id']}'",
                 font=("Arial", 12, "bold"),
                 bg=self.estilo.colorFondo(),
                 fg=self.estilo.colorLetra()).pack(pady=10)

        tk.Label(self.win, text="Nombre del rol:",
                 bg=self.estilo.colorFondo(),
                 fg=self.estilo.colorLetra()).pack(pady=4)
        
        self.entry_nombre = tk.Entry(self.win, readonlybackground=self.estilo.colorLetra(),bg=self.estilo.colorLetra(),fg=self.estilo.colorFondo(), width=30)
        self.entry_nombre.pack(pady=4)
        self.entry_nombre.insert(0, rol.get("nombre", rol["id"]))

        if self.controlador.es_rol_protegido(rol["id"]):
            self.entry_nombre.config(state="readonly")
            tk.Label(self.win, text="⚠ Rol protegido, no puede cambiar el nombre",
                     bg=self.estilo.colorFondo(),
                     fg=self.estilo.colorLetraH()).pack(pady=2)

        tk.Label(self.win, text="Permisos asignados:",
                 bg=self.estilo.colorFondo(),
                 fg=self.estilo.colorLetra()).pack(pady=8)

        self.listbox_permisos = tk.Listbox(self.win, selectmode=tk.MULTIPLE, width=40,
                                           bg=self.estilo.colorLetra(), fg=self.estilo.colorFondo())
        self.listbox_permisos.pack(pady=6, padx=10, fill=tk.BOTH, expand=True)

        self.todos_permisos = self.controlador.obtener_lista_permisos(user=self.user)
        self.permisos_ids = [p["id"] for p in self.todos_permisos]
        permisos_actuales = self.controlador.obtener_ids_permisos_de_rol(self.rol["id"])

        def es_permiso_admin(pid):
            return self.controlador.permiso_original_del_rol("admin", pid)

        for permiso in self.todos_permisos:
            pid = permiso["id"]

            # NO mostrar permisos de admin
            if es_permiso_admin(pid):
                continue

            protegido = self.controlador.permiso_original_del_rol(self.rol["id"], pid)
            display = permiso.get("nombre", pid)

            if protegido and self.controlador.es_rol_protegido(self.rol["id"]):
                display += "  [PROTEGIDO]"

            self.listbox_permisos.insert(tk.END, display)

            if pid in permisos_actuales:
                self.listbox_permisos.selection_set(self.listbox_permisos.size() - 1)

            if protegido and self.controlador.es_rol_protegido(self.rol["id"]):
                self.listbox_permisos.itemconfig(self.listbox_permisos.size() - 1,
                                                 bg=self.estilo.colorFondoH(),
                                                 fg=self.estilo.colorLetraH())

        tk.Button(self.win, text="Guardar",
                  bg=self.estilo.colorLetra(),
                  fg=self.estilo.colorFondo(),
                  command=self.guardar).pack(pady=10)

        tk.Button(self.win, text='Cerrar',
                  fg=self.estilo.colorFondo(),
                  bg=self.estilo.colorLetra(),
                  command=self.botonCerrar).pack(pady=4)
    def guardar(self):
        seleccion = [self.permisos_ids[i] for i in self.listbox_permisos.curselection()]
        exito, msg = self.controlador.editar_rol(self.rol["id"], seleccion, user=self.user)

        if exito:
            messagebox.showinfo("Éxito", msg)
        else:
            messagebox.showwarning("Advertencia", msg)

        self.win.destroy()
        if self.callback_recargar:
            self.callback_recargar()
