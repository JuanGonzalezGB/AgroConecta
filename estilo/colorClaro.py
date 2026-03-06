from estilo.estilizador import Estilo

class ColorClaro(Estilo):
    def __init__(self):     
        self.nombre = "light"
        self.fg ="#66817E"
        self.bg ="#D2ECF1"  
        self.fgH ="#144136"
        self.bgH ="#387077"  
        self.titCol = "#234047"   
    def colorTitulo(self):
        return self.titCol        
    def colorFondo(self):
        return self.bg
    def colorLetra(self):
        return self.fg
    def colorFondoH(self):
        return self.bgH
    def colorLetraH(self):
        return self.fgH
    def getNombre(self):
        return self.nombre