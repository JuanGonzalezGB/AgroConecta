from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle

class BaseScreen(Screen):
    def __init__(self, estilo, **kwargs):
        super().__init__(**kwargs)
        self.estilo = estilo

        with self.canvas.before:
            Color(*self.estilo.colorFondo())
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def actualizar_fondo(self, estilo):
        """Permite cambiar el fondo si cambia el tema"""
        self.estilo = estilo
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.estilo.colorFondo())
            self.rect = Rectangle(size=self.size, pos=self.pos)