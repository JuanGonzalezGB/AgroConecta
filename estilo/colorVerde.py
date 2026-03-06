from estilo.estilizador import Estilo

class ColorVerde(Estilo):
    def __init__(self):
        self.nombre = "green"
        self.bg ="#141D03"
        self.fg ="#DDDDBA"
        self.fgH ="#00FF0D"
        self.bgH ="#58915B"     
        self.titCol = "#0FA340"  
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