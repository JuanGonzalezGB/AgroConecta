from estilo.estilizador import Estilo
from estilo.colorUtils import normalizar_color
class ColorClaro(Estilo):
    def __init__(self):     
        self.nombre = "light"
        self.fg ="#66817E"
        self.bg ="#D2ECF1"  
        self.fgH ="#144136"
        self.bgH ="#387077"  
        self.titCol = "#234047"   
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