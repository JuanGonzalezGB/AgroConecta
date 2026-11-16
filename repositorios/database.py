"""Configuración de la base de datos (SQLAlchemy 2.x).

Por defecto usa SQLite en ``data/agroconecta.db``. Para cambiar de motor basta con
definir la variable de entorno ``DATABASE_URL`` (ver ``.env.example``); ningún otro
módulo conoce el motor concreto.

Sesiones: una por operación (``session_scope``). El engine usa
``check_same_thread=False`` para poder compartirse entre Tkinter y los hilos de FastAPI.
"""
import logging
import os
import threading
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE_URL = "sqlite:///data/agroconecta.db"

load_dotenv(BASE_DIR / ".env")

_lock = threading.Lock()
_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def _es_sqlite(url) -> bool:
    return url.get_backend_name() == "sqlite"


def _es_memoria(url) -> bool:
    return _es_sqlite(url) and url.database in (None, "", ":memory:")


def _anclar_ruta_sqlite(url):
    """Las rutas SQLite relativas se resuelven desde la raíz del proyecto, no del cwd."""
    if _es_sqlite(url) and not _es_memoria(url):
        ruta = Path(url.database)
        if not ruta.is_absolute():
            ruta = BASE_DIR / ruta
        ruta.parent.mkdir(parents=True, exist_ok=True)
        return url.set(database=str(ruta))
    return url


def make_engine(database_url: str | None = None) -> Engine:
    url = make_url(database_url or get_database_url())
    url = _anclar_ruta_sqlite(url)
    kwargs: dict = {}
    if _es_sqlite(url):
        kwargs["connect_args"] = {"check_same_thread": False}
        if _es_memoria(url):
            # Una sola conexión compartida: si no, cada conexión vería una BD vacía distinta.
            kwargs["poolclass"] = StaticPool
    engine = create_engine(url, **kwargs)

    if _es_sqlite(url):
        memoria = _es_memoria(url)

        @event.listens_for(engine, "connect")
        def _pragmas(dbapi_conn, _record):
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            cur.execute("PRAGMA busy_timeout=5000")
            if not memoria:
                cur.execute("PRAGMA journal_mode=WAL")
                cur.execute("PRAGMA synchronous=NORMAL")
            cur.close()

    return engine


def configure(database_url: str | None = None) -> Engine:
    """(Re)crea el engine global. Útil para pruebas (``sqlite://``) o para cambiar de URL."""
    global _engine, _session_factory
    with _lock:
        if _engine is not None:
            _engine.dispose()
        _engine = make_engine(database_url)
        _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
        return _engine


def get_engine() -> Engine:
    if _engine is None:
        configure()
    return _engine  # type: ignore[return-value]


def get_session_factory() -> sessionmaker[Session]:
    if _session_factory is None:
        configure()
    return _session_factory  # type: ignore[return-value]


def init_db() -> None:
    """Crea las tablas que falten (sin Alembic por ahora)."""
    from repositorios.modelos import Base

    Base.metadata.create_all(get_engine())
    logger.info("Base de datos lista: %s", get_engine().url.render_as_string(hide_password=True))


@contextmanager
def session_scope(factory: sessionmaker[Session] | None = None):
    """Sesión por operación: commit si todo sale bien, rollback si hay excepción."""
    session = (factory or get_session_factory())()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
