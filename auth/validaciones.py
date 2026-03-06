import re
def validar_nombre(nombre):
    patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}$"
    return bool(re.match(patron, nombre))


def validar_email(email):
    patron = r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,6}$"
    return bool(re.match(patron, email))


def validar_contrasena(contrasena):
    patron = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$"
    return bool(re.match(patron, contrasena))


def validar_nit(nit):
    patron = r"^\d{6,12}(-\d)?$"
    return bool(re.match(patron, nit))


def validar_telefono(telefono):
    patron = r"^\d{7,10}$"
    return bool(re.match(patron, telefono))

