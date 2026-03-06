import logging
from modelo.rolesModel import cargar_roles
from kivy.app import App

logger = logging.getLogger(__name__)


class ControladorVistas:

    def __init__(self, user=None, usuario_objetivo=None, notificationService=None):
        self.user = user
        self.usuario_objetivo = usuario_objetivo
        self.notificationService = notificationService

    def _sm(self):
        """Obtiene el ScreenManager activo"""
        return App.get_running_app().root

    # ----------------- NAVEGACIÓN -----------------

    def open_main(self):
        logger.debug("Cambiando a MainView")
        App.get_running_app().root.current = "MainView"

    def open_temas(self):
        logger.debug("Cambiando a Temas")
        App.get_running_app().root.current = "Temas"

    def open_register(self):
        self._sm().current = "Registro"
        logger.info("Registro cargado correctamente")

    def open_generica(self, rol_id):
        self._sm().current = "Generica"
        logger.info("GenericaView cargada correctamente")

    def open_campesino(self):
        self._sm().current = "Campesino"

    def open_restaurante(self):
        self._sm().current = "Restaurante"

    def open_delivery(self):
        self._sm().current = "Delivery"

    def open_admin(self):
        self._sm().current = "Admin"

    def openPerfil(self):
        self._sm().current = "Perfil"

    def open_pedidos_view(self):
        self._sm().current = "Pedidos"

    # ----------------- ROLES -----------------

    def abrir_vista_por_roles(self):

        roles_def = cargar_roles()
        roles_usuario = [r for r in roles_def if r["id"] in self.user.get("roles", [])]

        if not roles_usuario:
            logger.warning("No hay interfaz asociada a los roles del usuario.")
            return

        rol = roles_usuario[0]

        if rol["vista"] == "open_generica":
            self.open_generica(rol["id"])
        else:
            getattr(self, rol["vista"])()

    def reconstruir_main(self):

        from vistas.main_view import MainView
        from estilo.temaActual import TemaActual

        sm = self._sm()

        screen = sm.get_screen("MainView")

        screen.clear_widgets()

        estilo = TemaActual.obtener()

        new_view = MainView(estilo, self.notificationService)

        screen.add_widget(new_view)            