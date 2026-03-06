from estilo.estilizador import Estilo
from estilo.colorUtils import normalizar_color
class ColorVinotinto(Estilo):
    def __init__(self):
        self.nombre = "wine"
        self.bg ="#55071E"
        self.fg ="#E90909"
        self.fgH ="#0966A3"
        self.bgH ="#58915B"     
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