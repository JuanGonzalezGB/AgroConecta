from estilo.estilizador import Estilo
from estilo.colorUtils import normalizar_color

class ColorAzul(Estilo):
    
    def __init__(self):     
        self.nombre = "blue"
        self.bg ="#0E2D50"
        self.fg ="#F5F0D2"  
        self.bgH ="#375F8B"
        self.fgH ="#DDBF12"   
        self.titCol = "#F1E7AA"   
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