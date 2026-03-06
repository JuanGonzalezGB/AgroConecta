import logging
from estilo import estiloFactory
import modelo.saveConfig
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from estilo.colorUtils import normalizar_color

logger = logging.getLogger(__name__)


class ControladorTemas:

    def __init__(self, layout, root, estilo):

        self.layout = layout
        self.root = root
        self.estilo = estilo
        self.tipo = modelo.saveConfig.cargar()

        self.rect_bg = None
        self.rect_color = None

        if self.layout:
            estiloSel = estiloFactory.EstiloFactory.definirEstilo(self.tipo)
            self._crear_fondo(estiloSel)

    def _crear_fondo(self, estiloSel):

        color = normalizar_color(estiloSel.colorFondo())

        # si el rectangulo no existe lo creamos
        if not self.rect_bg:

            with self.layout.canvas.before:
                self.rect_color = Color(*color)
                self.rect_bg = Rectangle(pos=(0, 0), size=Window.size)

            Window.bind(size=self._update_rect)

        else:
            # si ya existe solo cambiamos color
            self.rect_color.rgba = color

        self._aplicar_colores_widgets(estiloSel)

    def _aplicar_colores_widgets(self, estiloSel):

        for widget in self.layout.walk():

            if isinstance(widget, Label):
                widget.color = normalizar_color(estiloSel.colorTitulo())

            elif isinstance(widget, Button):

                widget.background_normal = ""
                widget.background_color = normalizar_color(estiloSel.colorLetra())
                widget.color = normalizar_color(estiloSel.colorFondo())

            elif isinstance(widget, Spinner):

                widget.background_normal = ""
                widget.background_color = normalizar_color(estiloSel.colorFondo())
                widget.color = normalizar_color(estiloSel.colorLetra())

    def aplicarTema(self, tipo):

        if not self.layout:
            logger.warning("No hay layout disponible")
            return

        self.tipo = tipo
        estiloSel = estiloFactory.EstiloFactory.definirEstilo(self.tipo)

        logger.debug(f'[Aplicando tema preview] {self.tipo}')

        self._crear_fondo(estiloSel)

    def _update_rect(self, *args):

        if self.rect_bg:
            self.rect_bg.size = Window.size

    def aceptarTema(self, tipo):

        if not self.layout:
            logger.warning("No hay layout disponible")
            return

        from controlador.controladorVistas import ControladorVistas

        modelo.saveConfig.guardar(tipo)

        estiloSel = estiloFactory.EstiloFactory.definirEstilo(tipo)

        controlaVistas = ControladorVistas(
            self.layout,
            self.root,
            None,
            None,
            estiloSel,
            None
        )

        controlaVistas.open_main()

        logger.info(f'Tema "{tipo}" guardado.')