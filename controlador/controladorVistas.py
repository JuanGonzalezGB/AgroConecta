import logging
from modelo.rolesModel import cargar_roles

logger = logging.getLogger(__name__)

class ControladorVistas:
    def __init__(self, frame, root, user, usuario_objetivo, estilo, notificationService):
        self.frame = frame  # Este debe ser siempre un layout de Kivy
        self.root = root
        self.user = user
        self.usuario_objetivo = usuario_objetivo
        self.estilo = estilo
        self.notificationService = notificationService
        self.vista_actual = None  # Para llevar referencia de la vista activa

    def abrir_vista_por_roles(self):
        """
        Abre la vista principal según los roles del usuario.
        Si hay varios roles, pregunta cuál desea abrir.
        """
        roles_def = cargar_roles()
        roles_usuario = [r for r in roles_def if r["id"] in self.user.get("roles", [])]

        if not roles_usuario:
            logger.warning("No hay interfaz asociada a los roles del usuario.")
            return

        if len(roles_usuario) == 1:
            rol = roles_usuario[0]
            if rol["vista"] == "open_generica":
                self.open_generica(rol["id"])
            else:
                getattr(self, rol["vista"])()
            return

        # Si hay varios roles, abrir la primera por defecto
        rol_seleccionado = roles_usuario[0]
        if rol_seleccionado["vista"] == "open_generica":
            self.open_generica(rol_seleccionado["id"])
        else:
            getattr(self, rol_seleccionado["vista"])()

    def cambiar_vista(self, nueva_vista):
        """
        Reemplaza la vista actual dentro del layout de Kivy.
        """
        if self.frame:
            logger.debug('Reemplazando contenido del frame...')
            # Eliminar todos los widgets hijos
            for child in list(self.frame.children):
                self.frame.remove_widget(child)
            # Agregar la nueva vista
            self.frame.add_widget(nueva_vista)
            self.vista_actual = nueva_vista
            logger.debug('Vista reemplazada correctamente')
        else:
            logger.warning('No hay frame disponible para cambiar la vista')

    # ----------------- VISTAS PRINCIPALES -----------------
    def open_main(self):
        from vistas.main_view import MainView
        vista = MainView(self.estilo, self.notificationService)
        self.cambiar_vista(vista)
        logger.info('MainView cargado correctamente')

    def open_temas(self):
        from vistas.selecTema import SelecTema
        if not self.frame:
            logger.warning('No hay layout disponible para abrir temas')
            return
        try:
            vista = SelecTema(self.frame, self.estilo)
            self.cambiar_vista(vista)
            logger.info('SelecTema cargado correctamente')
        except Exception as e:
            logger.exception(f'Error abriendo SelecTema: {e}')

    def open_generica(self, rol_id):
        from vistas.generica_view import GenericaView
        from controlador.controladorAdmin import ControladorAdmin

        roles_def = cargar_roles()
        rol = next((r for r in roles_def if r["id"] == rol_id), None)
        if not rol:
            return

        permisos_dict = {cat: [p["id"] for p in lista] for cat, lista in rol["permisos"].items()}
        self.controlAdmin = ControladorAdmin(self.user, self.root, self.notificationService)
        permisos_protegidos = self.controlAdmin.obtener_ids_permisos_de_rol_desde_inicial(rol_id)

        vista = GenericaView(self.root, self.user, self.estilo, self.notificationService,
                             rol_id, permisos_dict, permisos_protegidos)
        self.cambiar_vista(vista)
        self.mostrarNotificaciones(vista)
        logger.info(f'GenericaView cargada correctamente')

    def open_campesino(self):
        from vistas.campesino_view import CampesinoView
        vista = CampesinoView(self.root, self.user, self.estilo, self.notificationService)
        self.cambiar_vista(vista)
        self.mostrarNotificaciones(vista)
        logger.info('CampesinoView cargado correctamente')

    def open_restaurante(self):
        from vistas.restaurante_view import RestauranteView
        vista = RestauranteView(self.root, self.user, self.estilo, self.notificationService)
        self.cambiar_vista(vista)
        self.mostrarNotificaciones(vista)
        logger.info('RestauranteView cargado correctamente')

    def open_delivery(self):
        from vistas.delivery_view import DeliveryView
        vista = DeliveryView(self.root, self.user, self.estilo, self.notificationService)
        self.cambiar_vista(vista)
        self.mostrarNotificaciones(vista)
        logger.info('DeliveryView cargado correctamente')

    def open_admin(self):
        from vistas.admin_view import AdminView
        vista = AdminView(self.root, self.user, self.usuario_objetivo, self.estilo, self.notificationService)
        self.cambiar_vista(vista)
        self.mostrarNotificaciones(vista)
        logger.info('AdminView cargado correctamente')

    def open_register(self):
        from vistas.registro import Registro
        vista = Registro(self.root, self.estilo)
        self.cambiar_vista(vista)
        logger.info('Registro cargado correctamente')

    def openPerfil(self):
        vista = perfilView.PerfilView(self.root, self.user, self.estilo, self.notificationService)
        self.cambiar_vista(vista)
        logger.info('PerfilView cargado correctamente')

    def mostrarNotificaciones(self, vista):
        from controlador.controladorInternas import ControladorInternas
        if not self.frame:
            logger.warning('No hay layout disponible para mostrar notificaciones')
            return
        controlador = ControladorInternas(self.frame, self.root, self.user, self.estilo, vista, self.notificationService)
        controlador.open_internas()

    def open_pedidos_view(self):
        from vistas.subventanas.restauranteSubventanas.mis_pedidos_restaurante_view import MisPedidosRestauranteView
        vista = MisPedidosRestauranteView(self.root, self.user, self.estilo)
        self.cambiar_vista(vista)
        logger.info('MisPedidosRestauranteView cargado correctamente')