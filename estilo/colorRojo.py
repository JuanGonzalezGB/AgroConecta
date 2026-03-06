from estilo.estilizador import Estilo

class ColorRojo(Estilo):
    def __init__(self):     
        self.nombre = "red"
        self.fg ="#FFA4A4"
        self.bg ="#200101"  
        self.fgH ="#FF3300"
        self.bgH ="#FFC5A4" 
        self.titCol = "#B10300"  
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