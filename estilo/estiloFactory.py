from estilo import colorOscuro
from diccionarios import CLASESTEMAS


class EstiloFactory:
    @staticmethod
    def definirEstilo(tipo: str):    
        estilo = CLASESTEMAS.get(tipo, colorOscuro.ColorOscuro)
        return estilo()