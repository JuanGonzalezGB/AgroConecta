from estilo.estilizador import Estilo

class ColorByN(Estilo):
    def __init__(self):
        self.nombre = "bnw"
        self.fg ="#E7E7E7"
        self.bg ="#000000"
        self.fgH ="#FFFFFF"
        self.bgH ="#858585"  
        self.titCol = "#E7E7E7"   
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