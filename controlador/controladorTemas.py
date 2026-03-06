import logging
from estilo import estiloFactory
import modelo.saveConfig
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle

logger = logging.getLogger(__name__)

class ControladorTemas:
    def __init__(self, layout, root, estilo):
        self.layout = layout
        self.root = root
        self.estilo = estilo
        self.tipo = modelo.saveConfig.cargar()  # Tema guardado por defecto
        self.rect_bg = None

        # Aplicar tema inicial al layout desde el inicio
        if self.layout:
            self._crear_fondo(estiloFactory.EstiloFactory.definirEstilo(self.tipo))

    def _crear_fondo(self, estiloSel):
        """Crea el fondo del layout usando canvas"""
        self.layout.canvas.before.clear()
        with self.layout.canvas.before:
            self.rect_color = Color(*estiloSel.colorFondo())  # RGBA 0-1
            #self.rect_bg = Rectangle(pos=self.layout.pos, size=self.layout.size)
        # Actualizar tamaño dinámicamente
        self.layout.bind(pos=self._update_rect, size=self._update_rect)
        # Aplicar colores a los widgets hijos
        self._aplicar_colores_widgets(estiloSel)

    def _aplicar_colores_widgets(self, estiloSel):
        """Aplica colores a los widgets hijos del layout"""
        for widget in self.layout.children:
            if isinstance(widget, Label):
                widget.color = estiloSel.colorTitulo()
            elif isinstance(widget, Button):
                widget.background_color = estiloSel.colorLetra()
                widget.color = estiloSel.colorFondo()
            elif isinstance(widget, Spinner):
                widget.background_color = estiloSel.colorFondo()
                widget.color = estiloSel.colorLetra()

    def aplicarTema(self, tipo):
        """Aplica el tema seleccionado a la UI en tiempo real"""
        if not self.layout:
            logger.warning("No hay layout disponible para aplicar el tema")
            return

        self.tipo = tipo
        estiloSel = estiloFactory.EstiloFactory.definirEstilo(self.tipo)
        logger.debug(f'[Aplicando tema] {self.tipo}...')
        self._crear_fondo(estiloSel)
        logger.info(f'Tema {self.tipo} aplicado correctamente.')

    def _update_rect(self, *args):
        """Mantener el fondo del layout actualizado al redimensionar"""
        if self.rect_bg:
            self.rect_bg.pos = self.layout.pos
            self.rect_bg.size = self.layout.size

    def aceptarTema(self, tipo):
        """Guardar el tema seleccionado y recargar MainView"""
        if not self.layout:
            logger.warning("No hay layout disponible para aceptar el tema")
            return

        logger.debug(f'Intentando guardar tema: {tipo}...')
        from controlador.controladorVistas import ControladorVistas

        # Guardar configuración
        modelo.saveConfig.guardar(tipo)
        estiloSel = estiloFactory.EstiloFactory.definirEstilo(tipo)

        # Recargar MainView usando ControladorVistas
        controlaVistas = ControladorVistas(self.layout, self.root, None, None, estiloSel, None)
        controlaVistas.open_main()
        logger.info(f'Tema "{tipo}" guardado y MainView recargado.')