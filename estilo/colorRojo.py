from estilo.estilizador import Estilo
from estilo.colorUtils import normalizar_color
class ColorRojo(Estilo):
    def __init__(self):     
        self.nombre = "red"
        self.fg ="#FFA4A4"
        self.bg ="#200101"  
        self.fgH ="#FF3300"
        self.bgH ="#FFC5A4" 
        self.titCol = "#B10300"  
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