# main_view.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.app import App
import logging

from estilo.baseScreen import BaseScreen
from controlador.controladorLogin import ControladorLogin
from controlador.controladorVistas import ControladorVistas
from notificaciones.iniciar_notis import IniciarNotis

logger = logging.getLogger(__name__)

class MainView(BaseScreen):
    NAME = "MainView"

    def __init__(self, estilo, notification_service=None, **kwargs):
        super().__init__(estilo, name=self.NAME, **kwargs)

        self.notificationService = notification_service
        if self.notificationService is None:
            self.notificationService = IniciarNotis(None, None)

        self.user = None
        self.controladorVistas = ControladorVistas(
            user=self.user,
            notificationService=self.notificationService
        )

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Labels
        layout.add_widget(Label(text='AgroConecta', font_size=24, bold=True, color=estilo.colorTitulo()))
        layout.add_widget(Label(text='Iniciar sesión', font_size=18, color=estilo.colorTitulo()))
        layout.add_widget(Label(text='Email:', color=estilo.colorTitulo()))

        self.email_entry = TextInput(multiline=False, size_hint_y=None, height=30,
                                     background_color=estilo.colorLetra(),
                                     foreground_color=estilo.colorFondo())
        self.email_entry.bind(on_text_validate=lambda instance: self.submit())
        layout.add_widget(self.email_entry)

        layout.add_widget(Label(text='Contraseña:', color=estilo.colorTitulo()))
        self.pwd_entry = TextInput(password=True, multiline=False, size_hint_y=None, height=30,
                                   background_color=estilo.colorLetra(),
                                   foreground_color=estilo.colorFondo())
        self.pwd_entry.bind(on_text_validate=lambda instance: self.submit())
        layout.add_widget(self.pwd_entry)

        # Botones
        login_btn = Button(text='Iniciar sesión', size_hint_y=None, height=50,
                           background_color=estilo.colorFondoH(), color=estilo.colorLetraH())
        login_btn.bind(on_release=lambda x: self.submit())
        layout.add_widget(login_btn)

        register_btn = Button(text='Registrarse', size_hint_y=None, height=50,
                              background_color=estilo.colorLetra(), color=estilo.colorFondo())
        register_btn.bind(on_release=lambda x: self.controladorVistas.open_register())
        layout.add_widget(register_btn)

        exit_btn = Button(text='Salir', size_hint_y=None, height=50,
                          background_color=estilo.colorLetra(), color=estilo.colorFondo())
        exit_btn.bind(on_release=lambda x: App.get_running_app().stop())
        layout.add_widget(exit_btn)

        # Botón cambiar tema
        theme_btn = Button(text='🎨', size_hint=(None, None), size=(50, 50),
                           background_color=estilo.colorLetra(), color=estilo.colorFondo())
        theme_btn.bind(on_release=lambda x: self.controladorVistas.open_temas())
        layout.add_widget(theme_btn)

        self.add_widget(layout)

    def submit(self):
        email = self.email_entry.text.strip()
        pwd = self.pwd_entry.text.strip()
        user = [email, pwd]
        controlador = ControladorLogin(None, None, user, self.estilo, self.notificationService)
        if hasattr(controlador, "set_notification_service"):
            controlador.set_notification_service(self.notificationService)
        controlador.login(user)