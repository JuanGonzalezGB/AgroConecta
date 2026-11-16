import tkinter as tk
from vistas.interfaceViewPerfiles import InterfaceViewsPerfiles

class AdminView(InterfaceViewsPerfiles):
    def __init__(self, root, user, usuario_objetivo, estilo, notificationService):
        self.notificationService = notificationService
        self.estilo = estilo
        self.root = root
        self.root.geometry("")
        self.usuario_objetivo=usuario_objetivo
        self.user = user
        self.tipo = 'Admin'

        self.frame = tk.Frame(root, bg=self.estilo.colorFondo(), padx=10, pady=10)
        self.frame.pack(fill='both', expand=True)

        tk.Label(
            self.frame,
            text=f' 👨‍💼 Admin: {user.get("nombre","-")}',
            bg=self.estilo.colorFondo(),
            fg=self.estilo.colorTitulo(),
            font=('Arial',14,'bold')
        ).pack(pady=6)
        tk.Button(
            self.frame, text='⚙️ Gestionar Roles',
            bg=self.estilo.colorLetra(),
            fg=self.estilo.colorFondo(),
            command=self.openGestionRoles
        ).pack(pady=8)

        tk.Button(
            self.frame, text='📋 Asignar Roles a Usuarios',
            bg=self.estilo.colorLetra(),
            fg=self.estilo.colorFondo(),
            command=self.openAsignarRoles
        ).pack(pady=8)

        tk.Button(
        self.frame, text="🔐 Gestionar Permisos",
        bg=self.estilo.colorLetra(),
        fg=self.estilo.colorFondo(),
        command=self.openGestionPermisos
        ).pack(pady=8)
        tk.Button(self.frame, text='Cerrar sesión',bg=estilo.colorLetra(),fg=estilo.colorFondo(), command=self.cerrarSesion).pack(pady=8)
      
        tk.Button(
            self.frame, text='👥', bg=estilo.colorLetra(),
            fg=estilo.colorFondo(), command=self.openPerfil
        ).pack(anchor='w', pady=7)
        
        tk.Button(
            self.frame, text='🔔 Ver notificaciones',
            bg=self.estilo.colorLetra(),
            fg=self.estilo.colorFondo(),
            command=self.openNotificaciones
        ).pack(pady=10)

    def openGestionRoles(self):
        from controlador.controladorSubVistas import ControladorSubVistas
        controladorSubVistas = ControladorSubVistas(self.frame,self.root,self.user,self.usuario_objetivo,None,None,self.estilo,self.notificationService)
        controladorSubVistas.open_roles_view()

    def openAsignarRoles(self):
        from controlador.controladorSubVistas import ControladorSubVistas
        controladorSubVistas = ControladorSubVistas(self.frame,self.root,self.user,self.usuario_objetivo,None,None,self.estilo,self.notificationService)
        controladorSubVistas.open_asignar_roles_view()

    def openGestionPermisos(self):
        from controlador.controladorSubVistas import ControladorSubVistas
        controladorSubVistas = ControladorSubVistas(self.frame,self.root,self.user,self.usuario_objetivo,None,None,self.estilo,self.notificationService)
        controladorSubVistas.open_permisos_view()
