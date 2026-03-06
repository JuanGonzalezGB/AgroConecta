from estilo.estilizador import Estilo


class ColorJS(Estilo):
    
    def __init__(self):     
        self.nombre = "soldiergreen"
        self.bg ="#666600"
        self.fg ="#33FFFF"
        self.bgH ="#cccc00"
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