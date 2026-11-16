"""Arranque del sistema de datos: tablas, roles iniciales y administrador por defecto."""
import logging

from diccionarios import USUARIOS_INICIALES
from modelo.rolesModel import inicializar_roles
from repositorios import get_usuario_repo
from repositorios.database import init_db

logger = logging.getLogger(__name__)


def asegurarAdmin():
    """Crea el administrador inicial (de USUARIOS_INICIALES) si no hay ningún admin."""
    repo = get_usuario_repo()
    if any("admin" in u.get("roles", []) for u in repo.listar()):
        logger.debug("ADMIN ya existe")
        return
    logger.warning("No existe ADMIN, creando desde USUARIOS_INICIALES...")
    admin = dict(USUARIOS_INICIALES["admin"][0], tipo="admin")
    repo.crear(admin)
    logger.info("ADMIN creado correctamente")


def inicializar_sistema():
    """Idempotente: crea tablas, roles iniciales y admin. Llamar al arrancar cualquier cliente."""
    init_db()
    inicializar_roles()
    asegurarAdmin()
