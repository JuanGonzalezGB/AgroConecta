from tkinter import messagebox
from servicios import autenticacion
from servicios.autorizacion import permisos_de
from servicios.errores import ServicioError
from controlador.controladorVistas import ControladorVistas
import logging

logger = logging.getLogger(__name__)

class ControladorLogin:
    def __init__(self, frame, root, user, estilo, notificationService):
        self.frame = frame
        self.root = root
        self.user = user
        self.estilo = estilo
        self.notificationService = notificationService
        self.controlaVistas = ControladorVistas(
            self.frame, self.root, self.user, None, self.estilo, self.notificationService
        )

    def logout(self):
        logger.debug('Cerrando sesión...')
        self.user = None
        logger.info('Sesión cerrada correctamente')
        self.controlaVistas.open_main()

    def login(self, credenciales):
        email, pwd = credenciales
        logger.debug(f'Intentando iniciar sesión: {email}...')

        if not email or not pwd:
            logger.warning('Datos faltantes')
            messagebox.showerror('Error', 'Ingrese email y contraseña.')
            return

        try:
            user = autenticacion.login(email, pwd)  # verifica bcrypt/SHA-256 legado y migra el hash
        except ServicioError as e:
            messagebox.showerror("Error", e.mensaje)
            return

        # Permisos calculados desde los roles actuales
        user["permisos"] = sorted(permisos_de(user))
        self.user = user
        self.controlaVistas.user = self.user

        # Abrir la vista adecuada según roles
        self.controlaVistas.abrir_vista_por_roles()
