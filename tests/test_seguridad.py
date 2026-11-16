import hashlib

from auth.seguridad import (
    es_hash_bcrypt, es_hash_legado, hash_contrasena, necesita_rehash, verificar_contrasena,
)
from modelo.CRUD import buscarUsuario
from repositorios import get_usuario_repo


def test_hash_es_bcrypt_y_con_sal():
    h1, h2 = hash_contrasena("Secreta123!"), hash_contrasena("Secreta123!")
    assert es_hash_bcrypt(h1) and h1.startswith("$2")
    assert h1 != h2  # sal distinta en cada hash


def test_verificacion_correcta_e_incorrecta():
    h = hash_contrasena("Secreta123!")
    assert verificar_contrasena("Secreta123!", h)
    assert not verificar_contrasena("otra", h)
    assert not verificar_contrasena("", h)
    assert not verificar_contrasena("Secreta123!", "")


def test_contrasena_muy_larga_no_se_trunca():
    larga = "a" * 100
    h = hash_contrasena(larga)
    assert verificar_contrasena(larga, h)
    assert not verificar_contrasena("a" * 99 + "b", h)


def test_hash_legado_sha256_se_reconoce_y_verifica():
    legado = hashlib.sha256(b"vieja").hexdigest()
    assert es_hash_legado(legado) and not es_hash_bcrypt(legado)
    assert verificar_contrasena("vieja", legado)
    assert not verificar_contrasena("nueva", legado)
    assert necesita_rehash(legado)
    assert not necesita_rehash(hash_contrasena("x"))


def test_hash_basura_no_verifica():
    assert not verificar_contrasena("x", "no-es-un-hash")


def test_login_migra_hash_legado_a_bcrypt(crear_usuario):
    crear_usuario("Campesino", "viejo@mail.com")
    legado = hashlib.sha256(b"Vieja123!").hexdigest()
    repo = get_usuario_repo()
    repo.actualizar_password("viejo@mail.com", legado)

    ok, user = buscarUsuario("viejo@mail.com", "Vieja123!")
    assert ok and es_hash_bcrypt(user["password"])
    guardado = repo.obtener_por_email("viejo@mail.com")["password"]
    assert es_hash_bcrypt(guardado)
    assert verificar_contrasena("Vieja123!", guardado)

    # Tras la migración sigue entrando, y ya no cambia el hash en cada login.
    ok, _ = buscarUsuario("viejo@mail.com", "Vieja123!")
    assert ok
    assert repo.obtener_por_email("viejo@mail.com")["password"] == guardado


def test_login_con_contrasena_incorrecta_no_migra(crear_usuario):
    crear_usuario("Campesino", "viejo@mail.com")
    legado = hashlib.sha256(b"Vieja123!").hexdigest()
    repo = get_usuario_repo()
    repo.actualizar_password("viejo@mail.com", legado)
    ok, user = buscarUsuario("viejo@mail.com", "mala")
    assert not ok and user is None
    assert repo.obtener_por_email("viejo@mail.com")["password"] == legado


def test_login_usuario_inexistente():
    assert buscarUsuario("nadie@mail.com", "x") == (False, None)


def test_admin_inicial_con_hash_legado_puede_entrar_y_se_migra():
    ok, user = buscarUsuario("ADMIN", "ADMIN")
    assert ok and es_hash_bcrypt(user["password"])
