import tkinter as tk
from tkinter import simpledialog, messagebox
from vistas.subventanas.interfaceSubViews import InterfaceSubViews
from controlador.controladorAdmin import ControladorAdmin
import logging

logger = logging.getLogger(__name__)

class PermisosView(InterfaceSubViews):
    def __init__(self,user, root, estilo, notificationService):
        self.notificationService = notificationService
        self.user = user
        self.root = root
        self.estilo = estilo
        self.titulo = "Gestión de Permisos"
        self.win = tk.Toplevel(root)
        self.win.title(self.titulo)
        self.win.geometry("380x380")
        self.win.config(bg=self.estilo.colorFondo())
        self.win.grab_set()

        tk.Label(
            self.win, text="🔐 Permisos disponibles",
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorLetra(),
            font=("Arial", 13, "bold")
        ).pack(pady=10)

        self.listbox = tk.Listbox(
            self.win, width=45,
            fg=self.estilo.colorFondo(),
            bg=self.estilo.colorLetra(),
            font=("Arial", 11)
        )
        self.listbox.pack(pady=6)

        btn_frame = tk.Frame(self.win, bg=self.estilo.colorFondo())
        btn_frame.pack(pady=12)

        tk.Button(btn_frame, text="➕ Nuevo",
                  bg=self.estilo.colorLetra(),
                  fg=self.estilo.colorFondo(),
                  command=self.nuevo).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="✏️ Editar",
                  bg=self.estilo.colorLetra(),
                  fg=self.estilo.colorFondo(),
                  command=self.editar).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="🗑 Eliminar",
                  bg=self.estilo.colorLetra(),
                  fg=self.estilo.colorFondo(),
                  command=self.eliminar).grid(row=0, column=2, padx=5)

        tk.Button(self.win, text='Cerrar',
                  fg=self.estilo.colorFondo(),
                  bg=self.estilo.colorLetra(),
                  command=self.botonCerrar).pack(pady=6)
        

        # Solo un controlador por vista
        self.controlador = ControladorAdmin(self.user,self.root, self.notificationService)
        self.recargar_listbox() 
        self.bloquearRoot()   
        
    def recargar_listbox(self):
        self.listbox.delete(0, tk.END)
        self.permisos = self.controlador.obtener_lista_permisos(user=self.user)

        def es_permiso_admin(pid):
            # Devuelve True si el permiso pertenece originalmente al rol admin
            return self.controlador.permiso_original_del_rol("admin", pid)

        # Filtrar y mostrar solo permisos que NO sean de admin
        self.permisos_mostrables = [p for p in self.permisos if not es_permiso_admin(p["id"])]

        for p in self.permisos_mostrables:
            self.listbox.insert(tk.END, f"{p['id']}  |  {p['nombre']}")
    
    def nuevo(self):
        id_perm = simpledialog.askstring("Nombre visible", "Nombre:")
        if not id_perm:
            return

        nombre = simpledialog.askstring("Nuevo permiso", "ID del permiso:")
        if not nombre:
            nombre = id_perm

        # Elegir rol
        roles = self.controlador.obtener_roles(user=self.user)

        # Enumeramos los roles
        rol_lista = [f"{i+1}. {r['nombre']} (ID: {r['id']})" for i, r in enumerate(roles)]
        rol_texto = "\n".join(rol_lista)

        # Pedimos un número en lugar del ID completo
        seleccion = simpledialog.askinteger("Asignar permiso", f"Seleccione un rol:\n{rol_texto}", minvalue=1, maxvalue=len(roles))
        if not seleccion:
            return

        # Obtenemos el rol correspondiente
        rol_id = roles[seleccion - 1]['id']


        # Controlador deduce automáticamente categoría y agrega
        exito, msg = self.controlador.agregar_permiso_a_rol(id_perm, nombre, rol_id, user=self.user)
        messagebox.showinfo("Resultado", msg)
        self.recargar_listbox()


    def editar(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Atención", "Selecciona un permiso")
            return
        idx = self.listbox.curselection()[0]
        permiso = self.permisos_mostrables[idx]

        from controlador.controladorSubVistas import ControladorSubVistas
        controlaSubVistas = ControladorSubVistas(None,self.root,self.user,None,None,None,self.estilo,self.notificationService)
        controlaSubVistas.open_editar_permiso_view(permiso,callback_recargar=self.recargar_listbox)

        '''from vistas.subventanas.ventana_editar_permiso_view import VentanaEditarPermiso
        VentanaEditarPermiso(self.root,self.user,permiso,self.estilo,self.notificationService,callback_recargar=self.recargar_listbox)
'''

    def eliminar(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Atención", "Selecciona un permiso")
            return
        permiso = self.permisos_mostrables[idx[0]]
        if messagebox.askyesno("Confirmar", f"¿Eliminar permiso {permiso['id']}?"):
            exito, msg = self.controlador.eliminar_permiso_global(permiso["id"], user=self.user)
            
            # Mostrar el mensaje al usuario
            if exito:
                messagebox.showinfo("Resultado", msg)
            else:
                messagebox.showwarning("Atención", msg)
            
            # Log
            import logging
            logger = logging.getLogger(__name__)
            if exito:
                logger.info(f"{self.user.get('email')} eliminó el permiso '{permiso['id']}' correctamente")
            else:
                logger.warning(f"{self.user.get('email')} intentó eliminar permiso protegido '{permiso['id']}'")

            # Recargar la lista
            self.recargar_listbox()

