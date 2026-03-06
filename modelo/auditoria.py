import logging, os

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_PATH, exist_ok=True)
AUDIT_FILE = os.path.join(LOG_PATH, 'auditoria.log')

# Logger independiente
audit_logger = logging.getLogger("auditoria")
if not audit_logger.handlers:  # evita duplicar handlers si se importa varias veces
    handler = logging.FileHandler(AUDIT_FILE, mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    audit_logger.addHandler(handler)
    audit_logger.setLevel(logging.INFO)

def log_auditoria(usuario, accion, recurso, resultado, extra=None):
    """
    Registra eventos de auditoría.
    usuario: email del usuario actor
    accion: acción ejecutada (ej: crear_rol, eliminar_usuario, etc.)
    recurso: recurso afectado (ej: id_rol, email_usuario)
    resultado: SUCCESS o FAILED
    extra: texto adicional opcional
    """
    msg = f"user={usuario} action={accion} resource={recurso} result={resultado}"
    if extra:
        msg += f" extra={extra}"
    audit_logger.info(msg)