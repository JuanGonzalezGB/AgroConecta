import pytest

from auth.permisos import require_permission
from diccionarios import PERMISOS_ALIAS


@require_permission("agregar_cultivo")
def _accion(*, user):
    return "hecho"


def test_usuario_con_permiso_pasa(crear_usuario):
    campesino = crear_usuario("Campesino", "c@x.com")
    assert _accion(user=campesino) == "hecho"


def test_usuario_sin_permiso_es_denegado(crear_usuario):
    restaurante = crear_usuario("Restaurante", "r@x.com")
    assert _accion(user=restaurante) == (False, "Permiso 'agregar_cultivo' denegado")


def test_el_permiso_se_lee_de_los_roles_no_del_dict_del_usuario(crear_usuario):
    """Un dict 'user' manipulado no concede permisos: se consultan los roles reales."""
    restaurante = crear_usuario("Restaurante", "r@x.com")
    falso = dict(restaurante, permisos=["agregar_cultivo"])
    assert _accion(user=falso)[0] is False


def test_alias_de_permiso(crear_usuario, admin):
    from modelo.rolesModel import agregar_permiso_a_rol
    assert PERMISOS_ALIAS["agregar_cultivo"] == ["añadir_cultivo"]
    agregar_permiso_a_rol("restaurante", {"id": "añadir_cultivo", "nombre": "añadir_cultivo"}, "escritura")
    restaurante = crear_usuario("Restaurante", "r@x.com")
    assert _accion(user=restaurante) == "hecho"


def test_requiere_user_como_keyword():
    with pytest.raises(ValueError):
        _accion()
    with pytest.raises(ValueError):
        _accion(user="no-es-dict")


def test_designator_interno_pasa_siempre():
    assert _accion(user={"email": "DESIGNATOR"}) == "hecho"


def test_usuario_sin_roles_es_denegado():
    assert _accion(user={"email": "x@x.com", "roles": []})[0] is False
