from estilo.estilizador import Estilo
from estilo.colorUtils import normalizar_color

class ColorOscuro(Estilo):
    
    def __init__(self):     
        self.nombre = "dark"
        self.bg ="#2C2C2C"
        self.fg ="#E3ECEE"  
        self.bgH ="#144136"
        self.fgH ="#0DA7BB"  
        self.titCol = "#C7E6EC"   
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