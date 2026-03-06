from estilo.estilizador import Estilo

class ColorRasta(Estilo):
    def __init__(self):     
        self.nombre = "rasta"
        self.fg ="#1EFF00"
        self.bg ="#FF0000"  
        self.fgH ="#FFC400"
        self.bgH ="#0400FF" 
        self.titCol = "#00F7FF"  
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