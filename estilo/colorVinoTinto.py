from estilo.estilizador import Estilo

class ColorVinotinto(Estilo):
    def __init__(self):
        self.nombre = "wine"
        self.bg ="#55071E"
        self.fg ="#E90909"
        self.fgH ="#0966A3"
        self.bgH ="#58915B"     
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