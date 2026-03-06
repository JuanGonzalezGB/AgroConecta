from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from controlador.controladorLogin import ControladorLogin
from controlador.controladorVistas import ControladorVistas
from notificaciones.iniciar_notis import IniciarNotis
import logging

logger = logging.getLogger(__name__)

class MainView(BoxLayout):
    def __init__(self, estilo, notification_service=None, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self.estilo = estilo
        self.notificationService = notification_service
        if self.notificationService is None:
            self.notificationService = IniciarNotis(None, None)
        
        self.user = None

        # Etiquetas principales
        self.add_widget(Label(text='AgroConecta', font_size=24, bold=True,
                              color=estilo.colorTitulo()))
        self.add_widget(Label(text='Iniciar sesión', font_size=18,
                              color=estilo.colorTitulo()))

        # Email
        self.add_widget(Label(text='Email:', color=estilo.colorTitulo()))
        self.email_entry = TextInput(multiline=False, size_hint_y=None, height=30,
                                     background_color=estilo.colorLetra(),
                                     foreground_color=estilo.colorFondo())
        self.email_entry.bind(on_text_validate=lambda instance: self.submit())
        self.add_widget(self.email_entry)

        # Contraseña
        self.add_widget(Label(text='Contraseña:', color=estilo.colorTitulo()))
        self.pwd_entry = TextInput(password=True, multiline=False, size_hint_y=None, height=30,
                                   background_color=estilo.colorLetra(),
                                   foreground_color=estilo.colorFondo())
        self.pwd_entry.bind(on_text_validate=lambda instance: self.submit())
        self.add_widget(self.pwd_entry)

        # Inicializar ControladorVistas
        self.controladorVistas = ControladorVistas(
            frame=self,           # <-- usar este BoxLayout como contenedor
            root=None,            # puedes dejar None si no lo usas
            user=self.user,
            usuario_objetivo=None,
            estilo=self.estilo,
            notificationService=self.notificationService
)

        # Botones
        self.login_btn = Button(text='Iniciar sesión', size_hint_y=None, height=50,
                                background_color=estilo.colorFondoH(), color=estilo.colorLetraH())
        self.login_btn.bind(on_release=lambda x: self.submit())
        self.add_widget(self.login_btn)

        self.register_btn = Button(text='Registrarse', size_hint_y=None, height=50,
                                   background_color=estilo.colorLetra(), color=estilo.colorFondo())
        self.register_btn.bind(on_release=lambda x: self.controladorVistas.open_register())
        self.add_widget(self.register_btn)

        self.exit_btn = Button(text='Salir', size_hint_y=None, height=50,
                               background_color=estilo.colorLetra(), color=estilo.colorFondo())
        self.exit_btn.bind(on_release=lambda x: self.exitButton())
        self.add_widget(self.exit_btn)

        self.theme_btn = Button(text='🎨', size_hint=(None, None), size=(50, 50),
                                background_color=estilo.colorLetra(), color=estilo.colorFondo())
        self.theme_btn.bind(on_release=lambda x: self.controladorVistas.open_temas())
        self.add_widget(self.theme_btn)

    def exitButton(self):
        logger.info('Programa cerrado por usuario')
        App.get_running_app().stop()

    def submit(self):
        email = self.email_entry.text.strip()
        pwd = self.pwd_entry.text.strip()
        user = [email, pwd]
        self.controlador = ControladorLogin(None, None, user, self.estilo, self.notificationService)
        if hasattr(self.controlador, "set_notification_service") and self.notificationService:
            self.controlador.set_notification_service(self.notificationService)
        self.controlador.login(user)
