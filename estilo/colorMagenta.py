from estilo.estilizador import Estilo

class ColorMagenta(Estilo):
    def __init__(self):
        self.nombre = "magenta"
        self.bg ="#EA00FF"
        self.fg ="#F500B8"
        self.fgH ="#771177"
        self.bgH ="#915883"     
        self.titCol = "#F1F511"  
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