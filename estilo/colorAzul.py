from estilo.estilizador import Estilo


class ColorAzul(Estilo):
    
    def __init__(self):     
        self.nombre = "blue"
        self.bg ="#0E2D50"
        self.fg ="#F5F0D2"  
        self.bgH ="#375F8B"
        self.fgH ="#DDBF12"   
        self.titCol = "#F1E7AA"   
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