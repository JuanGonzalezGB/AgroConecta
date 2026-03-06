import tkinter as tk
from notificaciones.iniciar_notis import IniciarNotis
from controlador.controladorLogin import ControladorLogin
from controlador.controladorVistas import ControladorVistas
import logging

logger = logging.getLogger(__name__)

class MainView:
    def __init__(self, root, estilo,notification_service):
        self.estilo = estilo
        self.root = root   
        self.notificationService = notification_service
        if self.notificationService is None:
            self.notificationService=IniciarNotis(self.root,None)
        self.root.geometry("")
        self.frame = tk.Frame(self.root, bg=estilo.colorFondo(), padx=20, pady=20)
        self.frame.pack(fill='both', expand=True)
        self.user = None
        tk.Label(
            self.frame,
            text='AgroConecta',
            bg=estilo.colorFondo(),
            fg=estilo.colorTitulo(),
            font=('Arial', 18, 'bold')
        ).pack(anchor='n', pady=8)

        tk.Label(
            self.frame,
            text='Iniciar sesión',
            bg=estilo.colorFondo(),
            fg=estilo.colorTitulo(),
            font=('Arial', 12)
        ).pack(pady=6)

        tk.Label(
            self.frame,
            text='Email:',
            bg=estilo.colorFondo(),
            fg=estilo.colorTitulo()
        ).pack(anchor='w')

        self.email_entry = tk.Entry(
            self.frame,
            fg=estilo.colorFondo(),
            bg=estilo.colorLetra(),
            width=40
        )
        self.email_entry.pack(anchor='w', pady=1, fill='x')

        tk.Label(
            self.frame,
            text='Contraseña:',
            bg=estilo.colorFondo(),
            fg=estilo.colorTitulo()
        ).pack(anchor='w')

        self.pwd_entry = tk.Entry(
            self.frame,
            fg=estilo.colorFondo(),
            bg=estilo.colorLetra(),
            show='*',
            width=40
        )
        self.pwd_entry.pack(anchor='w', pady=(1,7), fill='x')

        self.email_entry.bind('<Return>', lambda e: self.submit())
        self.pwd_entry.bind('<Return>',  lambda e: self.submit())
        self.controladorVistas = ControladorVistas(self.frame, self.root, self.user,None, self.estilo,self.notificationService)

        tk.Button(
            self.frame,
            text='Iniciar sesión',
            bg=estilo.colorFondoH(),
            fg=estilo.colorLetraH(),
            command=self.submit,
            pady=20 
        ).pack(fill='x', pady=7)



        tk.Button(
            self.frame,
            text='Registrarse',
            bg=estilo.colorLetra(),
            fg=estilo.colorFondo(),
            command=self.controladorVistas.open_register
        ).pack(fill='x', pady=7)

        tk.Button(
            self.frame,
            text='Salir',
            bg=estilo.colorLetra(),
            fg=estilo.colorFondo(),
            command=self.exitButton
        ).pack(fill='x', pady=7)

        tk.Button(
            self.frame,
            text='🎨',
            bg=estilo.colorLetra(),
            fg=estilo.colorFondo(),
            command=self.controladorVistas.open_temas
        ).pack(anchor='sw', pady=7)


    def exitButton(self):
        logger.info('Programa cerrado por usuario')
        self.root.quit()

    def submit(self):
        email = self.email_entry.get().strip()
        pwd = self.pwd_entry.get().strip()
        user = [email, pwd]
        self.controlador = ControladorLogin(self.frame, self.root, user, self.estilo,self.notificationService)

        if hasattr(self.controlador, "set_notification_service") and self.notificationService:
            self.controlador.set_notification_service(self.notificationService)

        self.controlador.login(user)
