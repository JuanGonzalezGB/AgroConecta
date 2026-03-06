from abc import ABC, abstractmethod
class Estilo(ABC):
    @abstractmethod    
    def colorTitulo(self):
        pass
    @abstractmethod
    def colorFondo(self):
        pass
    @abstractmethod
    def colorLetra(self):
        pass
    @abstractmethod
    def colorFondoH(self):
        pass
    @abstractmethod
    def colorLetraH(self):
        pass
    @abstractmethod
    def getNombre(self):
        pass