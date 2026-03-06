from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from diccionarios import TEMAS
import modelo.saveConfig
from controlador.controladorTemas import ControladorTemas
import logging

logger = logging.getLogger(__name__)

class SelecTema(BoxLayout):
    def __init__(self,root, estilo, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self.estilo = estilo
        self.controladorTema = ControladorTemas(self, None, self.estilo)
        self.root=root
        # Título
        self.add_widget(Label(
            text="Elegir modo de colores",
            font_size=24,
            bold=True,
            color=self.estilo.colorTitulo()
        ))

        # Spinner (equivalente a OptionMenu)
        opciones = list(TEMAS.keys())
        self.tipo = self.traduz()
        self.spinner = Spinner(
            text=self.tipo,
            values=opciones,
            size_hint_y=None,
            height=44
        )
        self.spinner.bind(text=self.prever)
        self.add_widget(self.spinner)

        # Botones
        aceptar_btn = Button(
            text='Aceptar',
            size_hint_y=None,
            height=50,
            background_color=self.estilo.colorLetra(),
            color=self.estilo.colorFondo()
        )
        aceptar_btn.bind(on_release=lambda x: self.submit())
        self.add_widget(aceptar_btn)

        cancelar_btn = Button(
            text='Cancelar',
            size_hint_y=None,
            height=50,
            background_color=self.estilo.colorLetra(),
            color=self.estilo.colorFondo()
        )
        cancelar_btn.bind(on_release=lambda x: self.back())
        self.add_widget(cancelar_btn)

    def traduz(self):
        codigoANombre = {v: k for k, v in TEMAS.items()}
        return codigoANombre.get(modelo.saveConfig.cargar(), 'Oscuro')

    def prever(self, spinner, valor):
        tipito = TEMAS.get(valor, "dark")
        self.controladorTema.aplicarTema(tipito)

    def submit(self):
        tipito = TEMAS.get(self.spinner.text, "dark")
        self.controladorTema.aceptarTema(tipito)

    def back(self):
        logger.info('\t\tOPERACION CANCELADA')
        from controlador.controladorVistas import ControladorVistas
        
        #self.controlador = ControladorVistas(None, None, None, None, self.estilo, None)
        self.controlador = ControladorVistas(
            frame=self,           # <-- usar este BoxLayout como contenedor
            root=None,            # puedes dejar None si no lo usas
            user=None,
            usuario_objetivo=None,
            estilo=self.estilo,
            notificationService=None
)

        self.controlador.open_main()