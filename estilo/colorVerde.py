from estilo.estilizador import Estilo
from estilo.colorUtils import normalizar_color
class ColorVerde(Estilo):
    def __init__(self):
        self.nombre = "green"
        self.bg ="#141D03"
        self.fg ="#DDDDBA"
        self.fgH ="#00FF0D"
        self.bgH ="#58915B"     
        self.titCol = "#0FA340"  
    def colorTitulo(self):
        return normalizar_color(self.titCol)         
    def colorFondo(self):
        return normalizar_color(self.bg)
    def colorLetra(self):
        return normalizar_color(self.fg)
    def colorFondoH(self):
        return normalizar_color(self.bgH)
    def colorLetraH(self):
        return normalizar_color(self.fgH)
    def getNombre(self):
        return normalizar_color(self.nombre)