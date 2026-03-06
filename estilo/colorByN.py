from estilo.estilizador import Estilo
from estilo.colorUtils import normalizar_color
class ColorByN(Estilo):
    def __init__(self):
        self.nombre = "bnw"
        self.fg ="#E7E7E7"
        self.bg ="#000000"
        self.fgH ="#FFFFFF"
        self.bgH ="#858585"  
        self.titCol = "#E7E7E7"   
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