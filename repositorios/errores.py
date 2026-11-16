class RepositorioError(Exception):
    """Error base de la capa de repositorios."""


class DuplicadoError(RepositorioError):
    """Ya existe una entidad con la misma clave única (p. ej. email o id de rol)."""


class NoEncontradoError(RepositorioError):
    """La entidad referenciada no existe."""
