"""Capa de repositorios: único punto de acceso a datos de AgroConecta.

Las funciones ``get_*_repo`` devuelven la implementación SQLAlchemy configurada
(``DATABASE_URL``). Cambiar de motor no requiere tocar nada más.
"""
from repositorios.cultivo_repo import SQLAlchemyCultivoRepository
from repositorios.interfaces import (
    CultivoRepository, NotificacionRepository, PedidoRepository, RolRepository, UsuarioRepository,
)
from repositorios.notificacion_repo import SQLAlchemyNotificacionRepository
from repositorios.pedido_repo import SQLAlchemyPedidoRepository
from repositorios.rol_repo import SQLAlchemyRolRepository
from repositorios.usuario_repo import SQLAlchemyUsuarioRepository


def get_usuario_repo() -> UsuarioRepository:
    return SQLAlchemyUsuarioRepository()


def get_rol_repo() -> RolRepository:
    return SQLAlchemyRolRepository()


def get_cultivo_repo() -> CultivoRepository:
    return SQLAlchemyCultivoRepository()


def get_pedido_repo() -> PedidoRepository:
    return SQLAlchemyPedidoRepository()


def get_notificacion_repo() -> NotificacionRepository:
    return SQLAlchemyNotificacionRepository()
