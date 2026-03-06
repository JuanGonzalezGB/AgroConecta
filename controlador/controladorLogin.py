from tkinter import messagebox
from auth.seguridad import encriptar_contrasena
from modelo.CRUD import buscarUsuario
from modelo.rolesModel import aplicar_roles_y_permisos
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

        # Encriptar la contraseña ingresada para comparar con la almacenada
        pwd_hash = encriptar_contrasena(pwd)

        ok, user = buscarUsuario(email, pwd_hash)  # modificar buscarUsuario para comparar hashes
        if not ok:
            messagebox.showerror("Error", "Correo o contraseña incorrectos.")
            return

        if not user.get("roles"):
            messagebox.showwarning("Sin rol", "Este usuario no tiene roles asignados.")
            return

        # Aplicar roles y permisos
        self.user = aplicar_roles_y_permisos(user)
        self.controlaVistas.user = self.user

        # Abrir la vista adecuada según roles
        self.controlaVistas.abrir_vista_por_roles()
