from modelo.CRUD import cargarUsuarios, guardarUsuarios
from auth.seguridad import encriptar_contrasena
import logging
import re

logger = logging.getLogger(__name__)

# Patrón de SHA-256 en hexadecimal (64 caracteres, solo 0-9 y a-f)
SHA256_HEX_PATTERN = re.compile(r'^[a-f0-9]{64}$', re.IGNORECASE)

def actualizar_contrasenas():
    usuarios = cargarUsuarios()
    total_actualizadas = 0
    total_saltadas = 0
    try:
        for categoria, lista_usuarios in usuarios.items():
            for u in lista_usuarios:
                password_actual = u.get("password", "")
                if not password_actual:
                    logger.warning(f'Usuario sin contraseña en {categoria}: {u.get("email","[sin email]")}')
                    continue

                # Verificar si ya parece un SHA256
                if SHA256_HEX_PATTERN.fullmatch(password_actual):
                    # Detectado hash, saltamos
                    logger.debug(f'Contraseña ya en SHA-256 para usuario {u.get("email")}, no se vuelve a hashear.')
                    total_saltadas += 1
                    continue

                # Encriptar la contraseña
                u["password"] = encriptar_contrasena(password_actual)
                total_actualizadas += 1
                logger.info(f'Contraseña actualizada a SHA-256 para usuario {u.get("email")}')
        
        guardarUsuarios(usuarios)
        logger.info(f'Se actualizaron {total_actualizadas} contraseñas. {total_saltadas} ya estaban en SHA-256 y se saltaron.')

    except Exception as e:
        logger.critical(f'NO PUDE ENCRIPTAR LAS CONTRASEÑAS EXISTENTES :( --->  {e}')

        


