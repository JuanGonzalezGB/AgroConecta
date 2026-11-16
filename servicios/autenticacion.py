"""Registro, login y cambio de contraseña."""
from auth import validaciones as v
from auth.seguridad import hash_contrasena, verificar_contrasena
from diccionarios import LLAVESFORMUSUARIOS, TIPOSUSUARIOS
from modelo.CRUD import buscarUsuario, crearUsuario
from repositorios import get_usuario_repo
from servicios.errores import ConflictoError, NoAutenticadoError, NoEncontradoError, ValidacionError

TIPOS = {valor: etiqueta for etiqueta, valor in TIPOSUSUARIOS.items()}  # 'campesino' -> 'Campesino'


def publico(usuario: dict) -> dict:
    """Usuario sin el hash de la contraseña."""
    return {k: val for k, val in usuario.items() if k != "password"}


def validar_datos(tipo_etiqueta: str, datos: dict) -> list[str]:
    errores = []
    if not v.validar_nombre(datos.get("nombre", "")):
        errores.append("Nombre inválido (solo letras y espacios, mínimo 2).")
    if not v.validar_email(datos.get("email", "")):
        errores.append("Correo electrónico con formato inválido.")
    if not v.validar_contrasena(datos.get("password", "")):
        errores.append("La contraseña debe tener 8+ caracteres con mayúscula, minúscula, número y símbolo.")
    if not v.validar_telefono(datos.get("telefono", "")):
        errores.append("El teléfono debe tener entre 7 y 10 dígitos.")
    if "nit" in LLAVESFORMUSUARIOS[tipo_etiqueta] and not v.validar_nit(datos.get("nit", "")):
        errores.append("El NIT debe tener entre 6 y 12 dígitos (puede incluir un guion).")
    return errores


def registrar(tipo: str, datos: dict) -> dict:
    """``tipo``: 'campesino' | 'restaurante' | 'delivery'. Devuelve el usuario creado (sin hash)."""
    etiqueta = TIPOS.get(tipo)
    if etiqueta is None:
        raise ValidacionError(f"Tipo de usuario inválido: {tipo}")
    permitidos = LLAVESFORMUSUARIOS[etiqueta]
    datos = {k: datos[k] for k in permitidos if datos.get(k) is not None}
    errores = validar_datos(etiqueta, datos)
    if errores:
        raise ValidacionError(" ".join(errores))
    datos["password"] = hash_contrasena(datos["password"])
    ok, msg = crearUsuario(etiqueta, datos)
    if not ok:
        raise ConflictoError(msg)
    return publico(get_usuario_repo().obtener_por_email(datos["email"]))


def login(email: str, password: str) -> dict:
    ok, usuario = buscarUsuario(email, password)  # migra hashes SHA-256 legados a bcrypt
    if not ok:
        raise NoAutenticadoError("Correo o contraseña incorrectos.")
    if not usuario.get("roles"):
        raise NoAutenticadoError("Este usuario no tiene roles asignados.")
    return usuario


def obtener_usuario(email: str) -> dict:
    usuario = get_usuario_repo().obtener_por_email(email)
    if usuario is None:
        raise NoEncontradoError("Usuario no encontrado.")
    return usuario


def cambiar_contrasena(email: str, actual: str, nueva: str) -> None:
    usuario = obtener_usuario(email)
    if not verificar_contrasena(actual, usuario.get("password", "")):
        raise NoAutenticadoError("La contraseña actual es incorrecta.")
    if not v.validar_contrasena(nueva):
        raise ValidacionError(
            "La nueva contraseña no cumple los requisitos: mínimo 8 caracteres, "
            "mayúscula, minúscula, número y carácter especial.")
    get_usuario_repo().actualizar_password(email, hash_contrasena(nueva))
