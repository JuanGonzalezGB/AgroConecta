"""Inventario del campesino."""
from repositorios import get_cultivo_repo, get_usuario_repo
from servicios.autorizacion import exigir_permiso
from servicios.errores import NoEncontradoError, ValidacionError


def listar_mis_cultivos(usuario: dict) -> list[dict]:
    exigir_permiso(usuario, "ver_inventario")
    return get_cultivo_repo().listar(usuario["email"])


def agregar_cultivo(usuario: dict, nombre: str, cantidad: int, precio: float) -> dict:
    exigir_permiso(usuario, "agregar_cultivo")
    nombre = (nombre or "").strip().lower()
    if not nombre:
        raise ValidacionError("El nombre del cultivo es obligatorio.")
    if cantidad is None or cantidad <= 0:
        raise ValidacionError("La cantidad debe ser mayor que cero.")
    if precio is None or precio <= 0:
        raise ValidacionError("El precio debe ser mayor que cero.")
    return get_cultivo_repo().agregar_o_sumar(usuario["email"], nombre, cantidad, precio)


def eliminar_cultivo(usuario: dict, nombre: str) -> None:
    exigir_permiso(usuario, "eliminar_cultivo")
    if not get_cultivo_repo().eliminar(usuario["email"], nombre.strip().lower()):
        raise NoEncontradoError(f"No se encontró el cultivo '{nombre}'.")


def listar_campesinos(usuario: dict) -> list[dict]:
    """Campesinos con stock disponible (vista del restaurante)."""
    exigir_permiso(usuario, "ver_inventario")
    usuarios = {u["email"]: u for u in get_usuario_repo().listar() if u["tipo"] == "campesinos"}
    resultado = []
    for email, cultivos in get_cultivo_repo().listar_todos().items():
        con_stock = [c for c in cultivos if c["cantidad"] > 0]
        if email in usuarios and con_stock:
            u = usuarios[email]
            resultado.append({"email": email, "nombre": u["nombre"], "direccion": u.get("direccion"),
                              "telefono": u.get("telefono"), "cultivos": con_stock})
    return resultado


def inventario_de_campesino(usuario: dict, email_campesino: str) -> dict:
    exigir_permiso(usuario, "ver_inventario")
    u = get_usuario_repo().obtener_por_email(email_campesino)
    if u is None or u["tipo"] != "campesinos":
        raise NoEncontradoError("Campesino no encontrado.")
    return {"email": u["email"], "nombre": u["nombre"], "direccion": u.get("direccion"),
            "telefono": u.get("telefono"), "cultivos": get_cultivo_repo().listar(email_campesino)}
