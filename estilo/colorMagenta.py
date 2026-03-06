from estilo.estilizador import Estilo
from estilo.colorUtils import normalizar_color
class ColorMagenta(Estilo):
    def __init__(self):
        self.nombre = "magenta"
        self.bg ="#EA00FF"
        self.fg ="#F500B8"
        self.fgH ="#771177"
        self.bgH ="#915883"     
        self.titCol = "#F1F511"  
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