from sqlalchemy.orm import Session, sessionmaker

from repositorios.database import session_scope


class SQLAlchemyRepo:
    """Base común: cada operación abre y cierra su propia sesión."""

    def __init__(self, session_factory: sessionmaker[Session] | None = None):
        self._sf = session_factory

    def _session(self):
        return session_scope(self._sf)
