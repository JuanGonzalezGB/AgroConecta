from modelo.CRU import asignar_rol_a_usuario, quitar_rol_a_usuario
from modelo.rolesModel import (
    actualizar_permiso, actualizar_rol, agregar_permiso_a_rol, agregar_rol, aplicar_roles_y_permisos,
    cargar_roles, eliminar_permiso_de_rol, eliminar_rol, guardar_roles, obtener_rol_por_id,
)
from repositorios import get_usuario_repo


def _permisos(email):
    return set(get_usuario_repo().obtener_por_email(email)["permisos"])


def test_crear_rol_con_permisos_y_asignarlo(admin, crear_usuario):
    ok, _ = agregar_rol({"id": "inspector", "nombre": "Inspector", "vista": "open_generica"})
    assert ok
    assert agregar_permiso_a_rol("inspector", {"id": "ver_reportes", "nombre": "Ver reportes"}, "lectura")[0]
    crear_usuario("Restaurante", "r@x.com")
    base = _permisos("r@x.com")

    ok, _ = asignar_rol_a_usuario("r@x.com", "inspector", user=admin)
    assert ok
    assert _permisos("r@x.com") == base | {"ver_reportes"}
    assert set(get_usuario_repo().obtener_por_email("r@x.com")["roles"]) == {"restaurante", "inspector"}


def test_rol_duplicado_y_categoria_invalida():
    agregar_rol({"id": "x", "nombre": "X"})
    assert agregar_rol({"id": "x", "nombre": "Otra vez"})[0] is False
    assert agregar_permiso_a_rol("x", {"id": "p", "nombre": "p"}, "inventada") == (False, "Categoría inválida")
    assert agregar_permiso_a_rol("nope", {"id": "p", "nombre": "p"}, "otros") == (False, "Rol no encontrado")
    agregar_permiso_a_rol("x", {"id": "p", "nombre": "p"}, "otros")
    assert agregar_permiso_a_rol("x", {"id": "p", "nombre": "p"}, "otros")[0] is False


def test_editar_rol_y_permiso_se_refleja_en_todos_los_roles():
    for rid in ("a", "b"):
        agregar_rol({"id": rid, "nombre": rid.upper()})
        agregar_permiso_a_rol(rid, {"id": "compartido", "nombre": "viejo"}, "escritura")
    assert actualizar_permiso("compartido", "Nuevo nombre")[0]
    for rid in ("a", "b"):
        assert obtener_rol_por_id(rid)["permisos"]["escritura"] == [{"id": "compartido", "nombre": "Nuevo nombre"}]
    assert actualizar_rol("a", {"nombre": "Renombrado", "vista": "v"})
    assert obtener_rol_por_id("a")["nombre"] == "Renombrado"
    assert actualizar_rol("nope", {"nombre": "x"}) is False


def test_guardar_roles_reemplaza_permisos_como_hace_la_vista_admin():
    roles = cargar_roles()
    rol = next(r for r in roles if r["id"] == "delivery")
    rol["permisos"]["escritura"].append({"id": "marcar_entrega", "nombre": "marcar_entrega"})
    guardar_roles(roles)
    ids = [p["id"] for p in obtener_rol_por_id("delivery")["permisos"]["escritura"]]
    assert ids == ["marcar_entrega"]


def test_quitar_permiso_actualiza_a_los_usuarios(crear_usuario):
    crear_usuario("Campesino", "c@x.com")
    assert "vender_cultivo" in _permisos("c@x.com")
    ok, msg = eliminar_permiso_de_rol("vender_cultivo")
    assert ok and "Usuarios afectados: 1" in msg
    assert "vender_cultivo" not in _permisos("c@x.com")
    assert eliminar_permiso_de_rol("vender_cultivo")[0] is False


def test_eliminar_rol_quita_roles_y_permisos_a_usuarios(admin, crear_usuario):
    agregar_rol({"id": "temporal", "nombre": "T"})
    agregar_permiso_a_rol("temporal", {"id": "solo_temporal", "nombre": "x"}, "otros")
    crear_usuario("Campesino", "c@x.com")
    asignar_rol_a_usuario("c@x.com", "temporal", user=admin)
    assert "solo_temporal" in _permisos("c@x.com")

    assert eliminar_rol("temporal", admin)[0]
    u = get_usuario_repo().obtener_por_email("c@x.com")
    assert u["roles"] == ["campesino"] and "solo_temporal" not in u["permisos"]
    assert eliminar_rol("temporal", admin) == (False, "Rol no encontrado")


def test_eliminar_rol_no_quita_permiso_que_otro_rol_tambien_concede(admin, crear_usuario):
    agregar_rol({"id": "extra", "nombre": "E"})
    agregar_permiso_a_rol("extra", {"id": "ver_inventario", "nombre": "ver_inventario"}, "lectura")
    crear_usuario("Campesino", "c@x.com")
    asignar_rol_a_usuario("c@x.com", "extra", user=admin)
    eliminar_rol("extra", admin)
    assert "ver_inventario" in _permisos("c@x.com")  # sigue viniendo del rol 'campesino'


def test_asignar_y_quitar_validan_permiso_y_roles(admin, crear_usuario):
    crear_usuario("Campesino", "c@x.com")
    sin_permiso = crear_usuario("Restaurante", "r@x.com")
    assert asignar_rol_a_usuario("c@x.com", "delivery", user=sin_permiso)[0] is False  # denegado
    assert asignar_rol_a_usuario("c@x.com", "no_existe", user=admin) == (False, "Rol 'no_existe' no existe")
    assert asignar_rol_a_usuario("nadie@x.com", "delivery", user=admin) == (False, "Usuario no encontrado")
    assert asignar_rol_a_usuario("c@x.com", ["delivery", "no_existe"], user=admin)[0] is False

    asignar_rol_a_usuario("c@x.com", ["delivery", "restaurante"], user=admin)
    ok, msg = quitar_rol_a_usuario("c@x.com", ["delivery", "admin"], user=admin)
    assert ok and "'admin' no se puede quitar" in msg
    assert set(get_usuario_repo().obtener_por_email("c@x.com")["roles"]) == {"campesino", "restaurante"}


def test_aplicar_roles_y_permisos_recalcula(crear_usuario):
    u = crear_usuario("Restaurante", "r@x.com")
    u["permisos"] = ["basura"]
    assert "basura" not in aplicar_roles_y_permisos(u)["permisos"]
