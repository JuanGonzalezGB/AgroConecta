import tkinter as tk
from tkinter import simpledialog, messagebox
from controlador.controladorAdmin import ControladorAdmin
from vistas.subventanas.interfaceSubViews import InterfaceSubViews
from auth.permisos import require_permission

class RolesView(InterfaceSubViews):
    def __init__(self, root, estilo, user, notificationService):
        self.notificationService = notificationService
        self.user = user
        self.root = root
        self.estilo = estilo
        self.controlador = ControladorAdmin(self.user, self.root, self.notificationService)

        self.win = tk.Toplevel(root)
        self.win.title("Gestión de Roles")
        self.win.geometry("350x350")
        self.win.config(bg=self.estilo.colorFondo())
        self.win.grab_set()

        tk.Label(self.win, text="📌 Roles disponibles",
                 bg=self.estilo.colorFondo(),
                 fg=self.estilo.colorLetra(),
                 font=("Arial", 13, "bold")).pack(pady=8)

        self.listbox = tk.Listbox(self.win, width=40,
                                  fg=self.estilo.colorFondo(),
                                  bg=self.estilo.colorLetra(),
                                  font=("Arial", 11))
        self.listbox.pack(pady=8)

        btn_frame = tk.Frame(self.win, bg=self.estilo.colorFondo())
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="➕ Nuevo",
                  command=lambda: self.nuevo_rol(user=self.user),bg=self.estilo.colorLetra(),fg=self.estilo.colorFondo()).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="✏️ Editar",
                  command=lambda: self.editar_rol(user=self.user),bg=self.estilo.colorLetra(),fg=self.estilo.colorFondo()).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="🗑 Eliminar",
                  command=lambda: self.eliminar_rol(user=self.user),bg=self.estilo.colorLetra(),fg=self.estilo.colorFondo()).grid(row=0, column=2, padx=5)

        tk.Button(self.win, text="Cerrar", command=self.win.destroy,bg=self.estilo.colorLetra(),fg=self.estilo.colorFondo()).pack(pady=6)
        

        self.recargar_listbox()

    def recargar_listbox(self):
        self.listbox.delete(0, tk.END)

        self.roles_mostrados = self.controlador.obtener_lista_roles(user=self.user)

        for r in self.roles_mostrados:
            self.listbox.insert(tk.END, f"{r['id']}  |  {r['nombre']}")
        return self.listbox
        

        '''

    def recargar_listbox(self):
            self.listbox.delete(0, tk.END)
            self.roles = self.controlador.obtener_roles(user=self.user)
            self.roles_mostrados = [r for r in self.roles if r["id"].lower() != "admin"]
            for r in self.roles_mostrados:
                self.listbox.insert(tk.END, f"{r['id']}  |  {r['nombre']}")    '''

    @require_permission("gestionar_roles")
    def nuevo_rol(self, *, user):
        id_rol = simpledialog.askstring("Nuevo rol", "ID del rol:")
        if not id_rol:
            return
        nombre = simpledialog.askstring("Nuevo rol", "Nombre visible:")
        if not nombre:
            messagebox.showwarning("Atención", "El rol debe tener un nombre")
            return

        # ------------------------- LLAMADA A CONTROLADOR -------------------------
        exito, msg = self.controlador.agregar_nuevo_rol(id_rol, nombre, user=self.user)
        # -----------------------------------------------------------------------

        messagebox.showinfo("Resultado", msg)
        self.win.destroy()

    @require_permission("gestionar_roles")
    def editar_rol(self, *, user):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Atención", "Selecciona un rol")
            return
        rol = self.roles_mostrados[idx[0]]  # usar lista filtrada
        from controlador.controladorSubVistas import ControladorSubVistas
        self.controlaSubVistas = ControladorSubVistas(None,self.root,self.user,None,None,rol,self.estilo,self.notificationService)
        self.controlaSubVistas.open_editar_rol_view(callback_recargar=self.recargar_listbox)

    @require_permission("gestionar_roles")
    def eliminar_rol(self, *, user):
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un rol")
            return
        rol = self.roles_mostrados[seleccion[0]]  # usar lista filtrada

        if rol["id"].lower() == "admin":
            messagebox.showwarning("Atención", "No se puede eliminar el rol administrador")
            return

        # ------------------------- LLAMADA A CONTROLADOR -------------------------
        if messagebox.askyesno("Confirmar", f"¿Eliminar rol {rol['id']}?"):
            exito, msg = self.controlador.eliminar_rol_por_id(rol["id"], user=self.user)
            messagebox.showinfo("Resultado", msg)
            self.recargar_listbox()
        # -----------------------------------------------------------------------