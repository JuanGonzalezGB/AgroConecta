from estilo.estilizador import Estilo


class ColorOscuro(Estilo):
    
    def __init__(self):     
        self.nombre = "dark"
        self.bg ="#2C2C2C"
        self.fg ="#E3ECEE"  
        self.bgH ="#144136"
        self.fgH ="#0DA7BB"  
        self.titCol = "#C7E6EC"   
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