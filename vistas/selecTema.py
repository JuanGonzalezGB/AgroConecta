# selec_tema.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.app import App
import logging

import modelo.saveConfig
from estilo.temaActual import TemaActual
from diccionarios import TEMAS

logger = logging.getLogger(__name__)

class SelecTema(BoxLayout):
    def __init__(self, screen = None, estilo, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self.estilo = estilo
        self.screen = screen
        # Título
        self.add_widget(Label(text="Elegir modo de colores",
                              font_size=24, bold=True,
                              color=self.estilo.colorTitulo()))

        # Spinner
        opciones = list(TEMAS.keys())
        self.tipo = self.traduz()
        self.spinner = Spinner(text=self.tipo, values=opciones, size_hint_y=None, height=44)
        self.spinner.bind(text=self.prever)
        self.add_widget(self.spinner)

        # Botón aceptar
        aceptar_btn = Button(text='Aceptar', size_hint_y=None, height=50,
                             background_color=self.estilo.colorLetra(), color=self.estilo.colorFondo())
        aceptar_btn.bind(on_release=lambda x: self.submit())
        self.add_widget(aceptar_btn)

        # Botón cancelar
        cancelar_btn = Button(text='Cancelar', size_hint_y=None, height=50,
                              background_color=self.estilo.colorLetra(), color=self.estilo.colorFondo())
        cancelar_btn.bind(on_release=lambda x: self.back())
        self.add_widget(cancelar_btn)

    def traduz(self):
        codigoANombre = {v: k for k, v in TEMAS.items()}
        return codigoANombre.get(modelo.saveConfig.cargar(), 'Oscuro')

    def prever(self, spinner, valor):
        tipito = TEMAS.get(valor, "dark")
        logger.debug(f"Preview tema: {tipito}")
        # Actualiza el fondo de la pantalla actual
        estilo_preview = TemaActual.cambiar(tipito)
        App.get_running_app().root.current_screen.actualizar_fondo(estilo_preview)

    def submit(self):
        tipito = TEMAS.get(self.spinner.text, "dark")
        estilo_nuevo = TemaActual.cambiar(tipito)
        App.get_running_app().root.current_screen.actualizar_fondo(estilo_nuevo)
        App.get_running_app().root.current = "MainView"

    def back(self):
        App.get_running_app().root.current = "MainView"