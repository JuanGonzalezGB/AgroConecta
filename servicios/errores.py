"""Errores de negocio. No dependen de HTTP ni de Tkinter: cada cliente los traduce a su manera."""


class ServicioError(Exception):
    codigo = "error"

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class ValidacionError(ServicioError):
    codigo = "validacion"


class NoAutenticadoError(ServicioError):
    codigo = "no_autenticado"


class PermisoDenegadoError(ServicioError):
    codigo = "permiso_denegado"


class NoEncontradoError(ServicioError):
    codigo = "no_encontrado"


class ConflictoError(ServicioError):
    codigo = "conflicto"
