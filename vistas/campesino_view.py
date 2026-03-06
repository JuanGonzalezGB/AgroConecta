import tkinter as tk
from vistas.interfaceViewPerfiles import InterfaceViewsPerfiles

class CampesinoView(InterfaceViewsPerfiles):
    def __init__(self, root, user, estilo, notificationService):

        self.notificationService = notificationService
        self.estilo = estilo
        self.root = root
        self.root.geometry("")
        self.user = user
        self.tipo = 'Campesino'  
        from controlador.controladorVistas import ControladorVistas
        self.controlaVistas = ControladorVistas(
            None, self.root, self.user, None, self.estilo, self.notificationService
        )        
        self.frame = tk.Frame(root, bg=self.estilo.colorFondo(), padx=10, pady=10)
        self.frame.pack(fill='both', expand=True)

        tk.Label(
            self.frame,
            text=f' 👨‍🌾 Campesino: {user.get("nombre","-")}',
            bg=estilo.colorFondo(),
            fg=estilo.colorTitulo(),
            font=('Arial',14,'bold')
        ).pack(pady=6)

        tk.Button(
            self.frame, text='Cultivos', bg=estilo.colorLetra(),
            fg=estilo.colorFondo(), command=self.openCultivos
        ).pack(fill='x', pady=4)

        tk.Button(
            self.frame, text='Ganancias', bg=estilo.colorLetra(),
            fg=estilo.colorFondo(), command=self.openGanancias
        ).pack(fill='x', pady=4)

        tk.Button(
            self.frame, text='Cerrar sesión', bg=estilo.colorLetra(),
            fg=estilo.colorFondo(), command=self.cerrarSesion
        ).pack(pady=8)

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

    def openCultivos(self):
        from controlador.controladorSubVistas import ControladorSubVistas        
        self.controlador = ControladorSubVistas(
            self.frame,
            self.root,
            self.user,
            None,
            None,
            None,
            self.estilo,
            self.notificationService  
        )
        self.controlador.open_cultivos_view()


