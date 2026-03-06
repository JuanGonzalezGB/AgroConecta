from estilo.estilizador import Estilo

class ColorRosa(Estilo):
    def __init__(self):     
        self.nombre = "pink"
        self.fg ="#FFB4C4"
        self.bg ="#B6263E"  
        self.fgH ="#530C3C"
        self.bgH ="#EB6788"  
        self.titCol = "#FFBEBE"   
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