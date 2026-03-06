import modelo.saveConfig
from estilo.estiloFactory import EstiloFactory
class TemaActual:

    _estilo = None

    @classmethod
    def cargar(cls):
        """Carga el tema guardado"""
        tipo = modelo.saveConfig.cargar()
        cls._estilo = EstiloFactory.definirEstilo(tipo)
        return cls._estilo

    @classmethod
    def obtener(cls):
        """Devuelve el estilo actual"""
        if cls._estilo is None:
            return cls.cargar()
        return cls._estilo

    @classmethod
    def cambiar(cls, tipo):
        """Cambia el tema actual"""
        modelo.saveConfig.guardar(tipo)
        cls._estilo = EstiloFactory.definirEstilo(tipo)
        return cls._estilo