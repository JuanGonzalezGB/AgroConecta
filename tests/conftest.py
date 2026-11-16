import pytest

from auth.seguridad import hash_contrasena
from repositorios import database


@pytest.fixture(autouse=True)
def db():
    """Base SQLite en memoria, limpia en cada prueba. Sin Tkinter ni servidores."""
    database.configure("sqlite://")
    from modelo.inicializacion import inicializar_sistema
    inicializar_sistema()  # tablas + roles iniciales + admin
    yield database.get_engine()
    database.get_engine().dispose()


@pytest.fixture
def crear_usuario():
    """Fábrica: crea un usuario por su tipo ('Campesino', 'Restaurante', 'Delivery')."""
    from modelo.CRUD import crearUsuario
    from repositorios import get_usuario_repo

    def _crear(tipo, email, nombre=None, password="Clave123!", **extra):
        datos = {"nombre": nombre or email.split("@")[0], "email": email,
                 "password": hash_contrasena(password), **extra}
        ok, msg = crearUsuario(tipo, datos)
        assert ok, msg
        return get_usuario_repo().obtener_por_email(email)

    return _crear


@pytest.fixture
def admin():
    from repositorios import get_usuario_repo
    return get_usuario_repo().obtener_por_email("ADMIN")


@pytest.fixture(autouse=True)
def _bcrypt_rapido(monkeypatch):
    """Costo mínimo de bcrypt solo en pruebas, para que la suite sea rápida."""
    monkeypatch.setattr("auth.seguridad.BCRYPT_ROUNDS", 4)


@pytest.fixture(autouse=True)
def _sin_ui(monkeypatch):
    """Los avisos gráficos de permiso denegado no deben abrir ventanas en las pruebas."""
    monkeypatch.setattr("auth.permisos._avisar_permiso_denegado", lambda permiso: None)
