"""Migración puntual de contraseñas guardadas en texto plano a bcrypt.

- Texto plano       -> se hashea con bcrypt.
- SHA-256 legado    -> se deja igual: se migra a bcrypt solo en el próximo login
                       correcto (no se puede revertir un hash para re-hashearlo aquí).
- bcrypt            -> se omite.

Uso (desde la raíz del repo):  python -m scripts.encriptarJSON
"""
import logging

from auth.seguridad import es_hash_bcrypt, es_hash_legado, hash_contrasena
from modelo.CRU import cargarUsuarios, guardarUsuarios

logger = logging.getLogger(__name__)


def actualizar_contrasenas():
    usuarios = cargarUsuarios()
    hasheadas = legadas = ya_bcrypt = 0
    try:
        for categoria, lista_usuarios in usuarios.items():
            for u in lista_usuarios:
                actual = u.get("password", "")
                if not actual:
                    logger.warning(f'Usuario sin contraseña en {categoria}: {u.get("email", "[sin email]")}')
                    continue
                if es_hash_bcrypt(actual):
                    ya_bcrypt += 1
                elif es_hash_legado(actual):
                    legadas += 1  # se migrará en el login
                else:
                    u["password"] = hash_contrasena(actual)
                    hasheadas += 1
                    logger.info(f'Contraseña en texto plano hasheada para {u.get("email")}')

        guardarUsuarios(usuarios)
        logger.info(
            f"{hasheadas} hasheadas con bcrypt, {legadas} SHA-256 pendientes de migrar al login, "
            f"{ya_bcrypt} ya en bcrypt."
        )
    except Exception as e:
        logger.critical(f"No se pudieron encriptar las contraseñas existentes: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    actualizar_contrasenas()
